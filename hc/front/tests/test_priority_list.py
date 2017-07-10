from hc.test import BaseTestCase

from hc.api.models import Check, Priority

PRIORITY_LEVELS_DICT = {
    "high": 1,
    "medium": 2,
    "low": 3,
    "none": 0
}


class PriorityListTestCase(BaseTestCase):
    def setUp(self):
        super(PriorityListTestCase, self).setUp()
        self.client.login(username="alice@example.org", password="password")
        self.check = Check(user=self.alice, name="Alice Was Here")
        self.check.save()

    def test_renders_priority_list_page_for_a_particular_check(self):
        response = self.client.get("/checks/{}/priority/".format(self.check.code))

        self.assertContains(response, "alice@example.org", status_code=200)

    def test_creates_priority_object_for_a_user(self):
        payload = {self.alice.id: PRIORITY_LEVELS_DICT.get("high")}
        response = self.client.post("/checks/{}/priority/".format(self.check.code), data=payload)

        self.assertRedirects(response, "/checks/", 302)
        self.assertEqual(Priority.objects.count(), 1)

    def test_update_of_priority_object_for_a_user(self):
        priority = Priority(user=self.alice, current_check=self.check, level=PRIORITY_LEVELS_DICT.get("high"))
        priority.save()

        payload = {self.alice.id: PRIORITY_LEVELS_DICT.get("medium")}
        response = self.client.post("/checks/{}/priority/".format(self.check.code), data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Priority.objects.first().level, PRIORITY_LEVELS_DICT.get("medium"))
