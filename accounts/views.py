from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from .forms import LoginForm, ProfileForm, SignUpForm


def safe_next_url(request, fallback="core:home"):
    """Return the ?next= address only if it points to our own site, otherwise the fallback."""
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return next_url
    return fallback


def register(request):
    """Create an account, then log the new user in."""
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _("Welcome to MomentSnap, %(name)s!") % {"name": user.first_name})
            return redirect("core:home")
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    """Log in, then return to the page that asked for it."""
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(safe_next_url(request))
    else:
        form = LoginForm(request)

    return render(request, "accounts/login.html", {"form": form, "next": request.GET.get("next", "")})


@require_POST
def logout_view(request):
    """Log out. POST only, so another site can't log people out with a hidden link."""
    logout(request)
    messages.info(request, _("You have been logged out."))
    return redirect("core:home")


@login_required
def profile(request):
    """Show and update the logged-in user's own details."""
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Your profile has been updated."))
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "accounts/profile.html", {"form": form})