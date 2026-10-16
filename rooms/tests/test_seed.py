from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from accounts.models import User
from rooms.models import Booking, Room


class SeedCommandTests(TestCase):
    def test_seed_creates_demo_data_and_is_idempotent(self):
        out = StringIO()
        call_command("seed", stdout=out)
        self.assertEqual(Room.objects.count(), 3)
        self.assertTrue(User.objects.get(email="manager@example.com").is_manager)
        self.assertFalse(User.objects.get(email="user@example.com").is_manager)
        self.assertGreater(Booking.objects.count(), 0)
        self.assertIn("manager@example.com", out.getvalue())
        before = (Room.objects.count(), User.objects.count(), Booking.objects.count())
        call_command("seed", stdout=StringIO())
        self.assertEqual(before, (Room.objects.count(), User.objects.count(), Booking.objects.count()))

    def test_seeded_bookings_are_valid(self):
        call_command("seed", stdout=StringIO())
        for booking in Booking.objects.all():
            booking.full_clean()  # must not raise: no overlaps, within opening hours
