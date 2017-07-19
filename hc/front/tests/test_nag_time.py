from datetime import timedelta
from django.utils import timezone

from hc.api.management.commands.sendalerts import Command
from hc.test import BaseTestCase
from hc.api.models import Check
from mock import patch


class NagTestCase(BaseTestCase):
    def setUp(self):
        super(NagTestCase, self).setUp()
        self.client.login(username="alice@example.org", password="password")
        self.check = Check(user=self.alice, name="Alice Was Here")
        self.check.status = "down"
        self.check.last_ping = timezone.now() - timedelta(days=2, minutes=30)
        self.check.save()

    @patch("hc.api.management.commands.sendalerts.Command.handle_one")
    def test_nag_alerts_sent(self, mock_handle):
        self.check.nag_time = timedelta(minutes=30)
        result = Command().handle_one(self.check)
        assert result, "handle_one returns True"

    def test_adds_nag_time_to_check(self):
        payload = {"nag_time": 1200}
        response = self.client.post("/checks/{}/nag_time/".format(self.check.code), data=payload)
        self.check.refresh_from_db()

        self.assertRedirects(response, "/checks/", 302)
        self.assertEqual(self.check.nag_time, timedelta(minutes=20))

    def test_removes_nag_time(self):
        self.check.nag_time = timedelta(minutes=45)
        self.check.save()
        response = self.client.post("/checks/{}/remove_nag_time/".format(self.check.code))
        self.check.refresh_from_db()
        self.assertRedirects(response, "/checks/", 302)
        self.assertEqual(self.check.nag_time, timedelta(hours=0))
