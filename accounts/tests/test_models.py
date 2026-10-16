from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from accounts.models import MAGIC_LINK_TTL, MagicLink, Role, User


class UserModelTests(TestCase):
    def test_create_user_normalises_email_and_defaults_to_user_role(self):
        user = User.objects.create_user("  Alice@Example.COM ")
        self.assertEqual(user.email, "alice@example.com")
        self.assertEqual(user.role, Role.USER)
        self.assertFalse(user.is_manager)
        self.assertFalse(user.has_usable_password())

    def test_toggle_role_flips_between_user_and_manager(self):
        user = User.objects.create_user("a@example.com")
        user.toggle_role()
        self.assertTrue(User.objects.get(pk=user.pk).is_manager)
        user.toggle_role()
        self.assertFalse(User.objects.get(pk=user.pk).is_manager)

    def test_to_dict_exposes_role_fields(self):
        user = User.objects.create_user("a@example.com", role=Role.MANAGER)
        self.assertEqual(
            user.to_dict(),
            {"id": user.id, "email": "a@example.com", "role": "manager", "is_manager": True},
        )


class MagicLinkTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("a@example.com")

    def test_new_link_has_token_and_is_valid(self):
        link = MagicLink.objects.create(user=self.user)
        self.assertGreaterEqual(len(link.token), 32)
        self.assertTrue(link.is_valid)

    def test_consumed_link_is_invalid(self):
        link = MagicLink.objects.create(user=self.user)
        link.consume()
        self.assertFalse(MagicLink.objects.get(pk=link.pk).is_valid)

    def test_expired_link_is_invalid(self):
        link = MagicLink.objects.create(user=self.user)
        MagicLink.objects.filter(pk=link.pk).update(
            created_at=timezone.now() - MAGIC_LINK_TTL - timedelta(seconds=1)
        )
        self.assertFalse(MagicLink.objects.get(pk=link.pk).is_valid)
