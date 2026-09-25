"""Check that every local guide page is served over HTTP."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import unittest
from urllib.request import urlopen


SITE = Path(__file__).resolve().parents[1] / 'site'


class JoinGuideTests(unittest.TestCase):
    def test_html_pages_return_200(self):
        pages = sorted(SITE.glob('*.html'))
        self.assertTrue(pages, 'site/에 HTML 페이지가 없습니다')

        handler = partial(SimpleHTTPRequestHandler, directory=str(SITE))
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = Thread(target=server.serve_forever)
        thread.start()
        try:
            for page in pages:
                with self.subTest(page=page.name):
                    with urlopen(f'http://127.0.0.1:{server.server_port}/{page.name}',
                                 timeout=5) as response:
                        self.assertEqual(response.status, 200)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__':
    unittest.main()
