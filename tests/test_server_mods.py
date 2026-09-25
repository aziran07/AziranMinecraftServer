"""Check installed server mods against the lock without duplicating release pins."""

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ServerModTests(unittest.TestCase):
    def test_installed_mods_match_lock_and_exclude_client_only_mods(self):
        lock = json.loads((ROOT / 'mods-26.3.lock.json').read_text())
        mods = lock['mods']
        names = {mod['filename'] for mod in mods}
        self.assertTrue(mods)
        self.assertEqual(lock['mod_count'], len(mods))
        self.assertEqual(len(names), len(mods))
        directory = ROOT / lock['mods_directory']
        self.assertEqual({path.name for path in directory.glob('*.jar')}, names)
        extras = json.loads((ROOT / 'mods-26.3-client-extra.lock.json').read_text())
        self.assertFalse(names & {mod['filename'] for mod in extras['mods']})
        for mod in mods:
            with self.subTest(mod=mod['filename']):
                self.assertIn(lock['minecraft_version'], mod['game_versions'])
                self.assertIn(lock['loader'], mod['loaders'])
                data = (directory / mod['filename']).read_bytes()
                self.assertEqual(hashlib.sha512(data).hexdigest(), mod['sha512'])


if __name__ == '__main__':
    unittest.main()
