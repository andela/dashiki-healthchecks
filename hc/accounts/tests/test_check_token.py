from hc.test import BaseTestCase
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from hc.accounts.models import User, Profile
import uuid
from django.utils.html import strip_tags


class CheckTokenTestCase(BaseTestCase):

    def setUp(self):
        super(CheckTokenTestCase, self).setUp()
        self.profile.token = make_password("secret-token")
        self.profile.save()

    def test_it_shows_form(self):
        r = self.client.get("/accounts/check_token/alice/secret-token/")
        self.assertContains(r, "You are about to log in")

    def test_it_redirects(self):
        r = self.client.post("/accounts/check_token/alice/secret-token/")
        self.assertRedirects(r, "/checks/")

        # After login, token should be blank
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.token, "")

    # Login and test it redirects already logged in
    def test_login_redirects(self):
        # Create test user
        user = User(username="test", email="test@gmail.com")
        user.set_password("password123")
        user.save()

        # Login test user with valid credentials
        self.client.login(username="test@gmail.com", password="password123")
        response = self.client.get("/")
        self.assertRedirects(response, "/checks/")

    # Login with a bad token and check that it redirects
    def test_login_with_bad_token(self):
        user = User(username='test', email='test@gmail.com')
        user.set_password("password123")
        user.save()

        # Create profile instance
        profile = Profile(user=user)
        correct_token, wrong_token = str(uuid.uuid4()), str(uuid.uuid4())
        profile.token = make_password(correct_token)

        params = {
            "username": user.username,
            "token": wrong_token
        }

        uri = reverse("hc-check-token", args=[user.username, wrong_token])

        # Try logging in with wrong token
        response = self.client.post(uri, params)
        self.assertRedirects(response, '/accounts/login/')
    # Any other tests?

    def test_content_login_bad_token(self):
        user = User(username="demo", email="demo@andela.com")
        user.set_password("demo123456")
        user.save()

#         create profile of user instance
        profile = Profile(user=user)
        correct, wrong = str(uuid.uuid4()), str(uuid.uuid4())
        profile.token = make_password(correct)

        uri = reverse("hc-check-token", args=[user.username, wrong])
        response = self.client.post(uri, {"username": user.username, "token": wrong}, follow=True)
        self.assertTrue("incorrect login link" in strip_tags(response.content).lower())

    def test_correct_login_content(self):
        user = User(username="lorem", email="lorem@ipsum.org")
        user.set_password("lorem123456")
        user.save()

        # Login test user with valid credentials
        self.client.login(username="lorem@ipsum.org", password="lorem123456")
        response = self.client.get("/", follow=True)
        content = strip_tags(response.content).lower()

#         confirm dashboard
        self.assertTrue(user.email in content and 'account settings' in content and 'log out' in content)

