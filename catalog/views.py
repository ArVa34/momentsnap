from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Item


def item_list(request, category_slug=None):
    """Show active items, optionally limited to one category and its sub-categories."""
    categories = Category.objects.filter(parent=None).prefetch_related("children")
    items = Item.objects.filter(is_active=True).select_related("category")

    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        items = items.filter(
            Q(category=current_category) | Q(category__parent=current_category)
        )

    page_title = current_category.name if current_category else "All products"

    return render(request, "catalog/item_list.html", {
        "categories": categories,
        "current_category": current_category,
        "items": items,
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