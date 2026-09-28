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
    parser.add_argument("--patch", type=Path, help="Additional compatibility jar for explicit testing; official-only verification omits it")
    parser.add_argument("--full-modset", action="store_true", help="Load all installed server mods")
    parser.add_argument("--curios", type=Path, help="Test this official Curios jar instead of the installed version")
    args = parser.parse_args()
    if args.patch and not args.patch.is_file():
        parser.error("Patch jar does not exist")
    if args.curios and not args.curios.is_file():
        parser.error("Curios jar does not exist")
    work = Path(tempfile.mkdtemp(prefix="aziran-backpack-test-"))
    print(f"Test artifacts: {work}", flush=True)
    identity = f"{os.getuid()}:{os.getgid()}"
    input_mods = work / "input-mods"
    input_mods.mkdir()
    for path in (DATA / "mods").glob("*.jar"):
        if path.name.startswith("aziran-backpack-curios-"):
            continue
        if args.curios and path.name.startswith("curios-"):
            continue
        if args.full_modset or path.name.startswith(("travelersbackpack-", "curios-")):
            shutil.copyfile(path, input_mods / path.name)
    if args.curios:
        shutil.copyfile(args.curios, input_mods / args.curios.name)
    if args.patch:
        shutil.copyfile(args.patch, input_mods / args.patch.name)
    classpath = ":".join(
        ["/libraries/" + str(path.relative_to(DATA / "libraries"))
         for path in sorted((DATA / "libraries").rglob("*.jar"))
         if "installertools" not in path.parts and "net/minecraft/server/" not in path.as_posix()]
        + ["/mods/" + path.name for path in input_mods.glob("*.jar")]
    )
    source = Path(__file__).parent / "src/main"
    subprocess.run([
        "docker", "run", "--rm", "--network", "none", "--user", identity,
        "-v", f"{DATA}/libraries:/libraries:ro", "-v", f"{input_mods}:/mods:ro",
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
    for path in input_mods.glob("*.jar"):
        shutil.copyfile(path, mods / path.name)
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
    failed = False
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
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
