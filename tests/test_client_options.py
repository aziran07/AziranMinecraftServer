"""The distributed defaults must survive a second 26.3 client launch."""

from pathlib import Path
import json
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.1.10"
FAMILIARS = {
    "greedy_familiar", "drikwing", "wingnis", "bat_familiar",
    "deer_familiar", "cthulhu_familiar", "devil_familiar",
    "dragon_familiar", "blacksmith_familiar", "guardian_familiar",
    "headless_familiar", "chimera_familiar", "goat_familiar",
    "shub_niggurath_familiar", "beholder_familiar", "fairy_familiar",
    "mummy_familiar", "beaver_familiar",
}


class ClientOptionsTests(unittest.TestCase):
    def test_each_distribution_seeds_valid_unbound_familiar_keys(self):
        archives = {
            f"aziran-26.3-client-{VERSION}.mrpack": "client-overrides/options.txt",
            f"aziran-26.3-client-{VERSION}-manual.zip": "options.txt",
            f"aziran-26.3-client-{VERSION}-multimc.zip": ".minecraft/options.txt",
        }
        expected_keys = {f"key_key.occultism.familiar.{name}" for name in FAMILIARS}

        for archive_name, options_path in archives.items():
            with self.subTest(archive=archive_name):
                with zipfile.ZipFile(ROOT / "dist" / archive_name) as archive:
                    lines = archive.read(options_path).decode("utf-8").splitlines()

                self.assertIn("version:5023", lines)
                self.assertEqual(len(lines), len(set(lines)))
                settings = dict(line.split(":", 1) for line in lines)
                # Traveler's default B conflicts with JourneyMap's waypoint key.
                backpack_key = "key_key.travelersbackpack.inventory"
                self.assertEqual(set(settings) - {"version", "lang", "resourcePacks", backpack_key}, expected_keys)
                self.assertEqual(settings[backpack_key], "key.keyboard.y")
                self.assertEqual(settings['lang'], 'ko_kr')
                self.assertEqual(json.loads(settings['resourcePacks']),
                                 ['vanilla', 'mod_resources', 'file/occultism-ko-1.256.0-mc26.3.zip'])
                self.assertTrue(all(settings[key] == "key.keyboard.unknown" for key in expected_keys))
                self.assertNotIn("key.keyboard.-1", "\n".join(lines))


if __name__ == "__main__":
    unittest.main()
