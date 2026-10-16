# Seomra

Seomra is a small meeting room booking app used as the starter for a
spec-driven development workshop. It is deliberately complete but minimal:
sign in, pick a role, create rooms, book hourly slots, see who has what.

## What it does

- **Sign in with a magic link.** Enter an email, click the link. No passwords.
  Locally the link is printed to the terminal instead of being emailed.
- **Two roles, one click apart.** Everyone is a *user*. Anyone can switch
  themselves to *room manager* and back from the nav bar.
- **Rooms.** Managers create, edit and delete rooms.
- **Bookings.** Any signed-in person books a room for one or more consecutive
  hour slots between 09:00 and 17:00. Overlapping bookings are rejected.
- **Overview.** All rooms for one day, hour by hour, plus your upcoming bookings.
- **Room schedule.** One room, one week, click a free slot to book it.
- **Cancel.** You can cancel your own bookings; managers can cancel anyone's.

## Stack

Django 6 · inertia-django · Vue 3 · Tailwind 4 · Vite 6 · SQLite · uv

## Setup

```bash
uv sync                       # Python dependencies into .venv
npm install                   # JavaScript dependencies
uv run manage.py migrate      # create the SQLite database
uv run manage.py seed         # demo rooms, users and this week's bookings
```

## Run

Two terminals:

```bash
npm run dev                   # Vite dev server with hot reload
uv run manage.py runserver    # Django on http://localhost:8000
```

Open <http://localhost:8000>.

## Signing in

1. Enter an email on the login page (try `manager@example.com` or
   `user@example.com` after seeding, or any address you like).
2. Look at the terminal running `runserver`. The email, including the
   sign-in link, is printed there.
3. Open the link. It works once and expires after 15 minutes.

To send real email, set `EMAIL_BACKEND` in `.env` to an SMTP backend and add
the usual `EMAIL_*` settings.

## Tests

```bash
uv run manage.py test
```

## Project layout

```
accounts/            custom User (email + role), MagicLink, login views,
                     role switch, manager_required decorator
rooms/               Room and Booking models, room CRUD, schedule,
                     booking form, cancel, overview, seed command
seomra/              settings, URLs, Inertia shared props, JSON body middleware
frontend/js/pages/   one Vue component per screen (Auth/, Rooms/, Bookings/)
frontend/js/components/  Layout, FlashMessages, BookingCell
templates/base.html  the single HTML shell Inertia mounts into
```

Every view is a plain Django function that returns `inertia.render(...)`.
Validation lives in Django forms and model `clean()` methods. When a form is
invalid the same page is rendered again with an `errors` prop, which Inertia
feeds back into the Vue form.

## Behaviour in one place

- Slots are whole hours. A booking has a date, a start hour and an exclusive
  end hour: 9 to 10 is the 09:00–10:00 slot. Start must be 9–16, end 10–17.
- Two bookings of the same room on the same day conflict if they share any
  hour. Touching bookings (9–10 and 10–11) do not conflict.
- Everything except the login pages requires sign-in.
- Room create, edit and delete return 403 unless your role is manager.
- Cancelling returns 403 unless you own the booking or are a manager.
- Dates and hours are plain local values in `TIME_ZONE` (Europe/Dublin).

## Deliberately left out

These are good candidates for workshop exercises:

- Recurring bookings
- Room capacity, equipment and filtering
- Editing an existing booking
- Blocking bookings in the past
- Booking approval by a manager
- Email or chat notifications
- Weekend and holiday rules; multiple timezones
- Admin-managed roles instead of self-service switching
