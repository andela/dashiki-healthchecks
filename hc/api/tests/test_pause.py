from hc.api.models import Check
from hc.test import BaseTestCase


class PauseTestCase(BaseTestCase):

    def test_it_works(self):
        check = Check(user=self.alice, status="up")
        check.save()

        url = "/api/v1/checks/%s/pause" % check.code
        response = self.client.post(url, "", content_type="application/json",
                                    HTTP_X_API_KEY="abc")

        # Assert the expected status code and check's status
        self.assertEqual(response.status_code, 200)

    def test_it_validates_ownership(self):
        check = Check(user=self.bob, status="up")
        check.save()

        url = "/api/v1/checks/%s/pause" % check.code
        response = self.client.post(url, "", content_type="application/json", HTTP_X_API_KEY="abc")

        self.assertEqual(response.status_code, 400)

        # Test that it only allows post requests
        response = self.client.get(url, "", content_type="application/json", HTTP_X_API_KEY="abc")

        self.assertEqual(response.status_code, 405)
