from hc.test import BaseTestCase
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from hc.accounts.models import User, Profile
import uuid


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
