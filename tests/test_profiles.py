import unittest
from unittest.mock import patch
from werkzeug.datastructures import MultiDict

from backend.app import app
from backend.app.db_models import User


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.user = User(username='researcher', google_sub='example-sub',
                         name='Example Researcher', email='private@example.org',
                         research_interests=' Vision, , Climate , ', bio='A research biography.')

    def test_profile_redirects_to_shared_page(self):
        with self.client.session_transaction() as session:
            session['username'] = self.user.username
        with patch('backend.app.users.db.session.get', return_value=self.user):
            response = self.client.get('/profile')
            owner = self.client.get('/user/researcher').get_data(as_text=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/user/researcher')
        for text in ('Example Researcher', 'A research biography.', '<li>Vision</li>', '<li>Climate</li>', 'Edit profile', 'private@example.org'):
            self.assertIn(text, owner)
        self.assertNotIn('View public profile', owner)

    def test_visitors_and_other_users_cannot_see_owner_controls(self):
        for username in (None, 'other_researcher'):
            with self.subTest(username=username):
                with self.client.session_transaction() as session:
                    session.clear()
                    if username:
                        session['username'] = username
                with patch('backend.app.users.db.session.get', return_value=self.user):
                    response = self.client.get('/user/researcher')
                self.assertEqual(response.status_code, 200)
                html = response.get_data(as_text=True)
                self.assertIn('A research biography.', html)
                for text in ('Edit profile', 'View public profile', 'private@example.org'):
                    self.assertNotIn(text, html)

    def test_empty_profile_prompts_depend_on_ownership(self):
        self.user.bio = None
        self.user.research_interests = None
        with self.client.session_transaction() as session:
            session['username'] = self.user.username
        with patch('backend.app.users.db.session.get', return_value=self.user):
            owner = self.client.get('/user/researcher').get_data(as_text=True)
            with self.client.session_transaction() as session:
                session.clear()
            public = self.client.get('/user/researcher').get_data(as_text=True)
        self.assertIn('Add an introduction', owner)
        self.assertIn('Add research interests', owner)
        self.assertIn('This researcher hasn’t added an introduction yet.', public)
        self.assertIn('No research interests added yet.', public)
        self.assertNotIn('Add an introduction', public)

    def sign_in_for_edit(self):
        with self.client.session_transaction() as session:
            session['username'] = self.user.username

    def test_profile_choice_form_preselects_saved_values(self):
        self.sign_in_for_edit()
        self.user.institution = 'University of Michigan'
        self.user.research_interests = 'Machine learning, Public health'
        with patch('backend.app.users.db.session.get', return_value=self.user):
            response = self.client.get('/setup-profile?edit=1')
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('University affiliation', html)
        self.assertIn('value="University of Michigan" selected', html)
        self.assertIn('value="Machine learning" checked', html)
        self.assertIn('value="Public health" checked', html)
        self.assertNotIn('Separate interests with commas', html)

    def test_saves_multiple_interests_and_affiliation(self):
        self.sign_in_for_edit()
        data = MultiDict([('username', 'researcher'), ('name', 'Example Researcher'),
                          ('institution', 'University of Michigan'),
                          ('research_interests', 'Machine learning'),
                          ('research_interests', 'Public health'),
                          ('research_interests', 'Machine learning')])
        with patch('backend.app.users.db.session.get', return_value=self.user), \
                patch('backend.app.users.db.session.add'), \
                patch('backend.app.users.db.session.commit') as commit:
            response = self.client.post('/setup-profile?edit=1', data=data)
        self.assertEqual(response.status_code, 302)
        commit.assert_called_once()
        self.assertEqual(self.user.institution, 'University of Michigan')
        self.assertEqual(self.user.interest_list, ['Machine learning', 'Public health'])
        with patch('backend.app.users.db.session.get', return_value=self.user):
            html = self.client.get('/user/researcher').get_data(as_text=True)
        self.assertIn('University affiliation', html)
        self.assertIn('University of Michigan', html)
        self.assertIn('<li>Machine learning</li>', html)

    def test_rejects_values_outside_profile_choices(self):
        self.sign_in_for_edit()
        for invalid in ({'institution': 'Other university'}, {'research_interests': 'Invalid, topic'}):
            with self.subTest(invalid=invalid), \
                    patch('backend.app.users.db.session.get', return_value=self.user), \
                    patch('backend.app.users.db.session.commit') as commit:
                response = self.client.post('/setup-profile', data={
                    'username': 'researcher', 'name': 'Example Researcher', **invalid})
                self.assertEqual(response.status_code, 400)
                commit.assert_not_called()
                self.assertIn('profile-error', response.get_data(as_text=True))

    def test_custom_interests_are_saved_and_restored(self):
        self.sign_in_for_edit()
        data = MultiDict([('username', 'researcher'), ('name', 'Example Researcher'),
                          ('research_interests', 'machine learning'),
                          ('research_interests', 'Digital humanities'),
                          ('research_interests', 'DIGITAL HUMANITIES'),
                          ('custom_interest', 'Urban planning')])
        with patch('backend.app.users.db.session.get', return_value=self.user), \
                patch('backend.app.users.db.session.add'), \
                patch('backend.app.users.db.session.commit'):
            response = self.client.post('/setup-profile', data=data)
            edit = self.client.get('/setup-profile').get_data(as_text=True)
            public = self.client.get('/user/researcher').get_data(as_text=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.interest_list, ['Machine learning', 'Digital humanities', 'Urban planning'])
        self.assertIn('value="Digital humanities" checked', edit)
        self.assertIn('research-interest-data', edit)
        self.assertIn('<li>Urban planning</li>', public)

    def test_rejects_oversized_custom_interest(self):
        self.sign_in_for_edit()
        with patch('backend.app.users.db.session.get', return_value=self.user), \
                patch('backend.app.users.db.session.commit') as commit:
            response = self.client.post('/setup-profile', data={
                'username': 'researcher', 'name': 'Example Researcher', 'custom_interest': 'x' * 81})
        self.assertEqual(response.status_code, 400)
        commit.assert_not_called()

    def test_optional_choices_can_be_cleared(self):
        self.sign_in_for_edit()
        with patch('backend.app.users.db.session.get', return_value=self.user), \
                patch('backend.app.users.db.session.add'), \
                patch('backend.app.users.db.session.commit'):
            response = self.client.post('/setup-profile', data={
                'username': 'researcher', 'name': 'Example Researcher'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.institution, '')
        self.assertEqual(self.user.interest_list, [])

    def test_google_picture_is_refreshed_on_login(self):
        self.client.set_cookie('g_csrf_token', 'csrf')
        picture = 'https://lh3.googleusercontent.com/a/example-photo'
        with patch('backend.app.auth.id_token.verify_oauth2_token', return_value={
                'sub': 'example-sub', 'picture': picture}), \
                patch('backend.app.auth.db.session.execute') as execute, \
                patch('backend.app.auth.db.session.commit') as commit:
            execute.return_value.scalar_one_or_none.return_value = self.user
            response = self.client.post('/auth/google', data={'g_csrf_token': 'csrf', 'credential': 'token'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.picture_url, picture)
        commit.assert_called_once()
        with patch('backend.app.users.db.session.get', return_value=self.user):
            html = self.client.get('/user/researcher').get_data(as_text=True)
        self.assertIn('data-profile-picture', html)
        self.assertIn(picture, html)
        self.assertIn('<span>E</span>', html)

    def test_new_google_accounts_keep_picture_during_setup(self):
        self.client.set_cookie('g_csrf_token', 'csrf')
        picture = 'https://lh3.googleusercontent.com/a/new-photo'
        with patch('backend.app.auth.id_token.verify_oauth2_token', return_value={
                'sub': 'new-sub', 'name': 'New Researcher', 'picture': picture}), \
                patch('backend.app.auth.db.session.execute') as execute:
            execute.return_value.scalar_one_or_none.return_value = None
            response = self.client.post('/auth/google', data={'g_csrf_token': 'csrf', 'credential': 'token'})
        self.assertEqual(response.headers['Location'], '/setup-profile')
        with self.client.session_transaction() as session:
            self.assertEqual(session['pending_user']['picture_url'], picture)
        with patch('backend.app.users.db.session.execute') as execute:
            execute.return_value.scalar_one_or_none.return_value = None
            html = self.client.get('/setup-profile').get_data(as_text=True)
        self.assertIn(picture, html)

    def test_missing_or_unsafe_picture_uses_initials(self):
        for picture in (None, '', 'javascript:alert(1)', 'http://example.org/photo.png'):
            with self.subTest(picture=picture):
                self.user.picture_url = picture
                with patch('backend.app.users.db.session.get', return_value=self.user):
                    html = self.client.get('/user/researcher').get_data(as_text=True)
                self.assertNotIn('data-profile-picture', html)
                self.assertIn('<span>E</span>', html)

    def test_existing_account_login_sets_session(self):
        self.client.set_cookie('g_csrf_token', 'csrf')
        with patch('backend.app.auth.id_token.verify_oauth2_token', return_value={'sub': 'example-sub'}), \
                patch('backend.app.auth.db.session.execute') as execute:
            execute.return_value.scalar_one_or_none.return_value = self.user
            response = self.client.post('/auth/google', data={'g_csrf_token': 'csrf', 'credential': 'token'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/')
        with self.client.session_transaction() as session:
            self.assertEqual(session['username'], 'researcher')
            self.assertEqual(session['email'], 'private@example.org')
            self.assertNotIn('pending_user', session)

    def test_setup_in_another_tab_completes_pending_session(self):
        with self.client.session_transaction() as session:
            session['pending_user'] = {'google_sub': 'example-sub', 'email': 'private@example.org'}
        with patch('backend.app.users.db.session.execute') as execute:
            execute.return_value.scalar_one_or_none.return_value = self.user
            response = self.client.get('/setup-profile')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/profile')
        with self.client.session_transaction() as session:
            self.assertEqual(session['username'], 'researcher')
            self.assertEqual(session['email'], 'private@example.org')
            self.assertNotIn('pending_user', session)
