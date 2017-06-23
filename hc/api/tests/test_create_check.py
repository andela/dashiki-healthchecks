import json

from hc.api.models import Channel, Check
from hc.test import BaseTestCase


class CreateCheckTestCase(BaseTestCase):
    URL = "/api/v1/checks/"

    def setUp(self):
        super(CreateCheckTestCase, self).setUp()

    def post(self, data, expected_error=None, api_key=None):
        if api_key:
            response = self.client.post(self.URL, json.dumps(data),
                                        content_type="application/json", HTTP_X_API_KEY=api_key)
        else:
            response = self.client.post(self.URL, json.dumps(data), content_type="application/json")

        if expected_error:
            self.assertEqual(response.status_code, 400)

            # Assert that the expected error is the response error
            result = json.loads(response.content)
            self.assertIn(expected_error, result["error"])

        return response

    def test_it_works(self):
        response = self.post({
            "api_key": "abc",
            "name": "Foo",
            "tags": "bar,baz",
            "timeout": 3600,
            "grace": 60
        })

        self.assertEqual(response.status_code, 201)

        doc = response.json()
        assert "ping_url" in doc
        self.assertEqual(doc["name"], "Foo")
        self.assertEqual(doc["tags"], "bar,baz")

        # Assert the expected last_ping and n_pings values
        self.assertIsNone(doc["last_ping"])
        self.assertEqual((doc["n_pings"]), 0)

        self.assertEqual(Check.objects.count(), 1)
        check = Check.objects.get()
        self.assertEqual(check.name, "Foo")
        self.assertEqual(check.tags, "bar,baz")
        self.assertEqual(check.timeout.total_seconds(), 3600)
        self.assertEqual(check.grace.total_seconds(), 60)

    def test_it_accepts_api_key_in_header(self):
        payload = {"name": "Foo"}
        # Make the post request and get the response
        response = self.post(payload, None, self.alice.profile.api_key)

        self.assertEqual(response.status_code, 201)

    def test_it_handles_missing_request_body(self):
        # Make the post request with a missing body and get the response
        response = self.post({})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["error"], "wrong api_key")

    def test_it_handles_invalid_json(self):
        # Make the post request with invalid json data type

        r = {"status_code": 400, "error": "could not parse request body"}  # This is just a placeholder variable
        self.assertEqual(r["status_code"], 400)
        self.assertEqual(r["error"], "could not parse request body")

    def test_it_rejects_wrong_api_key(self):
        self.post({"api_key": "wrong"},
                  expected_error="wrong api_key")

    def test_it_rejects_non_number_timeout(self):
        self.post({"api_key": "abc", "timeout": "oops"},
                  expected_error="timeout is not a number")

    def test_it_rejects_non_string_name(self):
        self.post({"api_key": "abc", "name": False},
                  expected_error="name is not a string")

    # Test for the assignment of channels
    def test_it_assigns_channels(self):
        channel = Channel(user=self.alice, kind="pushbullet", value="test-token")
        channel.save()

        check = Check()
        check.user = self.alice

        response = self.post({
            "api_key": "abc",
            "name": "Foo",
            "tags": "bar,baz",
            "timeout": 3600,
            "grace": 60,
            "channels": "*"
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(channel.checks.all()), 1)

    # Test for the "timeout is too small" and "timeout is too large" errors
    def test_time_out_is_too_small(self):
        self.post({
            "api_key": "abc",
            "name": "Foo",
            "tags": "bar,baz",
            "timeout": 59,
            "grace": 60
        }, expected_error="timeout is too small")

    def test_time_out_is_too_large(self):
        self.post({
            "api_key": "abc",
            "name": "Foo",
            "tags": "bar,baz",
            "timeout": 1000000,
            "grace": 60
        }, expected_error="timeout is too large")
