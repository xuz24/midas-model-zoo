import re
import unittest

from backend.app import app


class HomepageTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_and_built_assets(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('Discover Research', html)
        self.assertIn('id="research-explorer"', html)
        assets = re.findall(r'(?:src|href)="(/static/dist/[^\"]+)"', html)
        self.assertGreaterEqual(len(assets), 2)
        for path in assets:
            with self.subTest(asset=path):
                asset = self.client.get(path)
                self.assertEqual(asset.status_code, 200)
                asset.close()

    def test_placeholder_destinations(self):
        for feature in ['login', 'project', 'github', 'contact', 'docs']:
            with self.subTest(feature=feature):
                response = self.client.get('/coming-soon/' + feature)
                self.assertEqual(response.status_code, 200)
                self.assertIn('PLATFORM PREVIEW', response.get_data(as_text=True))
        self.assertEqual(self.client.get('/coming-soon/unknown').status_code, 404)

    def test_submission_preview(self):
        response = self.client.get('/submit')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('Information entered here is not saved or sent.', html)
        self.assertIn('type="button" aria-describedby="submission-notice"', html)
        self.assertEqual(self.client.post('/submit', data={'title': 'Example'}).status_code, 405)
        legacy = self.client.get('/coming-soon/submit')
        self.assertEqual(legacy.status_code, 302)
        self.assertEqual(legacy.headers['Location'], '/submit')


if __name__ == '__main__':
    unittest.main()
