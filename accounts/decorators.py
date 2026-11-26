from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .roles import is_administrator, is_event_host


def role_required(check):
    """Allow a view only for logged-in users who pass `check`; everyone else gets the 403 page."""

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not check(request.user):
                raise PermissionDenied
            return view(request, *args, **kwargs)

        return wrapper

    return decorator


administrator_required = role_required(is_administrator)
event_host_required = role_required(is_event_host)