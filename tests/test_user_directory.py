from types import SimpleNamespace
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from backend.app import app
from backend.app.db_models import User


class UserDirectoryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        User.__table__.create(self.engine)
        self.session = Session(self.engine)
        self.addCleanup(self.engine.dispose)
        self.addCleanup(self.session.close)
        database = SimpleNamespace(select=select, session=self.session)
        mocked = patch('backend.app.users.db', database)
        mocked.start()
        self.addCleanup(mocked.stop)
        self.client = app.test_client()
        self.session.add_all([
            User(username='alice', google_sub='private-google-alice', name='Alice Smith',
                 email='private-alice@example.org', picture_url='https://lh3.googleusercontent.com/a/alice', institution='University of Michigan',
                 role='Professor', research_interests='Machine learning, Digital humanities',
                 bio='Studies historical archives.'),
            User(username='bob', google_sub='private-google-bob', name='Bob Jones',
                 email='private-bob@example.org', research_interests='Public health',
                 bio='Community research.'),
        ])
        self.session.commit()

    def test_directory_and_public_profile_links(self):
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        for text in ('2 researchers', 'Alice Smith', 'Bob Jones', 'Digital humanities',
                     'University of Michigan', 'href="/user/alice"', 'href="/user/bob"',
                     'href="/users" aria-current="page"'):
            self.assertIn(text, html)
        self.assertIn('https://lh3.googleusercontent.com/a/alice', html)
        self.assertIn('<span>B</span>', html)
        for text in ('private-alice@example.org', 'private-google-alice', 'Edit profile'):
            self.assertNotIn(text, html)

    def test_searches_public_fields_case_insensitively(self):
        for query in ('  ALICE  ', 'smith', 'michigan', 'professor', 'digital humanities', 'archives'):
            with self.subTest(query=query):
                html = self.client.get('/users', query_string={'q': query}).get_data(as_text=True)
                self.assertIn('href="/user/alice"', html)
                self.assertNotIn('href="/user/bob"', html)
                self.assertIn('1 researcher matching', html)
        html = self.client.get('/users?q=private-alice').get_data(as_text=True)
        self.assertIn('No researchers found', html)

    def test_email_is_visible_only_to_profile_owner(self):
        for viewer in (None, 'alice', 'bob'):
            with self.subTest(viewer=viewer):
                with self.client.session_transaction() as session:
                    session.clear()
                    if viewer:
                        session['username'] = viewer
                for username in ('alice', 'bob'):
                    response = self.client.get('/user/' + username)
                    self.assertEqual(response.status_code, 200)
                    html = response.get_data(as_text=True)
                    for account in ('alice', 'bob'):
                        email = f'private-{account}@example.org'
                        if viewer == username == account:
                            self.assertIn(email, html)
                            self.assertIn('Only visible to you', html)
                        else:
                            self.assertNotIn(email, html)
                directory = self.client.get('/users').get_data(as_text=True)
                for username in ('alice', 'bob'):
                    self.assertNotIn(f'private-{username}@example.org', directory)

    def test_search_treats_wildcards_as_literal_and_escapes_html(self):
        for query in ('%', '_', '<script>alert(1)</script>'):
            with self.subTest(query=query):
                html = self.client.get('/users', query_string={'q': query}).get_data(as_text=True)
                self.assertIn('No researchers found', html)
                self.assertNotIn('<script>alert(1)</script>', html)

    def test_empty_directory(self):
        self.session.query(User).delete()
        self.session.commit()
        html = self.client.get('/users').get_data(as_text=True)
        self.assertIn('The community is growing', html)
        self.assertIn('0 researchers', html)

    def test_directory_filters_combine_with_search_and_match_whole_values(self):
        for filters in (
            {'tag': 'machine learning'},
            {'institution': 'university of michigan'},
            {'role': 'professor'},
            {'q': 'archives', 'tag': 'Digital humanities', 'institution': 'University of Michigan', 'role': 'Professor'},
        ):
            with self.subTest(filters=filters):
                html = self.client.get('/users', query_string=filters).get_data(as_text=True)
                self.assertIn('href="/user/alice"', html)
                self.assertNotIn('href="/user/bob"', html)
                self.assertIn('aria-label="Filter researchers"', html)
                self.assertIn('Clear filters', html)
        for filters in ({'tag': 'Machine'}, {'role': 'Prof'}, {'institution': 'Michigan'},
                        {'tag': 'Machine learning', 'q': 'Bob'}, {'tag': 'missing'}):
            with self.subTest(filters=filters):
                html = self.client.get('/users', query_string=filters).get_data(as_text=True)
                self.assertIn('No researchers found', html)
                self.assertNotIn('href="/user/alice"', html)
                self.assertNotIn('href="/user/bob"', html)

    def test_filter_counts_and_search_preserve_selections(self):
        html = self.client.get('/users', query_string={'tag': 'Machine learning', 'role': 'Professor'}).get_data(as_text=True)
        self.assertIn('All <span>2</span>', html)
        self.assertIn('Machine learning <span>1</span>', html)
        self.assertIn('name="tag" value="Machine learning"', html)
        self.assertIn('name="role" value="Professor"', html)
        self.assertIn('tag=Machine+learning&amp;institution=University+of+Michigan&amp;role=Professor', html)
        self.assertNotIn('private-alice@example.org', html)

    def test_filtered_pagination_preserves_all_filters(self):
        self.session.add_all(User(username=f'filtered{i:02}', google_sub=f'filtered-sub{i}',
                                  name=f'Filtered {i:02}', research_interests='Climate science',
                                  institution='University of Michigan', role='Student') for i in range(25))
        self.session.commit()
        filters = dict(q='Filtered', tag='Climate science', institution='University of Michigan', role='Student')
        first = self.client.get('/users', query_string=filters).get_data(as_text=True)
        self.assertIn('Page 1 of 2', first)
        self.assertIn('q=Filtered&amp;tag=Climate+science&amp;institution=University+of+Michigan&amp;role=Student&amp;page=2', first)
        second = self.client.get('/users', query_string=dict(filters, page=2)).get_data(as_text=True)
        self.assertIn('href="/user/filtered24"', second)
        self.assertNotIn('href="/user/filtered00"', second)

    def test_sorting_uses_shared_catalog_controls_and_preserves_filters(self):
        from datetime import datetime
        self.session.get(User, 'alice').created_at = datetime(2026, 1, 1)
        self.session.get(User, 'bob').created_at = datetime(2026, 11, 1)
        self.session.commit()
        default = self.client.get('/users').get_data(as_text=True)
        recent = self.client.get('/users?sort=joined').get_data(as_text=True)
        self.assertLess(default.index('href="/user/alice"'), default.index('href="/user/bob"'))
        self.assertLess(recent.index('href="/user/bob"'), recent.index('href="/user/alice"'))
        self.assertIn('class="catalog-sort"', recent)
        self.assertIn('class="model-grid"', recent)
        self.assertIn('class="model-card researcher-card"', recent)
        self.assertIn('sort=joined', recent)
        self.assertIn('data-directory-total="2"', recent)
        filtered = self.client.get('/users?sort=joined&role=Professor').get_data(as_text=True)
        self.assertIn('href="/user/alice"', filtered)
        self.assertNotIn('href="/user/bob"', filtered)
        self.assertIn('role=Professor&amp;sort=joined', filtered)

    def test_pagination_preserves_search_and_handles_invalid_pages(self):
        self.session.add_all(User(username=f'researcher{i:02}', google_sub=f'sub{i}',
                                  name=f'Researcher {i:02}', research_interests='Climate science')
                             for i in range(25))
        self.session.commit()
        first = self.client.get('/users?q=climate').get_data(as_text=True)
        second = self.client.get('/users?q=climate&page=2').get_data(as_text=True)
        self.assertIn('Page 1 of 2', first)
        self.assertIn('q=climate&amp;page=2', first)
        self.assertIn('Page 2 of 2', second)
        self.assertIn('href="/user/researcher24"', second)
        self.assertNotIn('href="/user/researcher00"', second)
        for page in ('-1', 'invalid', '99999'):
            self.assertEqual(self.client.get('/users', query_string={'page': page}).status_code, 200)
