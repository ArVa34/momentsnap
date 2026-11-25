from django.shortcuts import render

from catalog.models import Category


def home(request):
    """Public home page: what MomentSnap is, how it works, and the shop's main categories."""
    categories = Category.objects.filter(parent=None)
    return render(request, "core/home.html", {"categories": categories})