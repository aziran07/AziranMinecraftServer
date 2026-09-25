"""Pinned-source acceptance checks for the Occultism Korean translation."""
import collections
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
JAR = ROOT / 'server-data-26.3-neoforge/mods/occultism-26.3-neoforge-1.256.0.jar'
JAR_SHA256 = '118d02366adffbd8ebbe0024f484c88d8720eff43fb70b1adfd7d0fde74ddb51'
TRANSLATIONS = ROOT / 'translations/occultism/ko_kr'
BASICS = {'getting_started', 'spirits', 'pentacles', 'rituals', 'summoning_rituals'}
FORMAT = re.compile(r'%(?:\d+\$)?[sd%]')
LINK = re.compile(r'\]\(([^)]*)\)')
# Brand names, purely symbolic values and multipliers are deliberately unchanged.
LITERAL_VALUES = {
    'Occultism', '', '...', '%s', 'x2', 'x3', 'x4', 'x6',
    '64x64', '32x32', '16x16', '%d/%d',
}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def read_json(value):
    return json.loads(value, object_pairs_hook=unique_object)


def partition(key):
    if not key.startswith('book.'):
        return 'interface'
    prefix = 'book.occultism.dictionary_of_spirits.'
    if key.startswith(prefix) and key[len(prefix):].split('.')[0] in BASICS:
        return 'guide_basics'
    return 'guide_advanced'


def source():
    if hashlib.sha256(JAR.read_bytes()).hexdigest() != JAR_SHA256:
        raise ValueError('Occultism JAR does not match the pinned translation source')
    with zipfile.ZipFile(JAR) as archive:
        return read_json(archive.read('assets/occultism/lang/en_us.json'))


def glossary_names():
    text = (ROOT / 'docs/OCCULTISM_KO_GLOSSARY.md').read_text()
    section = text.split('## 기존 이름 대응표\n')[1].split('## 현재 영어 파일')[0]
    names = {}
    for line in section.splitlines():
        if not line.startswith('| ') or '`' not in line:
            continue
        _, _, chosen, _, keys = [part.strip() for part in line.strip('|').split('|')]
        for key in re.findall(r'`([^`]+)`', keys):
            names[key] = chosen
    section = text.split('## 한국어 이름이 없던 주요 항목의 채택 표기\n')[1].split('\n## ', 1)[0]
    for line in section.splitlines():
        if line.startswith('| ') and '`' in line:
            _, _, chosen, keycell = [part.strip() for part in line.strip('|').split('|')]
            key = re.search(r'`([^`]+)`', keycell)[1]
            names[key] = chosen.split(' — ')[0]
    section = text.split('## 번역 중 추가한 공통 이름\n')[1].split('\n## ', 1)[0]
    common_names = {}
    for line in section.splitlines():
        if line.startswith('| ') and '`' in line:
            english, chosen, _ = [part.strip() for part in line.strip('|').split('|')]
            common_names[english] = chosen
    for key, english in source().items():
        if english in common_names:
            names[key] = common_names[english]
    return names


class TranslationChecks:
    shard = None

    @classmethod
    def setUpClass(cls):
        cls.english = {k: v for k, v in source().items() if partition(k) == cls.shard}
        cls.korean = read_json((TRANSLATIONS / f'{cls.shard}.json').read_text())

    def test_complete_key_set(self):
        self.assertEqual(set(self.korean), set(self.english))

    def test_actual_korean_and_preserved_literals(self):
        for key, value in self.korean.items():
            with self.subTest(key=key):
                self.assertIsInstance(value, str)
                original = self.english[key]
                if original in LITERAL_VALUES:
                    self.assertEqual(value, original)
                else:
                    self.assertRegex(value, '[가-힣]', 'Untranslated or empty value')
                self.assertNotIn('\ufffd', value)

    def test_placeholders_links_and_formatting(self):
        for key, original in self.english.items():
            with self.subTest(key=key):
                translated = self.korean[key]
                self.assertEqual(FORMAT.findall(translated), FORMAT.findall(original),
                                 'Preserve placeholder order/types; request review if indexing is needed')
                self.assertEqual(collections.Counter(LINK.findall(translated)),
                                 collections.Counter(LINK.findall(original)),
                                 'Preserve link destinations and color control targets')
                self.assertEqual(collections.Counter(re.findall(r'§.', translated)),
                                 collections.Counter(re.findall(r'§.', original)))
                self.assertEqual(translated.count('**'), original.count('**'))

    def test_approved_names(self):
        for key, expected in glossary_names().items():
            if key in self.english:
                with self.subTest(key=key):
                    self.assertEqual(self.korean[key], expected)

    def test_explicit_numbers_are_preserved(self):
        # Link destinations include color codes and IDs, checked separately.
        # Keep written numerals so quantities, percentages and steps cannot disappear.
        for key, original in self.english.items():
            with self.subTest(key=key):
                english = LINK.sub(']', original)
                korean = LINK.sub(']', self.korean[key])
                # Approved lexical spelling: Third Eye -> 제3의 눈.
                if re.search(r'Third Eye', original, re.IGNORECASE):
                    korean = korean.replace('제3의 눈', '제삼의 눈')
                self.assertEqual(collections.Counter(re.findall(r'\d+(?:\.\d+)?', korean)),
                                 collections.Counter(re.findall(r'\d+(?:\.\d+)?', english)))


