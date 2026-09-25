"""Client 1.1.9 must install the requested packs and enable only the translation."""

import hashlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION = 'occultism-ko-1.256.0-mc26.3.zip'


class ClientResourcePackTests(unittest.TestCase):
    def test_missing_or_corrupt_external_pack_is_rejected(self):
        spec = importlib.util.spec_from_file_location('resource_builder', ROOT / 'scripts/build_client_pack.py')
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        locked = json.loads((ROOT / 'mods-26.3-client-extra.lock.json').read_text())
        external = [p for p in locked['resourcepacks'] if p['source'] != 'repository-build']
        self.assertEqual(len(external), 2)
        with tempfile.TemporaryDirectory() as directory:
            builder.CLIENT_CACHE = Path(directory)
            for pack in external:
                with self.subTest(pack=pack['title']):
                    with self.assertRaisesRegex(SystemExit, '리소스팩이 없다'):
                        builder.load_resourcepacks({'resourcepacks': [pack]})
                    (builder.CLIENT_CACHE / pack['filename']).write_bytes(b'corrupt download')
                    with self.assertRaisesRegex(SystemExit, '일치하지 않는다'):
                        builder.load_resourcepacks({'resourcepacks': [pack]})

    def test_translation_build_failure_stops_client_build(self):
        spec = importlib.util.spec_from_file_location('resource_builder', ROOT / 'scripts/build_client_pack.py')
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / 'failing_translation_builder.py'
            script.write_text('raise SystemExit(3)\n')
            builder.TRANSLATION_BUILDER = script
            with self.assertRaisesRegex(SystemExit, '종료 코드 3'):
                builder.build_translation_pack()

    def test_pack_delivery_and_defaults(self):
        lock = json.loads((ROOT / 'mods-26.3-client.lock.json').read_text())
        self.assertEqual(lock['pack_version'], '1.1.9')
        packs = lock['resourcepacks']
        self.assertEqual(len(packs), 3)
        self.assertEqual(len({pack['filename'] for pack in packs}), 3)
        self.assertEqual({pack['title'] for pack in packs},
                         {'Occultism 한국어 번역', 'Stay True', 'Vanilla Experience+'})
        by_title = {pack['title']: pack for pack in packs}
        self.assertTrue(by_title['Stay True']['bundle_file'])
        self.assertEqual(by_title['Stay True']['sha256'],
                         'c61397d8e9d1f15e069f718c0bd61c5c347be1f3e18603ea576dccb570302c82')
        self.assertTrue(by_title['Occultism 한국어 번역']['bundle_file'])
        self.assertFalse(by_title['Vanilla Experience+']['bundle_file'])
        self.assertEqual(by_title['Vanilla Experience+']['sha512'],
                         '49ee05cc8e995b576cff053f2a24fbf62775f56c1a6a9701907abc8e42667b7c1999c1c023be2b73a1722b72e7b26191d80ad0830e8e632c2f2920051192709f')
        self.assertEqual([p['filename'] for p in packs if p['enabled_by_default']],
                         [TRANSLATION])
        archives = {
            'aziran-26.3-client-1.1.9.mrpack': 'client-overrides/',
            'aziran-26.3-client-1.1.9-manual.zip': '',
            'aziran-26.3-client-1.1.9-multimc.zip': '.minecraft/',
        }
        for filename, prefix in archives.items():
            with self.subTest(archive=filename), zipfile.ZipFile(ROOT / 'dist' / filename) as archive:
                options = dict(line.split(':', 1) for line in
                               archive.read(prefix + 'options.txt').decode().splitlines())
                self.assertEqual(options['lang'], 'ko_kr')
                selected = json.loads(options['resourcePacks'])
                self.assertEqual([p for p in selected if p.startswith('file/')],
                                 ['file/' + TRANSLATION])
                self.assertIn('vanilla', selected)
                # NeoForge otherwise inserts its required mod resources at the top,
                # overriding the translation with the language bundled in the mod.
                self.assertIn('mod_resources', selected)
                self.assertLess(selected.index('mod_resources'), selected.index('file/' + TRANSLATION))
                downloads = {}
                if filename.endswith('.mrpack'):
                    index = json.loads(archive.read('modrinth.index.json'))
                    downloads = {entry['path']: entry for entry in index['files']}
                for pack in packs:
                    path = 'resourcepacks/' + pack['filename']
                    if pack['bundle_file']:
                        data = archive.read(prefix + path)
                        self.assertEqual(len(data), pack['size'])
                        self.assertEqual(hashlib.sha512(data).hexdigest(), pack['sha512'])
                        with zipfile.ZipFile(io.BytesIO(data)) as inner:
                            self.assertIsNone(inner.testzip())
                            self.assertIn('pack.mcmeta', inner.namelist())
                        self.assertNotIn(path, downloads)
                    else:
                        self.assertNotIn(prefix + path, archive.namelist())
                        if filename.endswith('.mrpack'):
                            entry = downloads[path]
                            self.assertEqual(entry['downloads'], [pack['url']])
                            self.assertTrue(pack['url'].startswith('https://cdn.modrinth.com/'))
                            self.assertEqual(entry['hashes']['sha512'], pack['sha512'])
                            self.assertEqual(entry['fileSize'], pack['size'])
                            # Download even though activation remains the user's choice.
                            self.assertEqual(entry['env'], {'client': 'required', 'server': 'unsupported'})
                        self.assertIn(pack['url'], archive.read('README.md').decode())
                translation_data = archive.read(prefix + 'resourcepacks/' + TRANSLATION)
                self.assertEqual(translation_data, (ROOT / 'dist' / TRANSLATION).read_bytes())
                if filename.endswith('-manual.zip'):
                    manifest = json.loads(archive.read('manifest.json'))
                    entries = {entry['path']: entry for entry in manifest['files']}
                    for pack in packs:
                        path = 'resourcepacks/' + pack['filename']
                        if pack['bundle_file']:
                            self.assertEqual(entries[path]['sha512'], pack['sha512'])
                        else:
                            self.assertNotIn(path, entries)


if __name__ == '__main__':
    unittest.main()
