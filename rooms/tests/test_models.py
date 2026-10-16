from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import Role, User
from rooms.models import Booking, Room

DAY = date(2030, 1, 7)  # a Monday far in the future


def make_booking(room, user, start, end, day=DAY, save=True):
    booking = Booking(room=room, user=user, date=day, start_hour=start, end_hour=end)
    booking.full_clean()
    if save:
        booking.save()
    return booking


class BookingValidationTests(TestCase):
    def setUp(self):
        self.room = Room.objects.create(name="Boardroom")
        self.other_room = Room.objects.create(name="Huddle")
        self.user = User.objects.create_user("a@example.com")

    def test_valid_booking_saves(self):
        make_booking(self.room, self.user, 9, 10)
        self.assertEqual(Booking.objects.count(), 1)

    def test_start_before_opening_is_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            make_booking(self.room, self.user, 8, 10)
        self.assertIn("start_hour", ctx.exception.message_dict)

    def test_end_after_closing_is_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            make_booking(self.room, self.user, 16, 18)
        self.assertIn("end_hour", ctx.exception.message_dict)

    def test_end_must_be_after_start(self):
        with self.assertRaises(ValidationError) as ctx:
            make_booking(self.room, self.user, 11, 11)
        self.assertIn("end_hour", ctx.exception.message_dict)

    def test_identical_slot_is_a_conflict(self):
        make_booking(self.room, self.user, 9, 10)
        with self.assertRaises(ValidationError) as ctx:
            make_booking(self.room, self.user, 9, 10)
        self.assertIn("start_hour", ctx.exception.message_dict)

    def test_partial_overlap_is_a_conflict(self):
        make_booking(self.room, self.user, 9, 11)
        with self.assertRaises(ValidationError):
            make_booking(self.room, self.user, 10, 12)  # starts inside
        with self.assertRaises(ValidationError):
            make_booking(self.room, self.user, 9, 13)  # fully covers
        with self.assertRaises(ValidationError):
            make_booking(self.room, self.user, 10, 11)  # fully inside

    def test_touching_slots_are_not_a_conflict(self):
        make_booking(self.room, self.user, 9, 10)
        make_booking(self.room, self.user, 10, 11)
        self.assertEqual(Booking.objects.count(), 2)

    def test_same_slot_other_room_or_day_is_fine(self):
        make_booking(self.room, self.user, 9, 10)
        make_booking(self.other_room, self.user, 9, 10)
        make_booking(self.room, self.user, 9, 10, day=date(2030, 1, 8))
        self.assertEqual(Booking.objects.count(), 3)

    def test_editing_a_booking_does_not_conflict_with_itself(self):
        booking = make_booking(self.room, self.user, 9, 10)
        booking.title = "Renamed"
        booking.full_clean()  # must not raise


class BookingPermissionTests(TestCase):
    def test_owner_and_managers_can_cancel(self):
        room = Room.objects.create(name="Boardroom")
        owner = User.objects.create_user("owner@example.com")
        other = User.objects.create_user("other@example.com")
        manager = User.objects.create_user("m@example.com", role=Role.MANAGER)
        booking = make_booking(room, owner, 9, 10)
        self.assertTrue(booking.can_cancel(owner))
        self.assertTrue(booking.can_cancel(manager))
        self.assertFalse(booking.can_cancel(other))

    def test_to_dict_marks_ownership_for_viewer(self):
        room = Room.objects.create(name="Boardroom")
        owner = User.objects.create_user("owner@example.com")
        other = User.objects.create_user("other@example.com")
        booking = make_booking(room, owner, 9, 11)
        booking.title = "Sync"
        booking.save()
        self.assertEqual(
            booking.to_dict(owner),
            {
                "id": booking.id,
                "room_id": room.id,
                "room_name": "Boardroom",
                "user_email": "owner@example.com",
                "date": "2030-01-07",
                "start_hour": 9,
                "end_hour": 11,
                "title": "Sync",
                "is_mine": True,
                "can_cancel": True,
            },
        )
        as_other = booking.to_dict(other)
        self.assertFalse(as_other["is_mine"])
        self.assertFalse(as_other["can_cancel"])


class RoomTests(TestCase):
    def test_room_names_are_unique(self):
        Room.objects.create(name="Boardroom")
        room = Room(name="Boardroom")
        with self.assertRaises(ValidationError):
            room.full_clean()

    def test_rooms_order_by_name(self):
        Room.objects.create(name="Zeta")
        Room.objects.create(name="Alpha")
        self.assertEqual([r.name for r in Room.objects.all()], ["Alpha", "Zeta"])

    def test_deleting_room_deletes_bookings(self):
        room = Room.objects.create(name="Boardroom")
        user = User.objects.create_user("a@example.com")
        make_booking(room, user, 9, 10)
        room.delete()
        self.assertEqual(Booking.objects.count(), 0)
