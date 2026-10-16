from django.utils.http import url_has_allowed_host_and_scheme


def safe_referer(request, fallback="/"):
    """Return the Referer URL if it points at this host, otherwise ``fallback``."""
    referer = request.META.get("HTTP_REFERER")
    if referer and url_has_allowed_host_and_scheme(
        referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return referer
    return fallback
