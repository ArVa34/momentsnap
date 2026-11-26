"""The three MomentSnap roles: Administrator, Event host, and every other logged-in User."""

ADMINISTRATORS = "Administrators"
EVENT_HOSTS = "Event hosts"


def is_administrator(user):
    """Company staff: superusers or members of the Administrators group."""
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name=ADMINISTRATORS).exists()
    )


def is_event_host(user):
    """Customers who bought an event package (administrators can do everything hosts can)."""
    return user.is_authenticated and (
        is_administrator(user) or user.groups.filter(name=EVENT_HOSTS).exists()
    )