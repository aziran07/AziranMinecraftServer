"""Traveler's Backpack must ship unchanged to both server and clients."""

import hashlib
import json
from pathlib import Path
import tomllib
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
FILENAME = "travelersbackpack-neoforge-26.3-11.4.0.jar"
SHA512 = "0ec5ad7a9f87cb5a303a374a9a9f2655be80513fa65570f8e267b12a03bacbb41e1afe4dcc15682574be67cacef26ff674d09836dc6244a1d434fb4155f0fce1"
URL = f"https://cdn.modrinth.com/data/rlloIFEV/versions/Gdy0zkAN/{FILENAME}"


class TravelersBackpackDeploymentTests(unittest.TestCase):
    def test_server_has_official_26_3_build_and_satisfied_dependencies(self):
        lock = json.loads((ROOT / "mods-26.3.lock.json").read_text())
        mods = [m for m in lock["mods"] if "travelersbackpack" in m.get("declared_mod_ids", [])]
        self.assertEqual(len(mods), 1)
        mod = mods[0]
        self.assertEqual(mod["version_id"], "Gdy0zkAN")
        self.assertEqual(mod["filename"], FILENAME)
        self.assertEqual(mod["sha512"], SHA512)
        self.assertEqual(mod["url"], URL)
        directory = ROOT / lock["mods_directory"]
        self.assertEqual(sorted(p.name for p in directory.glob("travelersbackpack*.jar")), [FILENAME])
        data = (directory / FILENAME).read_bytes()
        self.assertEqual(len(data), 1475945)
        self.assertEqual(hashlib.sha512(data).hexdigest(), SHA512)
        with zipfile.ZipFile(directory / FILENAME) as jar:
            metadata = tomllib.loads(jar.read("META-INF/neoforge.mods.toml").decode())
            self.assertIn("assets/travelersbackpack/lang/ko_kr.json", jar.namelist())
        declared = next(m for m in metadata["mods"] if m["modId"] == "travelersbackpack")
        self.assertEqual(declared["version"], "11.4.0")
        required = {d["modId"]: d["versionRange"] for d in metadata["dependencies"]["travelersbackpack"]
                    if d.get("type", "required") == "required"}
        self.assertEqual(required, {"minecraft": "[26.3]", "neoforge": "[26.3.0.1-beta,)"})
        self.assertEqual(lock["minecraft_version"], "26.3")
        self.assertEqual(lock["loader_version"], "26.3.0.8-beta")

    def test_every_client_format_installs_the_same_backpack_mod(self):
        lock = json.loads((ROOT / "mods-26.3-client.lock.json").read_text())
        self.assertEqual(lock["pack_version"], "1.1.9")
        mods = [m for m in lock["mods"] if m["filename"] == FILENAME]
        self.assertEqual(len(mods), 1)
        self.assertEqual(mods[0]["origin"], "server-lock")
        self.assertEqual(mods[0]["sha512"], SHA512)
        for suffix, prefix in (("-manual.zip", ""), ("-multimc.zip", ".minecraft/")):
            with self.subTest(format=suffix):
                with zipfile.ZipFile(ROOT / f"dist/aziran-26.3-client-1.1.9{suffix}") as archive:
                    entries = [n for n in archive.namelist() if n.startswith(prefix + "mods/travelersbackpack")]
                    self.assertEqual(entries, [prefix + "mods/" + FILENAME])
                    self.assertEqual(hashlib.sha512(archive.read(entries[0])).hexdigest(), SHA512)
        with zipfile.ZipFile(ROOT / "dist/aziran-26.3-client-1.1.9.mrpack") as archive:
            index = json.loads(archive.read("modrinth.index.json"))
            entries = [e for e in index["files"] if e["path"].startswith("mods/travelersbackpack")]
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["path"], "mods/" + FILENAME)
            self.assertEqual(entries[0]["hashes"]["sha512"], SHA512)
            self.assertEqual(entries[0]["downloads"], [URL])
            self.assertEqual(entries[0]["env"]["client"], "required")


if __name__ == "__main__":
    unittest.main()
