"""Require official Curios persistence fix without the retired compatibility addon."""

from pathlib import Path
import importlib.util
import json
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BackpackPersistenceConfigTests(unittest.TestCase):
    def test_server_enables_curios_with_official_fix(self):
        with (ROOT / "server-data-26.3-neoforge/config/travelersbackpack-server.toml").open("rb") as stream:
            config = tomllib.load(stream)
        self.assertIs(config["server"]["backpackSettings"]["backSlotIntegration"], True)
        server = json.loads((ROOT / "mods-26.3.lock.json").read_text())
        client = json.loads((ROOT / "mods-26.3-client.lock.json").read_text())
        official = []
        for lock in (server, client):
            self.assertFalse(any("aziran_backpack_curios" in mod["declared_mod_ids"] for mod in lock["mods"]))
            curios = [mod for mod in lock["mods"] if "curios" in mod["declared_mod_ids"]]
            self.assertEqual(len(curios), 1)
            self.assertEqual(curios[0]["version_number"], "17.0.0-beta.2+26.3")
            official.append(curios[0])
        self.assertEqual(official[0]["sha512"], official[1]["sha512"])
        directory = ROOT / server["mods_directory"]
        self.assertFalse(list(directory.glob("aziran-backpack-curios-*.jar")))
        self.assertEqual([path.name for path in directory.glob("curios-*.jar")], [official[0]["filename"]])

    def test_client_builder_selects_official_curios_without_local_patch(self):
        spec = importlib.util.spec_from_file_location("client_builder", ROOT / "scripts/build_client_pack.py")
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        _, selected = builder.load_client_mods()
        self.assertTrue(selected)
        self.assertFalse(any("aziran_backpack_curios" in mod["declared_mod_ids"] for mod in selected))
        curios = next(mod for mod in selected if "curios" in mod["declared_mod_ids"])
        self.assertEqual(curios["version_number"], "17.0.0-beta.2+26.3")


if __name__ == "__main__":
    unittest.main()
