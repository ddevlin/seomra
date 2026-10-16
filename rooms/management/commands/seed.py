from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Role, User
from rooms.models import Booking, Room
from rooms.schedule import week_start

ROOMS = [
    ("Boardroom", "Seats 12, video conferencing"),
    ("Huddle", "Seats 4, whiteboard"),
    ("Phone Booth", "One person, soundproof"),
]

MANAGER_EMAIL = "manager@example.com"
USER_EMAIL = "user@example.com"

# (room, booked by, day offset from Monday, start, end, title)
BOOKINGS = [
    ("Boardroom", USER_EMAIL, 0, 9, 10, "Stand-up"),
    ("Boardroom", MANAGER_EMAIL, 0, 14, 16, "Quarterly planning"),
    ("Huddle", USER_EMAIL, 1, 10, 11, "1:1"),
    ("Boardroom", USER_EMAIL, 2, 11, 12, "Customer call"),
    ("Phone Booth", MANAGER_EMAIL, 3, 9, 10, ""),
    ("Huddle", MANAGER_EMAIL, 4, 15, 17, "Retro"),
]


class Command(BaseCommand):
    help = "Create demo users, rooms and this week's bookings. Safe to run more than once."

    def handle(self, *args, **options):
        users = {
            MANAGER_EMAIL: self._user(MANAGER_EMAIL, Role.MANAGER),
            USER_EMAIL: self._user(USER_EMAIL, Role.USER),
        }
        rooms = {
            name: Room.objects.get_or_create(name=name, defaults={"description": description})[0]
            for name, description in ROOMS
        }

        monday = week_start(timezone.localdate())
        created = 0
        for room_name, email, offset, start, end, title in BOOKINGS:
            _, was_created = Booking.objects.get_or_create(
                room=rooms[room_name],
                date=monday + timedelta(days=offset),
                start_hour=start,
                end_hour=end,
                defaults={"user": users[email], "title": title},
            )
            created += was_created

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(rooms)} rooms, {len(users)} users and {created} new bookings "
                f"for the week of {monday:%d %b %Y}."
            )
        )
        self.stdout.write(f"Sign in as {MANAGER_EMAIL} or {USER_EMAIL}; the link prints in this console.")

    def _user(self, email, role):
        return User.objects.filter(email=email).first() or User.objects.create_user(email, role=role)
