from hc.api.models import Channel, Check
from hc.settings import SITE_ROOT
from hc.test import BaseTestCase

ENDPOINT_URL = SITE_ROOT + "/api/v1/channels/"


class ApiAdminTestCase(BaseTestCase):

    def setUp(self):
        super(ApiAdminTestCase, self).setUp()
        self.check = Check.objects.create(user=self.alice, tags="foo bar")

        # Set Alice to be staff and superuser and save her :)
        self.alice.is_staff = True
        self.alice.is_superuser = True
        self.alice.save()

    def test_it_shows_channel_list_with_pushbullet(self):
        self.client.login(username="alice@example.org", password="password")
        channel = Channel(user=self.alice, kind="pushbullet", value="test-token")
        channel.save()

        # Assert for the push bullet
        response = self.client.get("{0}?kind={1}".format(ENDPOINT_URL, channel.kind))
        result = response.data.get("results")[0]
        actual = [result.get("user"), result.get("kind"), result.get("value")]
        expected = [channel.user.id, channel.kind, channel.value]

        self.assertEqual(response.status_code, 200)
        self.assertListEqual(actual, expected)
