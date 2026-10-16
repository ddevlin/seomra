from functools import wraps
from urllib.parse import urlsplit

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.urls import Resolver404, resolve


def manager_required(view):
    """Allow only signed-in users whose role is manager; everyone else gets a 403."""

    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_manager:
            raise PermissionDenied("Only room managers can do that.")
        return view(request, *args, **kwargs)

    wrapper.manager_only = True
    return wrapper


def is_manager_only(url):
    """True if ``url`` routes to a view wrapped in ``manager_required``."""
    try:
        match = resolve(urlsplit(url).path)
    except Resolver404:
        return False
    return getattr(match.func, "manager_only", False)
