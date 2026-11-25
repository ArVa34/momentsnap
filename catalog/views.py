from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext as _

from .forms import ItemFilterForm
from .models import Category, Item, SearchQuery

ITEMS_PER_PAGE = 9

# Only these sort options are allowed. User input never goes straight into order_by().
SORT_ORDER = {
    "newest": "-created_at",
    "price_asc": "price",
    "price_desc": "-price",
    "name": "name",
}


def filter_items(items, data):
    """Apply the cleaned search/filter values to an Item queryset."""
    if data["q"]:
        items = items.filter(name__icontains=data["q"])
    if data["event_type"]:
        items = items.filter(
            Q(event_type=data["event_type"]) | Q(event_type=Item.EventType.ANY)
        )
    if data["style"]:
        items = items.filter(style=data["style"])
    if data["min_price"] is not None:
        items = items.filter(price__gte=data["min_price"])
    if data["max_price"] is not None:
        items = items.filter(price__lte=data["max_price"])
    return items.order_by(SORT_ORDER.get(data["sort"], "-created_at"))


def log_search(request, term, results_count):
    """Save a search for analytics. Anonymous searches are stored without a user."""
    SearchQuery.objects.create(
        term=term.lower(),
        results_count=results_count,
        user=request.user if request.user.is_authenticated else None,
    )


def item_list(request, category_slug=None):
    """Shop page: active items, optionally in one category, with search, filters, sorting and pages."""
    categories = Category.objects.filter(parent=None).prefetch_related("children")
    items = Item.objects.filter(is_active=True).select_related("category")

    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        items = items.filter(
            Q(category=current_category) | Q(category__parent=current_category)
        )

    form = ItemFilterForm(request.GET)
    if form.is_valid():
        items = filter_items(items, form.cleaned_data)

    page_obj = Paginator(items, ITEMS_PER_PAGE).get_page(request.GET.get("page"))

    # Log real searches once: not when someone just clicks to page 2 of the same search.
    if form.is_valid() and form.cleaned_data["q"] and "page" not in request.GET:
        log_search(request, form.cleaned_data["q"], page_obj.paginator.count)

    page_title = current_category.name if current_category else _("All products")

    return render(request, "catalog/item_list.html", {
        "categories": categories,
        "current_category": current_category,
        "form": form,
        "page_obj": page_obj,
        "page_title": page_title,
    })


def item_detail(request, slug):
    """Show one active item."""
    item = get_object_or_404(
        Item.objects.select_related("category__parent"),
        slug=slug,
        is_active=True,
    )
    return render(request, "catalog/item_detail.html", {"item": item})