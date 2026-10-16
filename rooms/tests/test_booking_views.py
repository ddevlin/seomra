import json
from datetime import date, timedelta

from django.urls import reverse
from django.utils import timezone
from inertia.test import InertiaTestCase

from rooms.models import Booking
from seomra.testing import make_manager, make_room, make_user

FUTURE = date(2030, 1, 7)


class BookingFormTests(InertiaTestCase):
    def setUp(self):
        super().setUp()
        self.room = make_room()
        self.user = make_user()
        self.inertia.force_login(self.user)
        self.url = reverse("rooms:book", args=[self.room.id])

    def test_get_prefills_from_query(self):
        self.inertia.get(self.url + "?date=2030-01-07&hour=14")
        self.assertComponentUsed("Bookings/Form")
        props = self.props()
        self.assertEqual(props["room"]["id"], self.room.id)
        self.assertEqual(props["initial"], {"date": "2030-01-07", "start_hour": 14, "end_hour": 15, "title": ""})
        self.assertEqual(props["hours"], list(range(9, 17)))
        self.assertEqual(props["errors"], {})

    def test_garbage_query_falls_back_to_today_and_opening_hour(self):
        self.inertia.get(self.url + "?date=nope&hour=25")
        self.assertEqual(self.props()["initial"]["date"], timezone.localdate().isoformat())
        self.assertEqual(self.props()["initial"]["start_hour"], 9)
        self.inertia.get(self.url + "?hour=x")
        self.assertEqual(self.props()["initial"]["start_hour"], 9)

    def test_post_creates_booking_for_current_user(self):
        response = self.inertia.post(
            self.url, {"date": "2030-01-07", "start_hour": 10, "end_hour": 12, "title": "Sync"}
        )
        booking = Booking.objects.get()
        self.assertEqual(booking.user, self.user)
        self.assertEqual(
            (booking.room, booking.date, booking.start_hour, booking.end_hour, booking.title),
            (self.room, FUTURE, 10, 12, "Sync"),
        )
        self.assertRedirects(
            response,
            reverse("rooms:schedule", args=[self.room.id]) + "?week=2030-01-07",
            fetch_redirect_response=False,
        )

    def test_post_accepts_json_like_the_inertia_client(self):
        body = json.dumps({"date": "2030-01-07", "start_hour": 9, "end_hour": 10, "title": ""})
        response = self.inertia.post(self.url, body, content_type="application/json")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Booking.objects.count(), 1)

    def test_conflict_rerenders_with_error(self):
        other = make_user("other@example.com")
        Booking.objects.create(room=self.room, user=other, date=FUTURE, start_hour=10, end_hour=11)
        self.inertia.post(self.url, {"date": "2030-01-07", "start_hour": 10, "end_hour": 11})
        self.assertComponentUsed("Bookings/Form")
        self.assertIn("start_hour", self.props()["errors"])
        self.assertEqual(self.props()["initial"]["date"], "2030-01-07")
        self.assertEqual(Booking.objects.count(), 1)

    def test_invalid_hours_rerender_with_errors(self):
        self.inertia.post(self.url, {"date": "2030-01-07", "start_hour": 12, "end_hour": 12})
        self.assertIn("end_hour", self.props()["errors"])
        self.inertia.post(self.url, {"date": "2030-01-07", "start_hour": "abc", "end_hour": 12})
        self.assertIn("start_hour", self.props()["errors"])
        self.inertia.post(self.url, {"date": "2030-01-07", "start_hour": 8, "end_hour": 10})
        self.assertIn("start_hour", self.props()["errors"])
        self.inertia.post(self.url, {"date": "", "start_hour": 9, "end_hour": 10})
        self.assertIn("date", self.props()["errors"])
        self.assertEqual(Booking.objects.count(), 0)

    def test_requires_login(self):
        self.inertia.logout()
        self.assertEqual(self.inertia.get(self.url).status_code, 302)

    def test_unknown_room_is_404(self):
        self.assertEqual(self.inertia.get(reverse("rooms:book", args=[999])).status_code, 404)


