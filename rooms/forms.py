from django import forms

from .models import Booking, Room


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ["name", "description"]


class BookingForm(forms.ModelForm):
    """Pass ``instance=Booking(room=..., user=...)`` so the model's overlap check
    runs against the right room during ``is_valid()``."""

    class Meta:
        model = Booking
        fields = ["date", "start_hour", "end_hour", "title"]
