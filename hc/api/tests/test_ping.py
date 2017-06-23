from django.test import TestCase

from hc.api.models import Check, Ping


class PingTestCase(TestCase):

    def setUp(self):
        super(PingTestCase, self).setUp()
        self.check = Check.objects.create()

    def test_it_works(self):
        response = self.client.get("/ping/%s/" % self.check.code)
        assert response.status_code == 200

        self.check.refresh_from_db()
        assert self.check.status == "up"

        ping = Ping.objects.latest("id")
        assert ping.scheme == "http"

    def test_it_handles_bad_uuid(self):
        response = self.client.get("/ping/not-uuid/")
        assert response.status_code == 400

    def test_it_handles_120_char_ua(self):
        ua = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/44.0.2403.89 Safari/537.36")

        response = self.client.get("/ping/%s/" % self.check.code, HTTP_USER_AGENT=ua)
        assert response.status_code == 200

        ping = Ping.objects.latest("id")
        assert ping.ua == ua

    def test_it_truncates_long_ua(self):
        ua = "01234567890" * 30

        response = self.client.get("/ping/%s/" % self.check.code, HTTP_USER_AGENT=ua)
        assert response.status_code == 200

        ping = Ping.objects.latest("id")
        assert len(ping.ua) == 200
        assert ua.startswith(ping.ua)

    def test_it_reads_forwarded_ip(self):
        ip = "1.1.1.1"
        self.client.get("/ping/%s/" % self.check.code, HTTP_X_FORWARDED_FOR=ip)
        ping = Ping.objects.latest("id")
        # Assert the expected response status code and ping's remote address
        assert ping.remote_addr == ip

        ip = "1.1.1.1, 2.2.2.2"
        response = self.client.get("/ping/%s/" % self.check.code, HTTP_X_FORWARDED_FOR=ip,
                                   REMOTE_ADDR="3.3.3.3")
        ping = Ping.objects.latest("id")
        assert response.status_code == 200
        assert ping.remote_addr == "1.1.1.1"

    def test_it_reads_forwarded_protocol(self):
        self.client.get("/ping/%s/" % self.check.code, HTTP_X_FORWARDED_PROTO="https")
        ping = Ping.objects.latest("id")
        # Assert the expected response status code and ping's scheme
        assert ping.scheme == "https"

    def test_it_never_caches(self):
        response = self.client.get("/ping/%s/" % self.check.code)
        assert "no-cache" in response.get("Cache-Control")

    # Test that when a ping is made a check with a paused status changes status
    def test_a_ping_changes_status_of_paused_check_to_up(self):
        self.check.status = "paused"
        self.check.save()
        self.check.refresh_from_db()

        self.client.get("/ping/%s/" % self.check.code)
        self.check.refresh_from_db()
        assert self.check.status == "up"

    # Test that a post to a ping works
    def test_a_post_request_to_a_ping_works(self):
        response = self.client.post("/ping/%s/" % self.check.code)

        assert response.status_code == 200

    # Test that the csrf_client head works
    def test_that_the_csrf_client_head_works(self):
        response = self.client.get("http://example/ping/%s/" % self.check.code)

        assert response.status_code == 200
