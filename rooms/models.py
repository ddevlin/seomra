from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q

OPENING_HOUR = 9
CLOSING_HOUR = 17
HOURS = range(OPENING_HOUR, CLOSING_HOUR)  # start hour of each bookable slot


class Room(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


class Booking(models.Model):
    """A room held for whole-hour slots on one day.

    ``end_hour`` is exclusive: start_hour=9, end_hour=10 is the 09:00–10:00 slot.
    """

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    date = models.DateField()
    start_hour = models.PositiveSmallIntegerField()
    end_hour = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_hour"]
        constraints = [
            models.CheckConstraint(
                condition=Q(start_hour__gte=OPENING_HOUR, end_hour__lte=CLOSING_HOUR, start_hour__lt=F("end_hour")),
                name="booking_within_opening_hours",
            )
        ]

    def __str__(self):
        return f"{self.room} {self.date} {self.start_hour:02d}:00–{self.end_hour:02d}:00"

    def clean(self):
        if self.start_hour is None or self.end_hour is None or self.date is None:
            return  # field-level validation has already reported these
        errors = {}
        if not OPENING_HOUR <= self.start_hour < CLOSING_HOUR:
            errors["start_hour"] = f"Start must be between {OPENING_HOUR:02d}:00 and {CLOSING_HOUR - 1:02d}:00."
        if not OPENING_HOUR < self.end_hour <= CLOSING_HOUR:
            errors["end_hour"] = f"End must be between {OPENING_HOUR + 1:02d}:00 and {CLOSING_HOUR:02d}:00."
        elif self.end_hour <= self.start_hour:
            errors["end_hour"] = "End must be after start."
        if errors:
            raise ValidationError(errors)
        if self.room_id and self.overlapping().exists():
            raise ValidationError({"start_hour": "This room is already booked for part of that time."})

    def overlapping(self):
        """Other bookings of the same room on the same day that share at least one hour."""
        return Booking.objects.filter(
            room_id=self.room_id,
            date=self.date,
            start_hour__lt=self.end_hour,
            end_hour__gt=self.start_hour,
        ).exclude(pk=self.pk)

    def can_cancel(self, user):
        return user.is_authenticated and (user.id == self.user_id or user.is_manager)

    def to_dict(self, viewer=None):
        return {
            "id": self.id,
            "room_id": self.room_id,
            "room_name": self.room.name,
            "user_email": self.user.email,
            "date": self.date.isoformat(),
            "start_hour": self.start_hour,
            "end_hour": self.end_hour,
            "title": self.title,
            "is_mine": viewer is not None and viewer.id == self.user_id,
            "can_cancel": viewer is not None and self.can_cancel(viewer),
        }
