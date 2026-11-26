from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.utils.translation import gettext as _

from accounts.decorators import administrator_required
from catalog.models import Category, Item, SearchQuery


@administrator_required
def home(request):
    """Administration home. The management pages for items, categories and users come in Step 12."""
    stats = [
        (_("Products"), Item.objects.count()),
        (_("Categories"), Category.objects.count()),
        (_("Users"), get_user_model().objects.count()),
        (_("Searches"), SearchQuery.objects.count()),
    ]
    return render(request, "backoffice/home.html", {"stats": stats})