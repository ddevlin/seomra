from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from inertia import render

from seomra.forms import errors_dict
from seomra.http import safe_referer

from .decorators import is_manager_only
from .forms import LoginForm
from .magic_links import send_magic_link
from .models import MagicLink, User


def login_view(request):
    if request.user.is_authenticated:
        return redirect("rooms:index")
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].strip().lower()
            user = User.objects.filter(email=email).first() or User.objects.create_user(email)
            link = MagicLink.objects.create(user=user)
            send_magic_link(request, link)
            return redirect("accounts:login_sent")
        return render(request, "Auth/Login", {"errors": errors_dict(form)})
    return render(request, "Auth/Login")


def login_sent(request):
    return render(request, "Auth/Sent")


def login_verify(request, token):
    link = MagicLink.objects.filter(token=token).select_related("user").first()
    if link is None or not link.is_valid:
        messages.error(request, "That sign-in link is invalid or has expired. Request a new one.")
        return redirect("accounts:login")
    link.consume()
    login(request, link.user)
    return redirect("rooms:index")


@require_POST
def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@login_required
@require_POST
def switch_role(request):
    request.user.toggle_role()
    messages.success(request, f"You are now a {request.user.get_role_display().lower()}.")
    back = safe_referer(request)
    if not request.user.is_manager and is_manager_only(back):
        # Demoted while on a manager-only page: that page would now 403.
        back = reverse("rooms:index")
    return redirect(back)
