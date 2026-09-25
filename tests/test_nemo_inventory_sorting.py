"""Nemo installs from its publisher and leaves Mouse Tweaks in charge of gestures."""

import hashlib
import json
from pathlib import Path
import tomllib
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
FILENAME = 'nemos-inventory-sorting-NeoForge-26.3-1.22.1.jar'
URL = f'https://cdn.modrinth.com/data/JHgf35QL/versions/aeA0nhgf/{FILENAME}'
SHA512 = '5463c182d069eff9e320f68cd2d272829adbca6a338f4221c0e7dd9497c6e465118e66513a2a1720f5e3d1fab41451d0a173aef398044704568fa083d572f0eb'
CONFIG = 'config/nemos-inventory-sorting/general.json'


class NemoInventorySortingTests(unittest.TestCase):
    def test_official_client_mod_and_dependencies(self):
        lock = json.loads((ROOT / 'mods-26.3-client-extra.lock.json').read_text())
        mods = [m for m in lock['mods'] if m['filename'] == FILENAME]
        self.assertEqual(len(mods), 1)
        mod = mods[0]
        self.assertEqual(mod['version_id'], 'aeA0nhgf')
        self.assertEqual(mod['url'], URL)
        self.assertEqual(mod['sha512'], SHA512)
        self.assertFalse(mod['bundle_jar'])
        self.assertEqual(mod['declared_mod_ids'], ['nemos_inventory_sorting'])
        jar_path = ROOT / 'client-mods-cache' / FILENAME
        self.assertEqual(hashlib.sha512(jar_path.read_bytes()).hexdigest(), SHA512)
        with zipfile.ZipFile(jar_path) as jar:
            metadata = tomllib.loads(jar.read('META-INF/neoforge.mods.toml').decode())
        required = {d['modId']: d['versionRange']
                    for d in metadata['dependencies']['nemos_inventory_sorting']
                    if d.get('type', 'required') == 'required'}
        self.assertEqual(required, {'minecraft': '[26.3,)', 'neoforge': '[26.3.0.1-beta,)'})
        server = json.loads((ROOT / 'mods-26.3.lock.json').read_text())
        self.assertFalse(any(m['filename'] == FILENAME for m in server['mods']))
        self.assertFalse((ROOT / 'server-data-26.3-neoforge/mods' / FILENAME).exists())

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
