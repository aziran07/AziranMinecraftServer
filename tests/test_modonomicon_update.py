"""Deployment checks for the upstream Minecraft 26.3 book dragging fix."""

import hashlib
import json
from pathlib import Path
import tomllib
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
FILENAME = "modonomicon-26.3-neoforge-2.7.0.jar"
SHA512 = "7d16cb18892339b2ab226de271c06a32410983800bd50989f3e98f1b68d5c3f7a91017eb386a2c4995e893f78c642adb34a6dd0afc47e622705e0a209904d70e"
URL = f"https://cdn.modrinth.com/data/692GClaE/versions/SFKjMnCe/{FILENAME}"


class ModonomiconUpdateTests(unittest.TestCase):
    def test_server_installs_only_the_pinned_fix(self):
        lock = json.loads((ROOT / "mods-26.3.lock.json").read_text())
        mods = [m for m in lock["mods"] if "modonomicon" in m.get("declared_mod_ids", [])]
        self.assertEqual(len(mods), 1)
        mod = mods[0]
        self.assertEqual(mod["version_id"], "SFKjMnCe")
        self.assertEqual(mod["version_number"], "26.3-2.7.0")
        self.assertEqual(mod["filename"], FILENAME)
        self.assertEqual(mod["sha512"], SHA512)
        self.assertEqual(mod["url"], URL)
        directory = ROOT / lock["mods_directory"]
        self.assertEqual(sorted(p.name for p in directory.glob("modonomicon*.jar")), [FILENAME])
        data = (directory / FILENAME).read_bytes()
        self.assertEqual(hashlib.sha512(data).hexdigest(), SHA512)
        self.assertEqual(len(data), 2987945)
        with zipfile.ZipFile(directory / FILENAME) as jar:
            metadata = tomllib.loads(jar.read("META-INF/neoforge.mods.toml").decode())
        declared = next(m for m in metadata["mods"] if m["modId"] == "modonomicon")
        # The publisher prefixes the Modrinth version with Minecraft's version,
        # while the actual NeoForge mod metadata uses the mod version alone.
        self.assertEqual(declared["version"], "2.7.0")

    def test_all_client_formats_deliver_the_same_fix(self):
        lock = json.loads((ROOT / "mods-26.3-client.lock.json").read_text())
        self.assertEqual(lock["pack_version"], "1.1.10")
        mods = [m for m in lock["mods"] if "modonomicon" in m.get("declared_mod_ids", [])]
        self.assertEqual(len(mods), 1)
        self.assertEqual(mods[0]["filename"], FILENAME)
        self.assertEqual(mods[0]["sha512"], SHA512)
        for suffix, prefix in (("-manual.zip", ""), ("-multimc.zip", ".minecraft/")):
            with self.subTest(format=suffix):
                with zipfile.ZipFile(ROOT / f"dist/aziran-26.3-client-1.1.10{suffix}") as archive:
                    entries = [n for n in archive.namelist() if n.startswith(prefix + "mods/modonomicon")]
                    self.assertEqual(entries, [prefix + "mods/" + FILENAME])
                    self.assertEqual(hashlib.sha512(archive.read(entries[0])).hexdigest(), SHA512)
        with zipfile.ZipFile(ROOT / "dist/aziran-26.3-client-1.1.10.mrpack") as archive:
            index = json.loads(archive.read("modrinth.index.json"))
            entries = [e for e in index["files"] if e["path"].startswith("mods/modonomicon")]
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["path"], "mods/" + FILENAME)
            self.assertEqual(entries[0]["hashes"]["sha512"], SHA512)
            self.assertEqual(entries[0]["downloads"], [URL])


if __name__ == "__main__":
    unittest.main()
