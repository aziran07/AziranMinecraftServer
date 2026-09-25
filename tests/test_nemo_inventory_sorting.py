"""Nemo installs from its publisher and leaves Mouse Tweaks in charge of gestures."""

import json
from pathlib import Path
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
FILENAME = 'nemos-inventory-sorting-NeoForge-26.3-1.22.1.jar'
URL = f'https://cdn.modrinth.com/data/JHgf35QL/versions/aeA0nhgf/{FILENAME}'
SHA512 = '5463c182d069eff9e320f68cd2d272829adbca6a338f4221c0e7dd9497c6e465118e66513a2a1720f5e3d1fab41451d0a173aef398044704568fa083d572f0eb'
CONFIG = 'config/nemos-inventory-sorting/general.json'


class NemoInventorySortingTests(unittest.TestCase):
    def test_all_formats_configure_gestures_and_respect_distribution(self):
        for suffix, prefix in (('.mrpack', 'client-overrides/'),
                               ('-manual.zip', ''), ('-multimc.zip', '.minecraft/')):
            with self.subTest(format=suffix):
                with zipfile.ZipFile(ROOT / f'dist/aziran-26.3-client-1.1.10{suffix}') as archive:
                    self.assertFalse(any(Path(n).name == FILENAME for n in archive.namelist()))
                    settings = json.loads(archive.read(prefix + CONFIG))
                    for key in ('enableDragQuickMove', 'enableSplitQuickMove', 'enableScrollTransfer'):
                        self.assertIs(settings[key], False)
                    self.assertIs(settings['includeHotbarByDefault'], False)
                    self.assertIs(settings['enableSlotLocking'], True)
                    self.assertIs(settings['enableKeyMappings'], True)
                    self.assertIs(settings['enableHoverKeyMappings'], True)
                    self.assertIs(settings['enableContainerKeyMappings'], True)
                    if suffix == '.mrpack':
                        index = json.loads(archive.read('modrinth.index.json'))
                        entries = [e for e in index['files'] if e['path'] == 'mods/' + FILENAME]
                        self.assertEqual(len(entries), 1)
                        self.assertEqual(entries[0]['downloads'], [URL])
                        self.assertEqual(entries[0]['hashes']['sha512'], SHA512)
                        self.assertEqual(entries[0]['env'], {'client': 'required', 'server': 'unsupported'})
                    else:
                        instructions = archive.read('README.md').decode()
                        self.assertIn("Nemo's Inventory Sorting", instructions)
                        self.assertIn(URL, instructions)


if __name__ == '__main__':
    unittest.main()
