from .roles import is_administrator, is_event_host


def roles(request):
    """Make the user's roles available in every template as is_administrator / is_event_host."""
    return {
        "is_administrator": is_administrator(request.user),
        "is_event_host": is_event_host(request.user),
    }