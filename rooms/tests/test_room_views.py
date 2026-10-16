from datetime import date

from django.urls import reverse
from inertia.test import InertiaTestCase

from rooms.models import Booking, Room
from seomra.testing import make_manager, make_room, make_user


class RoomIndexTests(InertiaTestCase):
    def test_lists_rooms_alphabetically(self):
        make_room("Zeta")
        make_room("Alpha", description="Small")
        self.inertia.force_login(make_user())
        self.inertia.get(reverse("rooms:index"))
        self.assertComponentUsed("Rooms/Index")
        self.assertEqual([r["name"] for r in self.props()["rooms"]], ["Alpha", "Zeta"])
        self.assertEqual(self.props()["rooms"][0]["description"], "Small")

    def test_requires_login(self):
        response = self.inertia.get(reverse("rooms:index"))
        self.assertEqual(response.status_code, 302)


class RoomCreateTests(InertiaTestCase):
    def test_user_role_is_forbidden(self):
        self.inertia.force_login(make_user())
        self.assertEqual(self.inertia.get(reverse("rooms:create")).status_code, 403)
        self.assertEqual(self.inertia.post(reverse("rooms:create"), {"name": "X"}).status_code, 403)
        self.assertEqual(Room.objects.count(), 0)

    def test_manager_sees_form(self):
        self.inertia.force_login(make_manager())
        self.inertia.get(reverse("rooms:create"))
        self.assertComponentUsed("Rooms/Form")
        self.assertIsNone(self.props()["room"])
        self.assertEqual(self.props()["errors"], {})

    def test_manager_creates_room_and_lands_on_schedule(self):
        self.inertia.force_login(make_manager())
        response = self.inertia.post(reverse("rooms:create"), {"name": "Boardroom", "description": "Big table"})
        room = Room.objects.get(name="Boardroom")
        self.assertRedirects(response, reverse("rooms:schedule", args=[room.id]), fetch_redirect_response=False)
        self.assertEqual(room.description, "Big table")

    def test_duplicate_name_rerenders_with_error(self):
        make_room("Boardroom")
        self.inertia.force_login(make_manager())
        self.inertia.post(reverse("rooms:create"), {"name": "Boardroom"})
        self.assertComponentUsed("Rooms/Form")
        self.assertIn("name", self.props()["errors"])
        self.assertEqual(Room.objects.count(), 1)

    def test_blank_name_rerenders_with_error(self):
        self.inertia.force_login(make_manager())
        self.inertia.post(reverse("rooms:create"), {"name": ""})
        self.assertIn("name", self.props()["errors"])
        self.assertEqual(Room.objects.count(), 0)


class RoomEditDeleteTests(InertiaTestCase):
    def setUp(self):
        super().setUp()
        self.room = make_room("Boardroom")

    def test_edit_updates_room(self):
        self.inertia.force_login(make_manager())
        self.inertia.get(reverse("rooms:edit", args=[self.room.id]))
        self.assertComponentUsed("Rooms/Form")
        self.assertEqual(self.props()["room"]["name"], "Boardroom")
        response = self.inertia.post(
            reverse("rooms:edit", args=[self.room.id]), {"name": "Board Room", "description": ""}
        )
        self.assertRedirects(response, reverse("rooms:index"), fetch_redirect_response=False)
        self.assertEqual(Room.objects.get(pk=self.room.pk).name, "Board Room")

    def test_edit_forbidden_for_user(self):
        self.inertia.force_login(make_user())
        response = self.inertia.post(reverse("rooms:edit", args=[self.room.id]), {"name": "X"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Room.objects.get(pk=self.room.pk).name, "Boardroom")

    def test_edit_unknown_room_is_404(self):
        self.inertia.force_login(make_manager())
        self.assertEqual(self.inertia.get(reverse("rooms:edit", args=[999])).status_code, 404)

    def test_delete_removes_room_and_its_bookings(self):
        Booking.objects.create(room=self.room, user=make_user(), date=date(2030, 1, 7), start_hour=9, end_hour=10)
        self.inertia.force_login(make_manager())
        response = self.inertia.delete(reverse("rooms:delete", args=[self.room.id]))
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response["Location"], reverse("rooms:index"))
        self.assertEqual(Room.objects.count(), 0)
        self.assertEqual(Booking.objects.count(), 0)

    def test_delete_forbidden_for_user(self):
        self.inertia.force_login(make_user())
        self.assertEqual(self.inertia.delete(reverse("rooms:delete", args=[self.room.id])).status_code, 403)
        self.assertEqual(Room.objects.count(), 1)

    def test_delete_requires_delete_method(self):
        self.inertia.force_login(make_manager())
        self.assertEqual(self.inertia.get(reverse("rooms:delete", args=[self.room.id])).status_code, 405)
        self.assertEqual(Room.objects.count(), 1)


class RoomScheduleTests(InertiaTestCase):
    def setUp(self):
        super().setUp()
        self.room = make_room("Boardroom")
        self.user = make_user()
        self.inertia.force_login(self.user)

    def test_week_grid_props(self):
        other = make_user("other@example.com")
        Booking.objects.create(
            room=self.room, user=other, date=date(2030, 1, 8), start_hour=10, end_hour=12, title="Planning"
        )
        Booking.objects.create(room=self.room, user=self.user, date=date(2030, 1, 14), start_hour=9, end_hour=10)
        Booking.objects.create(room=make_room("Other"), user=self.user, date=date(2030, 1, 8), start_hour=9, end_hour=10)
        self.inertia.get(reverse("rooms:schedule", args=[self.room.id]) + "?week=2030-01-09")
        self.assertComponentUsed("Rooms/Schedule")
        props = self.props()
        self.assertEqual(props["room"]["name"], "Boardroom")
        self.assertEqual(props["days"][0], "2030-01-07")
        self.assertEqual(len(props["days"]), 7)
        self.assertEqual(props["hours"], list(range(9, 17)))
        self.assertEqual(props["prev_week"], "2029-12-31")
        self.assertEqual(props["next_week"], "2030-01-14")
        self.assertEqual(len(props["bookings"]), 1)  # next week's and other room's bookings excluded
        booking = props["bookings"][0]
        self.assertEqual(booking["title"], "Planning")
        self.assertEqual(booking["user_email"], "other@example.com")
        self.assertFalse(booking["is_mine"])
        self.assertFalse(booking["can_cancel"])

    def test_garbage_week_param_falls_back_to_current_week(self):
        response = self.inertia.get(reverse("rooms:schedule", args=[self.room.id]) + "?week=banana")
        self.assertEqual(response.status_code, 200)
        props = self.props()
        self.assertEqual(len(props["days"]), 7)
        self.assertIn(props["today"], props["days"])

    def test_unknown_room_is_404(self):
        self.assertEqual(self.inertia.get(reverse("rooms:schedule", args=[999])).status_code, 404)
