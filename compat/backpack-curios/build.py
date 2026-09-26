#!/usr/bin/env python3
"""Build the Aziran Backpack Curios compatibility jar reproducibly.

Compiles with Java 25 javac in a network-less Docker container against the installed server libraries and the
original Traveler's Backpack and Curios jars, after checking that every input matches its pinned hash.
Writes dist/backpack-curios/<jar> and a .sha256 file next to it. Nothing under server-data is modified.
"""

import hashlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile


PROJECT = Path(__file__).resolve().parent
ROOT = PROJECT.parents[1]
DATA = ROOT / "server-data-26.3-neoforge"
LIBRARIES = DATA / "libraries"
OUTPUT = ROOT / "dist" / "backpack-curios"
JAR_NAME = "aziran-backpack-curios-1.0.0.jar"
# eclipse-temurin:25-jdk as pulled when this build was verified; pinned by digest so javac cannot change silently.
IMAGE = "eclipse-temurin@sha256:97014c4b396021f9ddb7d592a7dbedb0c4e4215c29e03dc01c393558aefb71c2"
# Fixed entry timestamp for deterministic jars (the earliest date zip supports; matches NeoForge's own jars).
ZIP_TIMESTAMP = (1980, 2, 1, 0, 0, 0)

NEOFORGE_JAR = "net/neoforged/neoforge/26.3.0.8-beta/neoforge-26.3.0.8-beta-universal.jar"
MIXINEXTRAS_ENTRY = "META-INF/jarjar/mixinextras-neoforge-0.5.4.jar"

# Exact inputs this patch was reviewed against. Any mismatch means the server changed and the patch needs review.
PINNED_FILES = {
    DATA / "mods/travelersbackpack-neoforge-26.3-11.4.0.jar": "2fa8ffb5ec657ac23e4a048bd08892311695e1c80b87b8341eb33706abdef7ee",
    DATA / "mods/curios-neoforge-17.0.0-beta+26.3.jar": "6483ff2d109a07a3d60cd768fd1bece697be89b1374e8eb239259557c4f6cb4c",
    LIBRARIES / NEOFORGE_JAR: "24a4ff980a958477da8a1fd887f95e13552b4621e55fc1d525a69bc2cc8976b7",
    LIBRARIES / "net/neoforged/minecraft-server-patched/26.3.0.8-beta/minecraft-server-patched-26.3.0.8-beta.jar":
        "d13e3df851ed7f093a3b8c5d4b0d2c49027a77c532ef8abd463fde0244d2c7ce",
    LIBRARIES / "net/fabricmc/sponge-mixin/0.17.3+mixin.0.8.7/sponge-mixin-0.17.3+mixin.0.8.7.jar":
        "9e90efec71d2bad5b96c9089f019d14a8603227d3c5f408d12f53fae89d99d41",
}
MIXINEXTRAS_SHA256 = "6a464b1c603b716033f3561a0632a7cc7be17c9d75af1cab7f1db5fe98c3888a"
# Digest over the sorted "relative path  sha256" lines of every library jar on the compile classpath.
LIBRARY_SET_SHA256 = "aa06527b10a2e6eddbc342d7abacb05526685d1f1fd6fe30c120fdd314bcb6ce"

MANIFEST = (
    "Manifest-Version: 1.0\r\n"
    "Automatic-Module-Name: uk.aziran.backpackcurios\r\n"
    "Implementation-Title: aziran_backpack_curios\r\n"
    "Implementation-Version: 1.0.0\r\n"
    "\r\n"
)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def require_hash(label, actual, expected):
    if actual != expected:
        raise SystemExit(f"Hash mismatch for {label}: expected {expected}, got {actual}. Review the patch before rebuilding.")


# installertools ships a fat jar that shadows Gson and is not a runtime library. The unpatched vanilla server jar
# would shadow the NeoForge-patched Minecraft classes because it sorts first on the classpath.
EXCLUDED_LIBRARIES = ["net/neoforged/installertools/", "net/minecraft/server/"]


