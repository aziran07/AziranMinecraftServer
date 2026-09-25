"""The grave mod must be pinned, installed, and included for clients."""

import hashlib
import json
from pathlib import Path
import tomllib
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
FILENAME = "simpletomb-26.3-1.9.0.jar"
SHA512 = "83fa6e0a143e6e0538788cb301c36c5104df526878bc7cd6fc34f5044bb25e606b62cfdcf3ff1706fdefaf00602df99e724437fbceb482b054b04ba6d796c183"


class SimpleTombDeploymentTests(unittest.TestCase):
    def test_server_installs_pinned_neoforge_26_3_mod(self):
        lock = json.loads((ROOT / "mods-26.3.lock.json").read_text())
        mods = [mod for mod in lock["mods"] if "simpletomb" in mod.get("declared_mod_ids", [])]
        self.assertEqual(len(mods), 1)
        mod = mods[0]
        self.assertEqual(mod["filename"], FILENAME)
        self.assertEqual(mod["sha512"], SHA512)
        self.assertEqual(mod["source"], "curseforge")
        self.assertIn("26.3", mod["game_versions"])
        self.assertIn("neoforge", mod["loaders"])
        self.assertEqual(lock["mod_count"], len(lock["mods"]))

        jar_path = ROOT / lock["mods_directory"] / FILENAME
        self.assertEqual(hashlib.sha512(jar_path.read_bytes()).hexdigest(), SHA512)
        with zipfile.ZipFile(jar_path) as jar:
            metadata = tomllib.loads(jar.read("META-INF/neoforge.mods.toml").decode())
        self.assertIn("simpletomb", [entry["modId"] for entry in metadata["mods"]])

    def test_client_pack_contains_the_same_grave_mod(self):
        lock = json.loads((ROOT / "mods-26.3-client.lock.json").read_text())
        mods = [mod for mod in lock["mods"] if mod["filename"] == FILENAME]
        self.assertEqual(len(mods), 1)
        self.assertEqual(mods[0]["sha512"], SHA512)
        self.assertEqual(mods[0]["origin"], "server-lock")

        manual = ROOT / f"dist/aziran-26.3-client-{lock['pack_version']}-manual.zip"
        with zipfile.ZipFile(manual) as archive:
            self.assertEqual(hashlib.sha512(archive.read(f"mods/{FILENAME}")).hexdigest(), SHA512)


if __name__ == "__main__":
    unittest.main()