class InterfaceTranslationTests(TranslationChecks, unittest.TestCase):
    shard = 'interface'


class BasicsTranslationTests(TranslationChecks, unittest.TestCase):
    shard = 'guide_basics'

    def test_vanilla_material_names_and_config_labels(self):
        text = '\n'.join(self.korean.values())
        self.assertNotIn('싹트는 자수정', text)
        self.assertIn('싹 틔우는 자수정', text)
        guide = self.korean['book.occultism.dictionary_of_spirits.getting_started.divination_rod.config.text']
        self.assertIn('아이템', guide)
        self.assertIn('c:ores 광석 탐지', guide)


class AdvancedTranslationTests(TranslationChecks, unittest.TestCase):
    shard = 'guide_advanced'

    def test_vanilla_material_names(self):
        self.assertEqual(self.korean['book.occultism.dictionary_of_spirits.crafting_rituals.craft_budding_amethyst.name'],
                         '싹 틔우는 자수정 벼리기')
        self.assertEqual(self.korean['book.occultism.dictionary_of_spirits.crafting_rituals.craft_reinforced_deepslate.name'],
                         '보강된 심층암 벼리기')


class ResourcePackTests(unittest.TestCase):
    def test_zip_has_complete_translation_and_target_metadata(self):
        path = ROOT / 'dist/occultism-ko-1.256.0-mc26.3.zip'
        with zipfile.ZipFile(path) as archive:
            self.assertIsNone(archive.testzip())
            names = archive.namelist()
            self.assertEqual(len(names), len(set(names)))
            self.assertIn('pack.mcmeta', names)
            self.assertIn('assets/occultism/lang/ko_kr.json', names)
            self.assertFalse(any(n.endswith('.jar') or n.startswith('data/') for n in names))
            self.assertTrue(all(not n.startswith('/') and '..' not in Path(n).parts for n in names))
            metadata = read_json(archive.read('pack.mcmeta'))['pack']
            self.assertEqual(metadata['min_format'], [97, 1])
            self.assertEqual(metadata['max_format'], [97, 1])
            merged = {}
            for name in ('interface', 'guide_basics', 'guide_advanced'):
                data = read_json((TRANSLATIONS / f'{name}.json').read_text())
                self.assertFalse(set(merged) & set(data))
                merged.update(data)
            actual = read_json(archive.read('assets/occultism/lang/ko_kr.json'))
            self.assertEqual(actual, merged)
            self.assertEqual(set(actual), set(source()))


class BuilderFailureTests(unittest.TestCase):
    def run_builder(self, jar, translations, output):
        return subprocess.run(
            [sys.executable, str(ROOT / 'scripts/build_occultism_resource_pack.py'),
             '--source-jar', str(jar), '--translations-dir', str(translations),
             '--output', str(output)], text=True, capture_output=True, cwd=ROOT)

    def test_wrong_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            jar = folder / 'wrong.jar'
            jar.write_bytes(b'not the pinned Occultism release')
            output = folder / 'pack.zip'
            result = self.run_builder(jar, TRANSLATIONS, output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('SHA-256', result.stdout + result.stderr)
            self.assertFalse(output.exists())

    def test_missing_translation_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            translations = folder / 'translations'
            shutil.copytree(TRANSLATIONS, translations)
            path = translations / 'interface.json'
            values = read_json(path.read_text())
            del values['item.occultism.datura']
            path.write_text(json.dumps(values, ensure_ascii=False))
            output = folder / 'pack.zip'
            result = self.run_builder(JAR, translations, output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('item.occultism.datura', result.stdout + result.stderr)
            self.assertFalse(output.exists())

    def test_duplicate_translation_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            translations = folder / 'translations'
            shutil.copytree(TRANSLATIONS, translations)
            path = translations / 'interface.json'
            text = path.read_text().rstrip()
            path.write_text(text[:-1] + ',"item.occultism.datura":"중복"}')
            output = folder / 'pack.zip'
            result = self.run_builder(JAR, translations, output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('item.occultism.datura', result.stdout + result.stderr)
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
