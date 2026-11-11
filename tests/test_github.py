import unittest
from unittest.mock import Mock, patch

import requests

from backend.app import app
from backend.app.github import _cache, fetch_repository, repository_path, sanitize_readme


class GitHubTests(unittest.TestCase):
    def setUp(self):
        _cache.clear()

    def test_repository_links(self):
        self.assertEqual(repository_path({'source_url': 'https://github.com/org/repo.git/tree/main'}), 'org/repo')
        for url in ['https://github.com.evil.org/o/r', 'https://github.com@evil.org/o/r', 'https://github.com/o', 'file://github.com/o/r']:
            self.assertIsNone(repository_path({'source_url': url}))

    def test_sanitization_and_relative_urls(self):
        html = sanitize_readme('<script>alert(1)</script><img src="images/test.png" onerror="bad()"><a href="javascript:bad()">bad</a><a href="docs/start.md">Docs</a>', 'org/repo', 'main')
        self.assertNotIn('<script', html)
        self.assertNotIn('onerror', html)
        self.assertNotIn('javascript:', html)
        self.assertIn('https://raw.githubusercontent.com/org/repo/main/images/test.png', html)
        self.assertIn('https://github.com/org/repo/blob/main/docs/start.md', html)

    @patch('backend.app.github.requests.get')
    def test_fetch_render_and_cache(self, get):
        get.side_effect = [Mock(status_code=200, json=lambda: dict(full_name='org/repo', description='Research code', stargazers_count=12, forks_count=3, language='Python', license={'name': 'MIT'}, created_at='2020-01-01T00:00:00Z', updated_at='2026-01-01T00:00:00Z', topics=['science'], homepage='https://example.org', default_branch='main')), Mock(status_code=200, text='<h1>Read me</h1>')]
        result = fetch_repository('org/repo')
        self.assertEqual(fetch_repository('org/repo'), result)
        self.assertEqual(get.call_count, 2)
        with patch('backend.app.repository_path', return_value='org/repo'):
            html = app.test_client().get('/software/scikit-learn').get_data(as_text=True)
        for value in ['Research code', 'Python', 'MIT', 'science', '<h1>Read me</h1>', '2020-01-01T00:00:00Z']:
            self.assertIn(value, html)

    @patch('backend.app.github.requests.get')
    def test_failures_and_missing_readme(self, get):
        get.side_effect = requests.Timeout()
        self.assertIsNone(fetch_repository('org/repo'))
        self.assertIsNone(fetch_repository('org/repo'))
        self.assertEqual(get.call_count, 1)
        _cache.clear()
        get.side_effect = [Mock(status_code=200, json=lambda: {'full_name': 'org/repo'}), Mock(status_code=404)]
        self.assertIsNone(fetch_repository('org/repo')['readme'])

    def test_unavailable_page(self):
        with patch('backend.app.fetch_repository', return_value=None):
            response = app.test_client().get('/software/scikit-learn')
        self.assertEqual(response.status_code, 200)
        self.assertIn('temporarily unavailable', response.get_data(as_text=True))
