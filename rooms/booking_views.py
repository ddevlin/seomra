from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from inertia import render

from seomra.forms import errors_dict
from seomra.http import safe_referer

from .forms import BookingForm
from .models import CLOSING_HOUR, HOURS, OPENING_HOUR, Booking, Room
from .schedule import parse_date_param


def _short_date(day):
    return f"{day:%a} {day.day} {day:%b}"


def _initial_from_query(params, today):
    """Prefill the booking form from ``?date=...&hour=...`` (links in the grids)."""
    day = parse_date_param(params.get("date"), today)
    try:
        hour = int(params.get("hour", OPENING_HOUR))
    except (TypeError, ValueError):
        hour = OPENING_HOUR
    if not OPENING_HOUR <= hour < CLOSING_HOUR:
        hour = OPENING_HOUR
    return {"date": day.isoformat(), "start_hour": hour, "end_hour": hour + 1, "title": ""}


@login_required
def book(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    errors = {}
    if request.method == "POST":
        form = BookingForm(request.POST, instance=Booking(room=room, user=request.user))
        # Lock the room row so two people cannot both validate the same free
        # slot at once. SQLite serialises writers anyway; this keeps Postgres
        # correct too.
        with transaction.atomic():
            Room.objects.select_for_update().get(pk=room.pk)
            if form.is_valid():
                booking = form.save()
                messages.success(
                    request,
                    f"Booked {room.name} on {_short_date(booking.date)}, "
                    f"{booking.start_hour:02d}:00–{booking.end_hour:02d}:00.",
                )
                return redirect(f"{reverse('rooms:schedule', args=[room.id])}?week={booking.date.isoformat()}")
        errors = errors_dict(form)
        initial = {
            "date": request.POST.get("date", ""),
            "start_hour": request.POST.get("start_hour", OPENING_HOUR),
            "end_hour": request.POST.get("end_hour", OPENING_HOUR + 1),
            "title": request.POST.get("title", ""),
        }
    else:
        initial = _initial_from_query(request.GET, timezone.localdate())
    return render(
        request,
        "Bookings/Form",
        {"room": room.to_dict(), "initial": initial, "hours": list(HOURS), "errors": errors},
    )


@login_required
@require_http_methods(["DELETE"])
def cancel(request, booking_id):
    booking = get_object_or_404(Booking.objects.select_related("room"), pk=booking_id)
    if not booking.can_cancel(request.user):
        raise PermissionDenied("You can only cancel your own bookings.")
    booking.delete()
    messages.success(request, f"Cancelled {booking.room.name} on {_short_date(booking.date)}.")
    return redirect(safe_referer(request, fallback=reverse("rooms:overview")))


@login_required
def overview(request):
    """Every room for one day, plus the signed-in user's upcoming bookings."""
    today = timezone.localdate()
    day = parse_date_param(request.GET.get("date"), today)
    bookings = Booking.objects.filter(date=day).select_related("room", "user")
    mine = Booking.objects.filter(user=request.user, date__gte=today).select_related("room", "user")
    return render(
        request,
        "Bookings/Overview",
        {
            "date": day.isoformat(),
            "today": today.isoformat(),
            "rooms": [room.to_dict() for room in Room.objects.all()],
            "hours": list(HOURS),
            "bookings": [booking.to_dict(request.user) for booking in bookings],
            "my_bookings": [booking.to_dict(request.user) for booking in mine],
            "prev_day": (day - timedelta(days=1)).isoformat(),
            "next_day": (day + timedelta(days=1)).isoformat(),
        },
    )
