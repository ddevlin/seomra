import json
from datetime import timedelta

from django.core import mail
from django.urls import reverse
from django.utils import timezone
from inertia.test import InertiaTestCase

from accounts.models import MAGIC_LINK_TTL, MagicLink, User


class LoginPageTests(InertiaTestCase):
    def test_login_page_renders(self):
        self.inertia.get(reverse("accounts:login"))
        self.assertComponentUsed("Auth/Login")

    def test_authenticated_user_is_sent_to_rooms(self):
        self.inertia.force_login(User.objects.create_user("a@example.com"))
        response = self.inertia.get(reverse("accounts:login"))
        self.assertRedirects(response, reverse("rooms:index"), fetch_redirect_response=False)

    def test_posting_email_creates_user_link_and_emails_it(self):
        response = self.inertia.post(reverse("accounts:login"), {"email": " Alice@Example.COM "})
        self.assertRedirects(response, reverse("accounts:login_sent"), fetch_redirect_response=False)
        user = User.objects.get(email="alice@example.com")
        link = MagicLink.objects.get(user=user)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(reverse("accounts:login_verify", args=[link.token]), mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, ["alice@example.com"])

    def test_json_body_is_accepted_like_the_inertia_client_sends(self):
        response = self.inertia.post(
            reverse("accounts:login"), json.dumps({"email": "json@example.com"}), content_type="application/json"
        )
        self.assertRedirects(response, reverse("accounts:login_sent"), fetch_redirect_response=False)
        self.assertTrue(User.objects.filter(email="json@example.com").exists())

    def test_posting_same_email_twice_reuses_user(self):
        self.inertia.post(reverse("accounts:login"), {"email": "a@example.com"})
        self.inertia.post(reverse("accounts:login"), {"email": "A@EXAMPLE.com"})
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(MagicLink.objects.count(), 2)

    def test_invalid_email_rerenders_with_error(self):
        self.inertia.post(reverse("accounts:login"), {"email": "not-an-email"})
        self.assertComponentUsed("Auth/Login")
        self.assertIn("email", self.props()["errors"])
        self.assertEqual(User.objects.count(), 0)

    def test_sent_page_renders(self):
        self.inertia.get(reverse("accounts:login_sent"))
        self.assertComponentUsed("Auth/Sent")


class LoginVerifyTests(InertiaTestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user("a@example.com")
        self.link = MagicLink.objects.create(user=self.user)

    def verify(self, token):
        return self.client.get(reverse("accounts:login_verify", args=[token]))

    def test_valid_link_logs_in_and_is_consumed(self):
        response = self.verify(self.link.token)
        self.assertRedirects(response, reverse("rooms:index"), fetch_redirect_response=False)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)
        self.assertIsNotNone(MagicLink.objects.get(pk=self.link.pk).used_at)

    def test_used_link_is_rejected(self):
        self.verify(self.link.token)
        self.client.logout()
        response = self.verify(self.link.token)
        self.assertRedirects(response, reverse("accounts:login"), fetch_redirect_response=False)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_expired_link_is_rejected(self):
        MagicLink.objects.filter(pk=self.link.pk).update(
            created_at=timezone.now() - MAGIC_LINK_TTL - timedelta(seconds=1)
        )
        response = self.verify(self.link.token)
        self.assertRedirects(response, reverse("accounts:login"), fetch_redirect_response=False)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_unknown_token_is_rejected(self):
        response = self.verify("nope")
        self.assertRedirects(response, reverse("accounts:login"), fetch_redirect_response=False)

    def test_rejection_shows_flash_message_on_login_page(self):
        self.inertia.get(reverse("accounts:login_verify", args=["nope"]))
        self.inertia.get(reverse("accounts:login"))
        levels = [m["level_tag"] for m in self.props()["messages"]]
        self.assertIn("error", levels)


class LogoutTests(InertiaTestCase):
    def test_logout_requires_post_and_clears_session(self):
        user = User.objects.create_user("a@example.com")
        self.inertia.force_login(user)
        self.assertEqual(self.inertia.get(reverse("accounts:logout")).status_code, 405)
        response = self.inertia.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:login"), fetch_redirect_response=False)
        self.assertNotIn("_auth_user_id", self.inertia.session)


class SharedPropsTests(InertiaTestCase):
    def test_anonymous_shared_auth_is_null(self):
        self.inertia.get(reverse("accounts:login"))
        self.assertIsNone(self.props()["auth"]["user"])

    def test_signed_in_shared_auth_describes_user(self):
        user = User.objects.create_user("a@example.com")
        self.inertia.force_login(user)
        self.inertia.get(reverse("accounts:login_sent"))
        self.assertEqual(self.props()["auth"]["user"], user.to_dict())

    def test_protected_page_redirects_anonymous_to_login(self):
        response = self.inertia.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith(reverse("accounts:login")))

    def test_home_redirects_signed_in_user_to_rooms(self):
        self.inertia.force_login(User.objects.create_user("a@example.com"))
        response = self.inertia.get("/")
        self.assertRedirects(response, reverse("rooms:index"), fetch_redirect_response=False)
