import json

from django.contrib.messages import get_messages
from django.http import QueryDict
from inertia import share


def _to_form_value(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return str(value)


class JsonBodyMiddleware:
    """Expose JSON request bodies through ``request.POST``.

    The Inertia client submits forms as ``application/json``. Django only fills
    ``request.POST`` for form-encoded bodies, so without this views and Django
    forms would see empty input. With it, views read ``request.POST`` as usual.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method not in ("GET", "HEAD") and request.content_type == "application/json" and request.body:
            try:
                data = json.loads(request.body)
            except ValueError:
                data = None
            if isinstance(data, dict):
                query = QueryDict(mutable=True)
                for key, value in data.items():
                    if isinstance(value, list):
                        query.setlist(key, [_to_form_value(item) for item in value])
                    else:
                        query[key] = _to_form_value(value)
                request.POST = query
        return self.get_response(request)


def _auth(request):
    user = request.user
    return {"user": user.to_dict() if user.is_authenticated else None}


def _messages(request):
    return [{"message": m.message, "level_tag": m.level_tag} for m in get_messages(request)]


class DataShareMiddleware:
    """Props every Inertia page receives.

    Values are callables so they are evaluated when the response is built,
    after the view has run (e.g. after a role switch or a flash message).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        share(request, auth=lambda: _auth(request), messages=lambda: _messages(request))
        return self.get_response(request)
