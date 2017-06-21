from hc.api.models import Check
from hc.test import BaseTestCase
from django.urls import reverse


class AddCheckTestCase(BaseTestCase):

    def test_it_works(self):
        url = "/checks/add/"
        self.client.login(username="alice@example.org", password="password")
        r = self.client.post(url)
        self.assertRedirects(r, "/checks/")
        assert Check.objects.count() == 1

    # Test that team access works
    def test_team_access_works(self):
        self.client.login(username="alice@example.org", password="password")
        self.check = Check(user=self.alice, name="Alice Was Here")
        self.check.save()
        self.client.logout()

        self.client.login(username="bob@example.org", password="password")
        r = self.client.get(reverse("hc-checks"))
        self.assertContains(r, "Alice Was Here", status_code=200)
