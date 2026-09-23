"""Acceptance checks for the generated 26.3 client pack (build first)."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tomllib
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    'balm', 'cookingforblockheads', 'curios', 'farmersdelight', 'geckolib',
    'jade', 'jei', 'modonomicon', 'occultism', 'packetfixer', 'toms_storage',
    'lithium', 'mousetweaks', 'clumps', 'immediatelyfast', 'journeymap',
    'sodium', 'iris',
}


class ClientPackTests(unittest.TestCase):
    def test_corrupt_client_download_is_rejected(self):
        spec = importlib.util.spec_from_file_location('client_builder', ROOT / 'scripts/build_client_pack.py')
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        lock = json.loads((ROOT / 'mods-26.3-client-extra.lock.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            builder.CLIENT_CACHE = Path(directory)
            for mod in lock['mods']:
                (builder.CLIENT_CACHE / mod['filename']).write_bytes(b'corrupt download')
            with self.assertRaisesRegex(SystemExit, '일치하지 않는다'):
                builder.load_client_extras()

    def test_artifacts_match_requested_mods_and_dependencies(self):
        lock = json.loads((ROOT / 'mods-26.3-client.lock.json').read_text())
        self.assertEqual(lock['pack_version'], '1.1.4')
        self.assertEqual(lock['mod_count'], 18)
        self.assertEqual(lock['shared_with_server_count'], 13)
        self.assertEqual(lock['client_only_count'], 5)
        self.assertEqual(lock['minecraft_version'], '26.3')
        self.assertEqual(lock['loader_version'], '26.3.0.8-beta')
        mods = {m['filename']: m for m in lock['mods']}
        server = json.loads((ROOT / 'mods-26.3.lock.json').read_text())
        trusted = {m['filename']: m['sha512'] for m in server['mods']}
        # Independently obtained from the publishers' pinned Modrinth versions.
        trusted.update({
            'MouseTweaks-neoforge-mc26.3-2.31.jar': '93e7ac34bbc15de635073722054b11fed3981e0f39954286e8a57214ce5ce007e5562882cb81cd230c8ea49970970c84548cfc598332c539777986090b090798',
            'ImmediatelyFast-NeoForge-1.17.1+26.3.jar': '6fddcf7e9de2bf179bdd18cc317fa1cc50ea9c3a40b06a0e0673ecb1dba29fb2ac2743ada361e32f52c2c1f333043795a5149b8b89ee467665c2b734e7d5d951',
            'journeymap-neoforge-26.3-6.0.9.jar': '1ed0fc68d17e5134d55111aeea256cac523097eb2c899c11b4ead7f611058983ff54277a0dbcfe5a422a0bd77c05591a677be3bf13b7c927d0f4cfdfbe4d440b',
            'sodium-neoforge-0.9.2+mc26.3.jar': 'f5b62730bbee7d116a83c765b8e7cdb660da97ab7f122f180293eda3e56b5ca4d701b0bf18c36f087e9a7349f8ec113f1f8c0d462a8893c551a2f3e163bd0cb8',
            'iris-neoforge-1.11.6-snapshot+mc26.3-local.jar': '995f160829bc183e7b4acfe6ca149706b6f1a8e7a991d271312d1a92c8ac4cd26553f5be3772ce3e3247709a72f2ef2a050472a0d81d7891e792308d3211a803',
        })
        for name, mod in mods.items():
            self.assertEqual(mod['sha512'], trusted[name])
        manual = ROOT / 'dist/aziran-26.3-client-1.1.4-manual.zip'
        journey_name = 'journeymap-neoforge-26.3-6.0.9.jar'
        provided = {'minecraft', 'neoforge'}
        required = set()
        top_ids = set()

        def inspect(data, top=False):
            with zipfile.ZipFile(io.BytesIO(data)) as jar:
                if 'META-INF/neoforge.mods.toml' in jar.namelist():
                    meta = tomllib.loads(jar.read('META-INF/neoforge.mods.toml').decode())
                    ids = {m['modId'] for m in meta.get('mods', [])}
                    provided.update(ids)
                    if top:
                        top_ids.update(ids)
                    for deps in meta.get('dependencies', {}).values():
                        required.update(d['modId'] for d in deps if d.get('type', 'required') == 'required')
                elif top:
                    self.fail('Top-level client mod lacks NeoForge metadata')
                for name in jar.namelist():
                    if name.startswith('META-INF/jarjar/') and name.endswith('.jar'):
                        inspect(jar.read(name))

        with zipfile.ZipFile(manual) as archive:
            self.assertIsNone(archive.testzip())
            names = archive.namelist()
            self.assertEqual(len(names), len(set(names)))
            self.assertTrue(all(not n.startswith('/') and '..' not in Path(n).parts for n in names))
            jars = [n for n in names if n.startswith('mods/') and n.endswith('.jar')]
            self.assertEqual({Path(n).name for n in jars}, set(mods) - {journey_name})
            self.assertEqual(len(jars), 17)
            instructions = archive.read('README.md').decode()
            self.assertIn('JourneyMap', instructions)
            self.assertIn(mods[journey_name]['url'], instructions)
            self.assertTrue(all(n.startswith('mods/') for n in jars))
            self.assertIn('sources/iris/Iris-10d3598cd96b0566497b66efe66256f468cd977e-source.tar.gz', names)
            self.assertIn('sources/iris/glsl-transformer-3.0.0-pre3-sources.jar', names)
            for name in jars:
                data = archive.read(name)
                mod = mods[Path(name).name]
                self.assertEqual(len(data), mod['size'])
                for algorithm in ('sha1', 'sha512'):
                    self.assertEqual(hashlib.new(algorithm, data).hexdigest(), mod[algorithm])
                inspect(data, top=True)
        journey_data = (ROOT / 'client-mods-cache' / journey_name).read_bytes()
        self.assertEqual(hashlib.sha512(journey_data).hexdigest(), mods[journey_name]['sha512'])
        inspect(journey_data, top=True)
        self.assertEqual(top_ids, EXPECTED)
        self.assertFalse(required - provided, f'Missing dependencies: {required - provided}')
        self.assertIn('sodium-neoforge-0.9.2+mc26.3.jar', mods)
        self.assertIn('iris-neoforge-1.11.6-snapshot+mc26.3-local.jar', mods)
        self.assertIn('MouseTweaks-neoforge-mc26.3-2.31.jar', mods)
        self.assertIn('ImmediatelyFast-NeoForge-1.17.1+26.3.jar', mods)
        self.assertIn(journey_name, mods)
        self.assertFalse(any('xaerominimap' in name for name in mods))

        with zipfile.ZipFile(ROOT / 'dist/aziran-26.3-client-1.1.4.mrpack') as archive:
            self.assertIsNone(archive.testzip())
            index = json.loads(archive.read('modrinth.index.json'))
            self.assertEqual(index['dependencies'], {'minecraft': '26.3', 'neoforge': '26.3.0.8-beta'})
            self.assertEqual(index['formatVersion'], 1)
            self.assertEqual(index['game'], 'minecraft')
            paths = [f['path'] for f in index['files']]
            self.assertEqual(len(paths), len(set(paths)))
            shader_path = 'shaderpacks/ComplementaryReimagined_r5.9.3.zip'
            self.assertIn(shader_path, paths)
            shader = next(entry for entry in index['files'] if entry['path'] == shader_path)
            self.assertEqual(shader['hashes']['sha1'], '838139b54cddb56b2e83cd260d8efd960ac536d6')
            self.assertTrue(all(u.startswith('https://cdn.modrinth.com/') for u in shader['downloads']))
            got = {Path(p).name for p in paths if p != shader_path}
            for entry in index['files']:
                if entry['path'] == shader_path:
                    continue
                mod = mods[Path(entry['path']).name]
                self.assertEqual(entry['fileSize'], mod['size'])
                self.assertEqual(entry['hashes'], {a: mod[a] for a in ('sha1', 'sha512')})
                self.assertTrue(all(u.startswith('https://cdn.modrinth.com/') for u in entry['downloads']))
            self.assertIn(journey_name, got)
            self.assertEqual(
                next(f['downloads'] for f in index['files'] if Path(f['path']).name == journey_name),
                ['https://cdn.modrinth.com/data/lfHFW1mp/versions/OCuB6UWq/journeymap-neoforge-26.3-6.0.9.jar'],
            )
            for name in archive.namelist():
                if name.startswith('client-overrides/mods/') and name.endswith('.jar'):
                    self.assertTrue(name.startswith('client-overrides/mods/'))
                    self.assertNotEqual(Path(name).name, journey_name)
                    got.add(Path(name).name)
                    self.assertEqual(hashlib.sha512(archive.read(name)).hexdigest(), mods[Path(name).name]['sha512'])
            self.assertEqual(got, set(mods))
            self.assertIn('sources/iris/Iris-10d3598cd96b0566497b66efe66256f468cd977e-source.tar.gz', archive.namelist())
            self.assertNotIn('client-overrides/shaderpacks/ComplementaryReimagined_r5.9.3.zip', archive.namelist())


if __name__ == '__main__':
    unittest.main()
