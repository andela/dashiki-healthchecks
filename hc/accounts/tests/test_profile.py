from hc.test import BaseTestCase
from hc.accounts.models import Member
from hc.api.models import Check

from django.core import mail


class ProfileTestCase(BaseTestCase):

    def test_it_sends_set_password_link(self):
        self.client.login(username="alice@example.org", password="password")

        initial_mail_count = len(mail.outbox)

        form = {"set_password": "1"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 302

        # profile.token should be set now
        self.alice.profile.refresh_from_db()
        token = self.alice.profile.token
        # Assert that the token is set
        self.assertTrue(token is not None)
        self.assertTrue(len(token) > 0)

        # Assert that the email was sent and check email content
        self.assertEqual(len(mail.outbox) - initial_mail_count, 1)
        self.assertEqual(mail.outbox[0].subject, "Set password on healthchecks.io")
        self.assertTrue("link to set a password for your account"
                        " on healthchecks".lower() in mail.outbox[0].body.lower())

    def test_it_sends_report(self):
        initial_mail_count = len(mail.outbox)

        check = Check(name="Test Check", user=self.alice)
        check.save()

        self.alice.profile.send_report()

        # Assert that the email was sent and check email content
        self.assertEqual(len(mail.outbox) - initial_mail_count, 1)
        self.assertEqual(mail.outbox[len(mail.outbox) - 1].subject, "Monthly Report")
        self.assertTrue("this is a monthly report sent"
                        " by healthchecks.io" in mail.outbox[len(mail.outbox) - 1].body.lower())

    def test_it_adds_team_member(self):
        self.client.login(username="alice@example.org", password="password")

        initial_outbox_count = len(mail.outbox)

        form = {"invite_team_member": "1", "email": "frank@example.org"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 200

        member_emails = set()
        for member in self.alice.profile.member_set.all():
            member_emails.add(member.user.email)

        # Assert the existence of the member emails
        self.assertEqual(len(member_emails), len(self.alice.profile.member_set.all()))

        self.assertTrue("frank@example.org" in member_emails)

        # Assert that the email was sent and check email content
        self.assertEqual(len(mail.outbox) - initial_outbox_count, 1)
        self.assertEqual(mail.outbox[len(mail.outbox) - 1].subject, "You have been invited to"
                                                                    " join alice@example.org on healthchecks.io")
        self.assertTrue("alice@example.org invites you to their "
                        "healthchecks.io account" in mail.outbox[len(mail.outbox) - 1].body.lower())

    def test_add_team_member_checks_team_access_allowed_flag(self):
        self.client.login(username="charlie@example.org", password="password")

        form = {"invite_team_member": "1", "email": "frank@example.org"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 403

    def test_it_removes_team_member(self):
        self.client.login(username="alice@example.org", password="password")

        form = {"remove_team_member": "1", "email": "bob@example.org"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 200

        self.assertEqual(Member.objects.count(), 0)

        self.bobs_profile.refresh_from_db()
        self.assertEqual(self.bobs_profile.current_team, None)

    def test_it_sets_team_name(self):
        self.client.login(username="alice@example.org", password="password")

        form = {"set_team_name": "1", "team_name": "Alpha Team"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 200

        self.alice.profile.refresh_from_db()
        self.assertEqual(self.alice.profile.team_name, "Alpha Team")

    def test_set_team_name_checks_team_access_allowed_flag(self):
        self.client.login(username="charlie@example.org", password="password")

        form = {"set_team_name": "1", "team_name": "Charlies Team"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 403

    def test_it_switches_to_own_team(self):
        self.client.login(username="bob@example.org", password="password")

        self.client.get("/accounts/profile/")

        # After visiting the profile page, team should be switched back
        # to user's default team.
        self.bobs_profile.refresh_from_db()
        self.assertEqual(self.bobs_profile.current_team, self.bobs_profile)

    def test_it_shows_badges(self):
        self.client.login(username="alice@example.org", password="password")
        Check.objects.create(user=self.alice, tags="foo a-B_1  baz@")
        Check.objects.create(user=self.bob, tags="bobs-tag")

        r = self.client.get("/accounts/profile/")
        self.assertContains(r, "foo.svg")
        self.assertContains(r, "a-B_1.svg")

        # Expect badge URLs only for tags that match \w+
        self.assertNotContains(r, "baz@.svg")

        # Expect only Alice's tags
        self.assertNotContains(r, "bobs-tag.svg")

    # Test it creates and revokes API key
