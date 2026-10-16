from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from inertia import render

from accounts.decorators import manager_required
from seomra.forms import errors_dict

from .forms import RoomForm
from .models import HOURS, Room
from .schedule import parse_date_param, week_days, week_start


@login_required
def index(request):
    return render(request, "Rooms/Index", {"rooms": [room.to_dict() for room in Room.objects.all()]})


@manager_required
def create(request):
    form = RoomForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        room = form.save()
        messages.success(request, f"Room “{room.name}” created.")
        return redirect("rooms:schedule", room.id)
    return render(request, "Rooms/Form", {"room": None, "errors": errors_dict(form)})


@manager_required
def edit(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    form = RoomForm(request.POST or None, instance=room)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Room “{room.name}” updated.")
        return redirect("rooms:index")
    return render(request, "Rooms/Form", {"room": room.to_dict(), "errors": errors_dict(form)})


@manager_required
@require_http_methods(["DELETE"])
def delete(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    room.delete()
    messages.success(request, f"Room “{room.name}” deleted.")
    return redirect("rooms:index")


@login_required
def schedule(request, room_id):
    """One room, one week (Monday to Sunday), one row per bookable hour."""
    room = get_object_or_404(Room, pk=room_id)
    today = timezone.localdate()
    start = week_start(parse_date_param(request.GET.get("week"), today))
    days = week_days(start)
    bookings = room.bookings.filter(date__range=(days[0], days[-1])).select_related("room", "user")
    return render(
        request,
        "Rooms/Schedule",
        {
            "room": room.to_dict(),
            "days": [day.isoformat() for day in days],
            "hours": list(HOURS),
            "bookings": [booking.to_dict(request.user) for booking in bookings],
            "today": today.isoformat(),
            "prev_week": (start - timedelta(days=7)).isoformat(),
            "next_week": (start + timedelta(days=7)).isoformat(),
        },
    )