class CancelBookingTests(InertiaTestCase):
    def setUp(self):
        super().setUp()
        self.room = make_room()
        self.owner = make_user("owner@example.com")
        self.booking = Booking.objects.create(room=self.room, user=self.owner, date=FUTURE, start_hour=9, end_hour=10)
        self.url = reverse("rooms:cancel", args=[self.booking.id])

    def test_owner_can_cancel_and_returns_to_referer(self):
        self.inertia.force_login(self.owner)
        response = self.inertia.delete(self.url, HTTP_REFERER="http://testserver/rooms/1/?week=2030-01-07")
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response["Location"], "http://testserver/rooms/1/?week=2030-01-07")
        self.assertEqual(Booking.objects.count(), 0)

    def test_without_referer_returns_to_overview(self):
        self.inertia.force_login(self.owner)
        response = self.inertia.delete(self.url)
        self.assertEqual(response["Location"], reverse("rooms:overview"))

    def test_other_user_is_forbidden(self):
        self.inertia.force_login(make_user("other@example.com"))
        self.assertEqual(self.inertia.delete(self.url).status_code, 403)
        self.assertEqual(Booking.objects.count(), 1)

    def test_manager_can_cancel_anyones(self):
        self.inertia.force_login(make_manager())
        self.inertia.delete(self.url)
        self.assertEqual(Booking.objects.count(), 0)

    def test_requires_delete_method(self):
        self.inertia.force_login(self.owner)
        self.assertEqual(self.inertia.post(self.url).status_code, 405)
        self.assertEqual(Booking.objects.count(), 1)

    def test_unknown_booking_is_404(self):
        self.inertia.force_login(self.owner)
        self.assertEqual(self.inertia.delete(reverse("rooms:cancel", args=[999])).status_code, 404)


class OverviewTests(InertiaTestCase):
    def setUp(self):
        super().setUp()
        self.alpha = make_room("Alpha")
        self.beta = make_room("Beta")
        self.user = make_user()
        self.other = make_user("other@example.com")
        self.inertia.force_login(self.user)

    def test_day_grid_and_my_upcoming_bookings(self):
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        Booking.objects.create(room=self.alpha, user=self.other, date=today, start_hour=9, end_hour=10, title="Other today")
        Booking.objects.create(room=self.beta, user=self.user, date=today, start_hour=11, end_hour=12, title="Mine today")
        Booking.objects.create(room=self.beta, user=self.user, date=tomorrow, start_hour=9, end_hour=10, title="Mine tomorrow")
        Booking.objects.create(room=self.beta, user=self.user, date=yesterday, start_hour=9, end_hour=10, title="Mine yesterday")
        self.inertia.get(reverse("rooms:overview"))
        self.assertComponentUsed("Bookings/Overview")
        props = self.props()
        self.assertEqual(props["date"], today.isoformat())
        self.assertEqual(props["today"], today.isoformat())
        self.assertEqual([r["name"] for r in props["rooms"]], ["Alpha", "Beta"])
        self.assertEqual(props["hours"], list(range(9, 17)))
        self.assertEqual(sorted(b["title"] for b in props["bookings"]), ["Mine today", "Other today"])
        self.assertEqual([b["title"] for b in props["my_bookings"]], ["Mine today", "Mine tomorrow"])
        self.assertTrue(all(b["can_cancel"] for b in props["my_bookings"]))
        self.assertEqual(props["prev_day"], yesterday.isoformat())
        self.assertEqual(props["next_day"], tomorrow.isoformat())

    def test_date_param_selects_day(self):
        Booking.objects.create(room=self.alpha, user=self.other, date=FUTURE, start_hour=9, end_hour=10, title="Far")
        self.inertia.get(reverse("rooms:overview") + "?date=2030-01-07")
        self.assertEqual(self.props()["date"], "2030-01-07")
        self.assertEqual([b["title"] for b in self.props()["bookings"]], ["Far"])

    def test_garbage_date_falls_back_to_today(self):
        response = self.inertia.get(reverse("rooms:overview") + "?date=2026-13-45")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.props()["date"], timezone.localdate().isoformat())

    def test_requires_login(self):
        self.inertia.logout()
        self.assertEqual(self.inertia.get(reverse("rooms:overview")).status_code, 302)
