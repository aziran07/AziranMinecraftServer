"""Check the public join guide's installation contract and local links."""
from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import unquote, urlsplit


SITE = Path(__file__).resolve().parents[1] / 'site'
PACK_URL = ('https://github.com/aziran07/AziranMinecraftServer/releases/download/'
            'client-1.1.4/aziran-26.3-client-1.1.4.mrpack')


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

    def test_installation_details_and_download(self):
        text = ' '.join(self.page.text)
        for required in ('mc.aziran.uk', '26.3', '1.1.4', 'Java', '25', 'Prism',
                         'ComplementaryReimagined_r5.9.3', 'key.keyboard.unknown'):
            self.assertIn(required, text)
        links = [attrs.get('href') for tag, attrs in self.page.tags if tag == 'a']
        self.assertIn(PACK_URL, links)
        self.assertIn('https://prismlauncher.org/download/', links)
        self.assertTrue(any('확인' in part for part in self.page.text))

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

    def test_local_resources_and_publication_boundary(self):
        for tag, attrs in self.page.tags:
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
        self.assertEqual((SITE / 'CNAME').read_text().strip(), 'aziran.uk')
        self.assertTrue((SITE / '.nojekyll').is_file())
        forbidden = {'.env', 'key.pem', 'cert.pem', 'server.properties', 'ops.json'}
        self.assertFalse([p.name for p in SITE.rglob('*') if p.name in forbidden])


if __name__ == '__main__':
    unittest.main()
