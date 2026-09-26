"""Require the tested compatibility patch whenever Curios wearing is enabled.

This checks deployment configuration, not in-game persistence. The runtime
acceptance procedure is documented in docs/BACKPACK_PERSISTENCE.md.
"""

from pathlib import Path
import importlib.util
import json
import tomllib
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]


class BackpackPersistenceConfigTests(unittest.TestCase):
    def test_server_enables_curios_with_the_pinned_patch(self):
        path = ROOT / "server-data-26.3-neoforge/config/travelersbackpack-server.toml"
        with path.open("rb") as stream:
            config = tomllib.load(stream)
        self.assertIs(
            config["server"]["backpackSettings"]["backSlotIntegration"],
            True,
            "The validated compatibility patch should restore Curios Back-slot wearing.",
        )
        lock = json.loads((ROOT / "mods-26.3.lock.json").read_text())
        patches = [mod for mod in lock["mods"] if "aziran_backpack_curios" in mod["declared_mod_ids"]]
        self.assertEqual(len(patches), 1, "Curios wearing requires exactly one locked persistence patch")
        patch = patches[0]
        self.assertEqual(patch["environment"], "server_only")
        jar_path = ROOT / lock["mods_directory"] / patch["filename"]
        with zipfile.ZipFile(jar_path) as jar:
            metadata = tomllib.loads(jar.read("META-INF/neoforge.mods.toml").decode())
            pins = {dependency["modId"]: dependency["versionRange"]
                    for dependency in metadata["dependencies"]["aziran_backpack_curios"]}
            self.assertEqual(pins, {
                "minecraft": "[26.3]", "neoforge": "[26.3.0.8-beta]",
                "travelersbackpack": "[11.4.0]", "curios": "[17.0.0-beta+26.3]",
            })
            mixins = json.loads(jar.read("aziran_backpack_curios.mixins.json"))
            self.assertIs(mixins["required"], True)
            self.assertEqual(mixins["injectors"]["defaultRequire"], 1)
            self.assertFalse(any("backpacktests" in name for name in jar.namelist()),
                             "Production patch must not ship the automatic test server shutdown harness")
        client_lock = json.loads((ROOT / "mods-26.3-client.lock.json").read_text())
        self.assertNotIn(patch["filename"], {mod["filename"] for mod in client_lock["mods"]})

    def test_client_builder_accepts_server_patch_without_bundling_it(self):
        spec = importlib.util.spec_from_file_location("client_builder", ROOT / "scripts/build_client_pack.py")
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        server_lock, selected = builder.load_client_mods()
        patch = next(mod for mod in server_lock["mods"] if "aziran_backpack_curios" in mod["declared_mod_ids"])
        self.assertTrue(selected)
        self.assertNotIn(patch["filename"], {mod["filename"] for mod in selected})


if __name__ == "__main__":
    unittest.main()
