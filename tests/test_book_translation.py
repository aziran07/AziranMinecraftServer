"""Coverage beyond Occultism's language table, including Modonomicon itself."""

import collections
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile

from test_occultism_translation import JAR, ROOT, read_json, source


MODONOMICON = ROOT / 'server-data-26.3-neoforge/mods/modonomicon-26.3-neoforge-2.7.0.jar'
MODONOMICON_SHA256 = '27e1ca11f161012cc95c114beb5b58a96081d189857301c0d8a93466a4ad370a'
PACK = ROOT / 'dist/occultism-ko-1.256.0-mc26.3.zip'
LITERALS = ROOT / 'translations/occultism/ko_kr/book_overrides.json'
MOD_TRANSLATIONS = ROOT / 'translations/modonomicon/ko_kr.json'
FORMAT = re.compile(r'%(?:\d+\$)?[sd%]')
LINK = re.compile(r'\]\(([^)]*)\)')


def book_literals():
    """Find prose and dangling book keys omitted from the upstream language table."""
    english = source()
    result = {}
    with zipfile.ZipFile(JAR) as archive:
        for name in archive.namelist():
            if not name.startswith('data/occultism/modonomicon/books/') or not name.endswith('.json'):
                continue
            document = read_json(archive.read(name))
            for field in ('text', 'title', 'name', 'description'):
                value = document.get(field)
                if isinstance(value, str) and value and value not in english:
                    result.setdefault(value, []).append((name, field))
    return result


class BookTranslationTests(unittest.TestCase):
    def test_every_occultism_book_literal_resolves_in_pack(self):
        originals = book_literals()
        self.assertEqual(len(originals), 9)
        self.assertEqual(sum(key.startswith('book.') for key in originals), 4)
        translated = read_json(LITERALS.read_text())
        self.assertEqual(set(translated), set(originals))
        with zipfile.ZipFile(PACK) as archive:
            actual = read_json(archive.read('assets/occultism/lang/ko_kr.json'))
            self.assertEqual(set(actual), set(source()) | set(originals))
            self.assertFalse(any(name.startswith('data/') for name in archive.namelist()))
        for original, locations in originals.items():
            with self.subTest(locations=locations):
                # Use the exact page string, including its trailing newline, as I18n does.
                self.assertEqual(actual[original], translated[original])
                self.assertRegex(actual[original], '[가-힣]')
                self.assertNotIn(original.strip(), actual[original])

    def test_complete_modonomicon_translation_and_formatting(self):
        self.assertEqual(hashlib.sha256(MODONOMICON.read_bytes()).hexdigest(), MODONOMICON_SHA256)
        with zipfile.ZipFile(MODONOMICON) as archive:
            english = read_json(archive.read('assets/modonomicon/lang/en_us.json'))
        korean = read_json(MOD_TRANSLATIONS.read_text())
        self.assertEqual(len(english), 309)
        self.assertEqual(set(korean), set(english))
        # Names, emoticons, empty strings and pure formatting have no prose to translate.
        unchanged = {'Modonomicon', '', ':(', '%s.\n%s', '%s mb', '%s / %s mb'}
        for key, original in english.items():
            with self.subTest(key=key):
                translated = korean[key]
                self.assertIsInstance(translated, str)
                if original in unchanged:
                    self.assertEqual(translated, original)
                else:
                    self.assertRegex(translated, '[가-힣]')
                self.assertNotIn('\ufffd', translated)
                self.assertEqual(FORMAT.findall(translated), FORMAT.findall(original))
                self.assertEqual(collections.Counter(LINK.findall(translated)),
                                 collections.Counter(LINK.findall(original)))
                self.assertEqual(collections.Counter(re.findall(r'§.', translated)),
                                 collections.Counter(re.findall(r'§.', original)))
                self.assertEqual(collections.Counter(re.findall(r'\d+(?:\.\d+)?', translated)),
                                 collections.Counter(re.findall(r'\d+(?:\.\d+)?', original)))
        with zipfile.ZipFile(PACK) as archive:
            self.assertEqual(read_json(archive.read('assets/modonomicon/lang/ko_kr.json')), korean)
            notice = archive.read('NOTICE.md').decode()
            self.assertIn('Modonomicon', notice)
            self.assertIn('CC-BY-SA-4.0', notice)

    def run_invalid_build(self, output, *arguments):
        output.write_bytes(b'existing verified pack')
        result = subprocess.run(
            [sys.executable, str(ROOT / 'scripts/build_occultism_resource_pack.py'),
             '--output', str(output), *map(str, arguments)],
            cwd=ROOT, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output.read_bytes(), b'existing verified pack')
        return result.stdout + result.stderr

    def test_changed_modonomicon_source_preserves_existing_pack(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            jar = folder / 'wrong.jar'
            jar.write_bytes(b'wrong source')
            error = self.run_invalid_build(folder / 'pack.zip', '--modonomicon-jar', jar)
            self.assertIn('SHA-256', error)

    def test_missing_modonomicon_translation_preserves_existing_pack(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            translations = read_json(MOD_TRANSLATIONS.read_text())
            key = 'modonomicon.gui.button.next_page'
            del translations[key]
            path = folder / 'ko_kr.json'
            path.write_text(json.dumps(translations, ensure_ascii=False))
            error = self.run_invalid_build(folder / 'pack.zip', '--modonomicon-translations', path)
            self.assertIn(key, error)

    def test_missing_literal_translation_preserves_existing_pack(self):
        import shutil

        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            translations = folder / 'ko_kr'
            shutil.copytree(LITERALS.parent, translations)
            values = read_json(LITERALS.read_text())
            key = next(iter(values))
            del values[key]
            (translations / LITERALS.name).write_text(json.dumps(values, ensure_ascii=False))
            error = self.run_invalid_build(folder / 'pack.zip', '--translations-dir', translations)
            self.assertIn(key.strip(), error)


if __name__ == '__main__':
    unittest.main()
