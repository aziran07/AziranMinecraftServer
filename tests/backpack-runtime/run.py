#!/usr/bin/env python3
"""Compile and run actual backpack APIs in an isolated world; no live mutations."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "server-data-26.3-neoforge"
IMAGE = "eclipse-temurin:25-jdk"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--patch", type=Path, help="Compatibility jar; omit to reproduce the original bug")
    parser.add_argument("--full-modset", action="store_true", help="Load all installed server mods")
    args = parser.parse_args()
    if args.patch and not args.patch.is_file():
        parser.error("Patch jar does not exist")
    work = Path(tempfile.mkdtemp(prefix="aziran-backpack-test-"))
    print(f"Test artifacts: {work}", flush=True)
    identity = f"{os.getuid()}:{os.getgid()}"
    classpath = ":".join(
        ["/libraries/" + str(path.relative_to(DATA / "libraries"))
         for path in sorted((DATA / "libraries").rglob("*.jar"))
         if "installertools" not in path.parts and "net/minecraft/server/" not in path.as_posix()]
        + ["/mods/" + path.name for path in (DATA / "mods").glob("*.jar")]
    )
    source = Path(__file__).parent / "src/main"
    subprocess.run([
        "docker", "run", "--rm", "--network", "none", "--user", identity,
        "-v", f"{DATA}/libraries:/libraries:ro", "-v", f"{DATA}/mods:/mods:ro",
        "-v", f"{source}:/src:ro", "-v", f"{work}:/out", IMAGE,
        "javac", "--release", "25", "-proc:none", "-cp", classpath,
        "-d", "/out/classes", "/src/java/uk/aziran/backpacktests/BackpackPersistenceTests.java",
    ], check=True)
    server = work / "server"
    mods = server / "mods"
    mods.mkdir(parents=True)
    with zipfile.ZipFile(mods / "aziran-backpack-tests.jar", "w", zipfile.ZIP_DEFLATED) as jar:
        for directory in [work / "classes", source / "resources"]:
            for path in directory.rglob("*"):
                if path.is_file():
                    jar.write(path, path.relative_to(directory))
    for path in (DATA / "mods").glob("*.jar"):
        # Select the patch only through --patch, including after it is deployed.
        if path.name.startswith("aziran-backpack-curios-"):
            continue
        if args.full_modset or path.name.startswith(("travelersbackpack-", "curios-")):
            shutil.copyfile(path, mods / path.name)
    if args.patch:
        shutil.copyfile(args.patch, mods / args.patch.name)
    (server / "eula.txt").write_text("eula=true\n")
    (server / "server.properties").write_text(
        "online-mode=false\nenable-rcon=false\nlevel-name=test-world\n"
        "level-type=minecraft:flat\ngenerate-structures=false\nview-distance=2\n"
        "simulation-distance=2\nmax-players=1\nmax-tick-time=60000\n"
    )
    config = server / "config"
    config.mkdir()
    (config / "travelersbackpack-server.toml").write_text(
        "[server.backpackSettings]\nbackSlotIntegration = true\n"
    )
    name = work.name
    command = [
        "docker", "run", "--rm", "--name", name, "--network", "none", "--user", identity,
        "--memory", "4g", "-v", f"{server}:/data", "-v", f"{DATA}/libraries:/data/libraries:ro",
        "-w", "/data", IMAGE, "java", "-Xms512M", "-Xmx3G",
    ]
    for phase in ("write", "read"):
        report = server / "backpack-tests-result.json"
        report.unlink(missing_ok=True)
        log_path = work / f"console-{phase}.log"
        phase_command = [
            *command, f"-Daziran.backpackTestPhase={phase}",
            "@libraries/net/neoforged/neoforge/26.3.0.8-beta/unix_args.txt", "nogui",
        ]
        with log_path.open("w") as log:
            try:
                result = subprocess.run(phase_command, stdout=log, stderr=subprocess.STDOUT, timeout=300)
            except subprocess.TimeoutExpired:
                subprocess.run(["docker", "stop", "-t", "30", name], check=True)
                raise
        print(f"Server exit: {result.returncode}; console: {log_path}", flush=True)
        if not report.is_file():
            raise RuntimeError(f"Server produced no test report; inspect {log_path}")
        outcomes = json.loads(report.read_text())
        shutil.copyfile(report, work / f"results-{phase}.json")
        for test_name, outcome in outcomes.items():
            print(f"{test_name}: {outcome}", flush=True)
        if result.returncode != 0 or not outcomes or any(value != "PASS" for value in outcomes.values()):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
