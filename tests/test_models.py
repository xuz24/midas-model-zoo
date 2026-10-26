import json
import re
import unittest
from unittest.mock import patch

from backend.app import app


class ModelCatalogTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_catalog_data_and_navigation(self):
        response = self.client.get('/models')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('id="model-explorer"', html)
        self.assertIn('href="/models" aria-current="page"', html)
        payload = re.search(r'<script id="model-data" type="application/json">(.*?)</script>', html, re.S)
        models = json.loads(payload.group(1))
        self.assertEqual(len(models), 2)
        self.assertEqual(len({model['id'] for model in models}), 2)
        self.assertIn('BERT Base (Uncased)', html)
        self.assertEqual(self.client.get('/coming-soon/model').status_code, 200)

    def test_empty_catalog(self):
        with patch('backend.app.get_models', return_value=[]):
            response = self.client.get('/models')
        self.assertEqual(response.status_code, 200)
        self.assertIn('No models available yet.', response.get_data(as_text=True))

    def test_previous_placeholder_redirects(self):
        response = self.client.get('/coming-soon/models')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/models')
