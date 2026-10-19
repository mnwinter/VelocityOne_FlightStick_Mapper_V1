"""Catch text encodings that prevent GitHub Pages from building the site."""
from pathlib import Path
import unittest


class DocumentationEncodingTests(unittest.TestCase):
    def test_pages_sources_are_utf8(self):
        docs = Path(__file__).resolve().parents[1] / 'docs'
        sources = [p for p in docs.rglob('*')
                   if p.suffix.lower() in {'.md', '.html', '.css', '.scss', '.yml', '.yaml'}]
        self.assertTrue(sources)
        for path in sources:
            with self.subTest(path=str(path.relative_to(docs))):
                path.read_bytes().decode('utf-8', errors='strict')


if __name__ == '__main__':
    unittest.main()