def library_jars():
    return sorted(
        path for path in LIBRARIES.rglob("*.jar")
        if not any(path.relative_to(LIBRARIES).as_posix().startswith(prefix) for prefix in EXCLUDED_LIBRARIES)
    )


def library_set_digest(jars):
    lines = "".join(f"{jar.relative_to(LIBRARIES).as_posix()}  {sha256_file(jar)}\n" for jar in jars)
    return sha256_bytes(lines.encode())


def check_inputs(jars):
    for path, expected in PINNED_FILES.items():
        if not path.is_file():
            raise SystemExit(f"Missing pinned input: {path}")
        require_hash(path.relative_to(ROOT).as_posix(), sha256_file(path), expected)
    require_hash("library classpath set", library_set_digest(jars), LIBRARY_SET_SHA256)


def extract_mixinextras(work):
    with zipfile.ZipFile(LIBRARIES / NEOFORGE_JAR) as neoforge:
        data = neoforge.read(MIXINEXTRAS_ENTRY)
    require_hash(MIXINEXTRAS_ENTRY, sha256_bytes(data), MIXINEXTRAS_SHA256)
    target = work / "mixinextras.jar"
    target.write_bytes(data)
    return target


def compile_sources(work, jars):
    sources = sorted((PROJECT / "src/main/java").rglob("*.java"))
    classpath = ":".join(
        ["/libraries/" + jar.relative_to(LIBRARIES).as_posix() for jar in jars]
        + ["/mods/travelersbackpack-neoforge-26.3-11.4.0.jar", "/mods/curios-neoforge-17.0.0-beta+26.3.jar",
           "/work/mixinextras.jar"]
    )
    (work / "classes").mkdir()
    subprocess.run([
        "docker", "run", "--rm", "--network", "none", "--user", f"{os.getuid()}:{os.getgid()}",
        "-v", f"{LIBRARIES}:/libraries:ro", "-v", f"{DATA / 'mods'}:/mods:ro",
        "-v", f"{PROJECT / 'src/main/java'}:/src:ro", "-v", f"{work}:/work",
        IMAGE, "javac", "--release", "25", "-proc:none", "-encoding", "UTF-8", "-implicit:none",
        "-Xlint:all,-classfile", "-Werror", "-cp", classpath, "-d", "/work/classes",
        *["/src/" + source.relative_to(PROJECT / "src/main/java").as_posix() for source in sources],
    ], check=True)
    return work / "classes"


def write_jar(classes, target):
    entries = {"META-INF/MANIFEST.MF": MANIFEST.encode()}
    for directory in [classes, PROJECT / "src/main/resources"]:
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                name = path.relative_to(directory).as_posix()
                if name in entries:
                    raise SystemExit(f"Duplicate jar entry: {name}")
                entries[name] = path.read_bytes()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as jar:
        # Manifest first, then everything else in sorted order.
        for name in ["META-INF/MANIFEST.MF"] + sorted(name for name in entries if name != "META-INF/MANIFEST.MF"):
            info = zipfile.ZipInfo(name, ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            jar.writestr(info, entries[name])
    target.write_bytes(buffer.getvalue())


def main():
    jars = library_jars()
    if "--print-library-digest" in sys.argv:
        print(library_set_digest(jars))
        return 0
    check_inputs(jars)
    with tempfile.TemporaryDirectory(prefix="aziran-backpack-curios-build-") as temp:
        work = Path(temp)
        extract_mixinextras(work)
        classes = compile_sources(work, jars)
        OUTPUT.mkdir(parents=True, exist_ok=True)
        target = OUTPUT / JAR_NAME
        write_jar(classes, target)
        shutil.rmtree(classes)
    digest = sha256_file(target)
    (OUTPUT / (JAR_NAME + ".sha256")).write_text(f"{digest}  {JAR_NAME}\n")
    print(f"{target}\nsha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
