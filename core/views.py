from django.shortcuts import render


def home(request):
    """Public home page."""
    return render(request, "core/home.html")