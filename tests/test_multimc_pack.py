"""Validate the portable MultiMC export against the existing client lock."""
import configparser
import hashlib
import json
from pathlib import Path
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class MultiMCPackTests(unittest.TestCase):
    def test_instance_and_mods(self):
        lock = json.loads((ROOT / 'mods-26.3-client.lock.json').read_text())
        path = ROOT / 'dist/aziran-26.3-client-1.1.3-multimc.zip'
        self.assertEqual(list((ROOT / 'dist').glob('aziran-26.3-client-*-multimc.zip')), [path])
        with zipfile.ZipFile(path) as z:
            self.assertIsNone(z.testzip())
            names = z.namelist()
            self.assertEqual(len(names), len(set(names)))
            self.assertTrue(all(not n.startswith('/') and '..' not in Path(n).parts for n in names))
            pack = json.loads(z.read('mmc-pack.json'))
            self.assertEqual(pack['formatVersion'], 1)
            components = {c['uid']: c['version'] for c in pack['components']}
            self.assertEqual(components['net.minecraft'], '26.3')
            self.assertEqual(components['net.neoforged'], '26.3.0.8-beta')
            self.assertEqual(len(pack['components']), len(components))
            self.assertNotIn('net.minecraftforge', components)
            cfg = configparser.ConfigParser()
            cfg.read_string('[instance]\n' + z.read('instance.cfg').decode())
            self.assertEqual(cfg['instance']['InstanceType'], 'OneSix')
            self.assertEqual(cfg['instance']['name'], 'Aziran 26.3 Client 1.1.3')
            for key in ('JavaPath', 'PreLaunchCommand', 'PostExitCommand', 'WrapperCommand'):
                self.assertFalse(cfg['instance'].get(key, ''))
            jars = {n for n in names if n.endswith('.jar')}
            journey_name = 'journeymap-neoforge-26.3-6.0.9.jar'
            self.assertEqual(jars, {'.minecraft/mods/' + m['filename'] for m in lock['mods'] if m['filename'] != journey_name})
            self.assertEqual(len(jars), 15)
            self.assertFalse(any('sodium' in name.lower() for name in jars))
            self.assertFalse(any('xaerominimap' in name.lower() for name in jars))
            instructions = z.read('README.md').decode()
            self.assertIn('JourneyMap', instructions)
            journey = next(m for m in lock['mods'] if m['filename'] == journey_name)
            self.assertIn(journey['url'], instructions)
            manifest = json.loads(z.read('manifest.json'))
            base = manifest.get('install_root', '.')
            manifest_paths = {str(Path(base) / f['path']) for f in manifest['files']}
            self.assertEqual(manifest_paths, jars)
            for mod in lock['mods']:
                if mod['filename'] == journey_name:
                    continue
                data = z.read('.minecraft/mods/' + mod['filename'])
                self.assertEqual(len(data), mod['size'])
                self.assertEqual(hashlib.sha512(data).hexdigest(), mod['sha512'])
            self.assertIn('README.md', names)
            self.assertIn('LICENSES.md', names)
            self.assertTrue(all(n in jars or n in {'mmc-pack.json', 'instance.cfg', 'README.md', 'LICENSES.md', 'manifest.json'} for n in names))


if __name__ == '__main__':
    unittest.main()
