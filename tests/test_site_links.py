"""Catch broken local navigation and assets when guides move between pages."""

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import unquote, urlsplit


SITE = Path(__file__).resolve().parents[1] / 'site'


class PageLinks(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = []
        self.urls = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for attr in ('href', 'src'):
            if attrs.get(attr):
                self.urls.append(attrs[attr])


class SiteLinkTests(unittest.TestCase):
    def test_local_links_fragments_and_assets_resolve(self):
        pages = {path: PageLinks(path.read_text()) for path in SITE.glob('*.html')}
        self.assertIn(SITE / 'index.html', pages)
        for path, page in pages.items():
            with self.subTest(page=path.name):
                duplicates = [key for key, count in Counter(page.ids).items() if count > 1]
                self.assertEqual(duplicates, [], 'Duplicate HTML IDs')
            for url in page.urls:
                target = urlsplit(url)
                if target.scheme or target.netloc:
                    continue
                with self.subTest(page=path.name, url=url):
                    local = unquote(target.path)
                    if local.startswith('/'):
                        destination = SITE / local.lstrip('/')
                    elif local:
                        destination = path.parent / local
                    else:
                        destination = path
                    destination = destination.resolve()
                    if destination.is_dir():
                        destination /= 'index.html'
                    self.assertTrue(destination.is_relative_to(SITE), 'Link escapes published site')
                    self.assertTrue(destination.is_file(), 'Missing linked file')
                    if target.fragment and destination in pages:
                        self.assertIn(unquote(target.fragment), pages[destination].ids,
                                      'Missing linked HTML anchor')


if __name__ == '__main__':
    unittest.main()
