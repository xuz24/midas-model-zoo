import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.app import app
from backend.app.records import KINDS, catalog_entries, load_records, safe_url


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_catalogs_and_detail_pages(self):
        for kind in KINDS:
            with self.subTest(kind=kind):
                records = load_records(kind)
                response = self.client.get('/' + kind)
                self.assertEqual(response.status_code, 200)
                html = response.get_data(as_text=True)
                self.assertIn(f'href="/{kind}" aria-current="page"', html)
                data_id = 'model-data' if kind == 'models' else 'catalog-data'
                payload = re.search(r'<script id="' + data_id + r'" type="application/json">(.*?)</script>', html, re.S)
                entries = json.loads(payload.group(1))
                self.assertEqual({e['id'] for e in entries}, {r['id'] for r in records})
                self.assertNotIn('Demo catalog', html)
                for entry in entries:
                    detail = self.client.get(entry['detail_url'])
                    self.assertEqual(detail.status_code, 200)
                    self.assertIn('Record details', detail.get_data(as_text=True))
                self.assertEqual(self.client.get(f'/{kind}/missing-record').status_code, 404)

    def test_empty_catalogs(self):
        for kind in KINDS:
            with self.subTest(kind=kind), patch('backend.app.get_' + kind, return_value=[]):
                self.assertEqual(self.client.get('/' + kind).status_code, 200)

    def test_home_uses_all_records(self):
        html = self.client.get('/').get_data(as_text=True)
        payload = re.search(r'<script id="research-data" type="application/json">(.*?)</script>', html, re.S)
        entries = json.loads(payload.group(1))
        self.assertEqual(len(entries), sum(len(load_records(kind)) for kind in KINDS))
        self.assertEqual(len(entries), len({entry['id'] for entry in entries}))
        self.assertIn('id="research-carousel"', html)
        self.assertNotIn('class="visual-grid"', html)
        for entry in entries:
            self.assertRegex(entry['updated'], r'^\d{4}-\d{2}-\d{2}$')

    def test_related_records_and_missing_optional_fields(self):
        html = self.client.get('/models/bert-base-uncased').get_data(as_text=True)
        self.assertIn('/datasets/wikipedia-2020', html)
        self.assertIn('/papers/devlin-2018-bert', html)
        self.assertIn('https://huggingface.co/bert-base-uncased', html)
        dataset = catalog_entries('datasets')[0]
        self.assertEqual(dataset['owner'], 'Contributor not specified')

    def test_yaml_validation_and_safe_loading(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / 'models'
            folder.mkdir()
            (folder / 'template.md').write_text('Not YAML')
            path = folder / 'entry.yaml'
            valid = 'id: example\nname: Example\nsummary: Test\nlast_updated: 2026-10-21\n'
            with patch('backend.app.records.RECORDS_ROOT', root):
                path.write_text(valid)
                self.assertEqual(load_records('models')[0]['last_updated'], '2026-10-21')
                (folder / 'duplicate.yml').write_text(valid)
                with self.assertRaisesRegex(ValueError, 'Duplicate id'):
                    load_records('models')
                (folder / 'duplicate.yml').unlink()
                for invalid in ['!!python/object:builtins.object {}', 'id: missing-fields', valid.replace('2026-10-21', 'invalid')]:
                    path.write_text(invalid)
                    with self.assertRaisesRegex(ValueError, 'entry.yaml'):
                        load_records('models')

    def test_no_script_links(self):
        self.assertIsNone(safe_url('javascript:alert(1)'))
        self.assertIsNone(safe_url('file:///etc/passwd'))
        self.assertEqual(safe_url('https://example.org'), 'https://example.org')

    def test_json_safely_escapes_submission_text(self):
        entry = dict(id='test', title='</script><script>alert(1)</script>', owner='Lab', description='Demo', category='AI', format='CSV', tags=[], updated='2026-10-01', detail_url='/datasets/test')
        with patch('backend.app.get_datasets', return_value=[entry]):
            html = self.client.get('/datasets').get_data(as_text=True)
        self.assertNotIn(entry['title'], html)
        payload = re.search(r'<script id="catalog-data" type="application/json">(.*?)</script>', html, re.S)
        self.assertEqual(json.loads(payload.group(1))[0]['title'], entry['title'])
