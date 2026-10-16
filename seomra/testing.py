"""Small factories shared by the test suites."""

from accounts.models import Role, User
from rooms.models import Room


def make_user(email="user@example.com", role=Role.USER):
    return User.objects.create_user(email, role=role)


def make_manager(email="manager@example.com"):
    return make_user(email, role=Role.MANAGER)


def make_room(name="Boardroom", **kwargs):
    return Room.objects.create(name=name, **kwargs)
