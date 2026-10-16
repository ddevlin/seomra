from django.urls import reverse
from inertia.test import InertiaTestCase

from accounts.models import Role, User


class SwitchRoleTests(InertiaTestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user("a@example.com")

    def test_switch_toggles_role_and_redirects_back(self):
        self.inertia.force_login(self.user)
        response = self.inertia.post(reverse("accounts:switch_role"), HTTP_REFERER="http://testserver/bookings/")
        self.assertRedirects(response, "http://testserver/bookings/", fetch_redirect_response=False)
        self.assertEqual(User.objects.get(pk=self.user.pk).role, Role.MANAGER)
        self.inertia.post(reverse("accounts:switch_role"))
        self.assertEqual(User.objects.get(pk=self.user.pk).role, Role.USER)

    def test_external_referer_falls_back_to_home(self):
        self.inertia.force_login(self.user)
        response = self.inertia.post(reverse("accounts:switch_role"), HTTP_REFERER="https://evil.example/x")
        self.assertRedirects(response, "/", fetch_redirect_response=False)

    def test_switch_requires_post(self):
        self.inertia.force_login(self.user)
        self.assertEqual(self.inertia.get(reverse("accounts:switch_role")).status_code, 405)

    def test_switch_requires_login(self):
        response = self.inertia.post(reverse("accounts:switch_role"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith(reverse("accounts:login")))

    def test_shared_auth_reflects_role(self):
        self.inertia.force_login(self.user)
        self.inertia.get(reverse("accounts:login_sent"))
        self.assertEqual(self.props()["auth"]["user"]["role"], "user")


class SwitchRoleFromManagerPageTests(InertiaTestCase):
    """Demoting yourself while on a manager-only page must not bounce you into a 403."""

    def setUp(self):
        super().setUp()
        self.manager = User.objects.create_user("m@example.com", role=Role.MANAGER)
        self.inertia.force_login(self.manager)

    def test_demotion_on_manager_only_page_goes_to_rooms_index(self):
        response = self.inertia.post(reverse("accounts:switch_role"), HTTP_REFERER="http://testserver/rooms/new")
        self.assertRedirects(response, reverse("rooms:index"), fetch_redirect_response=False)
        self.assertEqual(User.objects.get(pk=self.manager.pk).role, Role.USER)

    def test_demotion_on_ordinary_page_returns_there(self):
        response = self.inertia.post(reverse("accounts:switch_role"), HTTP_REFERER="http://testserver/bookings/?date=2030-01-07")
        self.assertRedirects(response, "http://testserver/bookings/?date=2030-01-07", fetch_redirect_response=False)

    def test_promotion_on_any_page_returns_there(self):
        self.manager.role = Role.USER
        self.manager.save()
        response = self.inertia.post(reverse("accounts:switch_role"), HTTP_REFERER="http://testserver/rooms/1/?week=2030-01-07")
        self.assertRedirects(response, "http://testserver/rooms/1/?week=2030-01-07", fetch_redirect_response=False)
