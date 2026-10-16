from django.urls import path

from . import booking_views, views

app_name = "rooms"

urlpatterns = [
    path("rooms/", views.index, name="index"),
    path("rooms/new", views.create, name="create"),
    path("rooms/<int:room_id>/", views.schedule, name="schedule"),
    path("rooms/<int:room_id>/edit", views.edit, name="edit"),
    path("rooms/<int:room_id>/delete", views.delete, name="delete"),
    path("rooms/<int:room_id>/book", booking_views.book, name="book"),
    path("bookings/", booking_views.overview, name="overview"),
    path("bookings/<int:booking_id>/cancel", booking_views.cancel, name="cancel"),
]
