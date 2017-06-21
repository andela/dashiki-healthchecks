from django.conf import settings
from django.core.signing import base64_hmac

from hc.api.models import Check
from hc.test import BaseTestCase


class BadgeTestCase(BaseTestCase):

    def setUp(self):
        super(BadgeTestCase, self).setUp()
        self.check = Check.objects.create(user=self.alice, tags="foo bar")

    def test_it_rejects_bad_signature(self):
        response = self.client.get("/badge/%s/12345678/foo.svg" % self.alice.username)
        # Assert the expected response status code
        self.assertEqual(response.status_code, 400)

    def test_it_returns_svg(self):
        signature = base64_hmac(str(self.alice.username), "foo", settings.SECRET_KEY)
        signature = signature[:8].decode("utf-8")
        url = "/badge/%s/%s/foo.svg" % (self.alice.username, signature)

        response = self.client.get(url)
        # Assert that the svg is returned
        self.assertEqual(response.status_code, 200)
        self.assertIn('foo', response.content.decode('utf-8'))
