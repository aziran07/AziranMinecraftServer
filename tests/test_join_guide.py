"""Check the public join guide's installation contract and local links."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit


SITE = Path(__file__).resolve().parents[1] / 'site'
PACK_URL = ('https://github.com/aziran07/AziranMinecraftServer/releases/download/'
            'client-1.1.5/aziran-26.3-client-1.1.5.mrpack')
OCCULTISM_URL = 'https://www.curseforge.com/minecraft/mc-mods/occultism'


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.tags = []
        self.text = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


class JoinGuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = Page((SITE / 'index.html').read_text())

    def assert_local_resources_exist(self, page):
        for tag, attrs in page.tags:
            for key in ('src', 'href'):
                value = attrs.get(key)
                if not value or value.startswith('#'):
                    continue
                url = urlsplit(value)
                self.assertNotEqual(url.scheme, 'http', value)
                if url.scheme or url.netloc:
                    continue
                path = (SITE / unquote(url.path).lstrip('/')).resolve()
                self.assertTrue(path.is_relative_to(SITE.resolve()), value)
                self.assertTrue(path.is_file(), value)

    def test_installation_details_and_download(self):
        text = ' '.join(self.page.text)
        for required in ('mc.aziran.uk', '26.3', '1.1.5', 'Java', '25', 'Prism',
                         'ComplementaryReimagined_r5.9.3', 'key.keyboard.unknown'):
            self.assertIn(required, text)
        links = [attrs.get('href') for tag, attrs in self.page.tags if tag == 'a']
        self.assertIn(PACK_URL, links)
        self.assertIn('https://prismlauncher.org/download/', links)
        self.assertIn('서버가 이미 들어 있습니다', text)
        self.assertIn('문제가 생기면 오류 내용을 알려 주세요', text)

    def test_accessibility_basics(self):
        tags = self.page.tags
        self.assertTrue(any(tag == 'html' and attrs.get('lang') == 'ko'
                            for tag, attrs in tags))
        self.assertTrue(any(tag == 'meta' and attrs.get('name') == 'viewport'
                            for tag, attrs in tags))
        self.assertEqual(sum(tag == 'h1' for tag, _ in tags), 1)
        self.assertTrue(any(tag == 'main' for tag, _ in tags))
        self.assertTrue(any(attrs.get('aria-live') in ('polite', 'assertive')
                            for _, attrs in tags))

    def test_java_preparation_is_part_of_installation_steps(self):
        source = (SITE / 'index.html').read_text()
        steps = re.search(r'<section\b[^>]*\bid="steps"[^>]*>(.*?)</section>',
                          source, re.DOTALL)
        self.assertIsNotNone(steps)
        step_html = steps.group(1)
        self.assertEqual(step_html.count('class="step"'), 4)
        self.assertIn('id="java"', step_html)
        self.assertIn('Java 25', step_html)
        self.assertIn('https://prismlauncher.org/wiki/getting-started/installing-java/',
                      step_html)
        self.assertIn('설치되어 있', step_html)
        self.assertIn('설치할 필요', step_html)
        self.assertRegex(step_html, r'<img\b[^>]*\bsrc="prism-java-settings\.png"'
                                    r'[^>]*\balt="[^"]+"')
        self.assertNotRegex(source, r'<section\b[^>]*\bid="java"')

    def test_local_resources_and_publication_boundary(self):
        self.assert_local_resources_exist(self.page)
        self.assertEqual((SITE / 'CNAME').read_text().strip(), 'aziran.uk')
        self.assertTrue((SITE / '.nojekyll').is_file())
        forbidden = {'.env', 'key.pem', 'cert.pem', 'server.properties', 'ops.json'}
        self.assertFalse([p.name for p in SITE.rglob('*') if p.name in forbidden])

    def test_occultism_guide_is_linked_from_home(self):
        links = [attrs.get('href') for tag, attrs in self.page.tags if tag == 'a']
        self.assertIn('occultism.html', links)
        self.assertIn('Occultism', ' '.join(self.page.text))

    def test_public_web_map_is_linked_and_explained(self):
        source = (SITE / 'index.html').read_text()
        links = [attrs.get('href') for tag, attrs in self.page.tags if tag == 'a']
        self.assertIn('https://mcmap.aziran.uk/', links)
        self.assertIn('#webmap', links)
        self.assertRegex(source, r'<section\b[^>]*\bid="webmap"')
        self.assertIn('BlueMap', source)

    def test_occultism_guide_has_verified_first_steps_and_sources(self):
        guide = Page((SITE / 'occultism.html').read_text())
        text = ' '.join(guide.text)
        for required in ('Occultism', "Demon's Dream", 'Dictionary of Spirits'):
            self.assertIn(required, text)
        links = [attrs.get('href') for tag, attrs in guide.tags if tag == 'a']
        self.assertIn(OCCULTISM_URL, links)
        self.assertIn('index.html', links)
        self.assertTrue(any(tag == 'html' and attrs.get('lang') == 'ko'
                            for tag, attrs in guide.tags))
        self.assertEqual(sum(tag == 'h1' for tag, _ in guide.tags), 1)
        self.assertTrue(any(tag == 'main' for tag, _ in guide.tags))
        self.assert_local_resources_exist(guide)


if __name__ == '__main__':
    unittest.main()
