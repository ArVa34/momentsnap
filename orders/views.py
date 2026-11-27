from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from catalog.models import Item

from .cart import MAX_QUANTITY, Cart
from .forms import CartQuantityForm


def cart_detail(request):
    """Show the cart with fresh prices from the database."""
    lines, total = Cart(request).summary()
    return render(request, "orders/cart.html", {"lines": lines, "total": total})


@require_POST
def cart_add(request, item_id):
    """Add an item from its product page."""
    item = get_object_or_404(Item, pk=item_id, is_active=True)
    form = CartQuantityForm(request.POST)
    if not form.is_valid():
        messages.error(request, _("Please choose a quantity between 1 and %(max)s.") % {"max": MAX_QUANTITY})
        return redirect(item.get_absolute_url())

    if Cart(request).add(item, form.cleaned_data["quantity"]):
        messages.success(request, _("%(item)s was added to your cart.") % {"item": item.name})
    else:
        messages.error(request, _("Sorry, %(item)s is out of stock.") % {"item": item.name})
    return redirect("orders:cart")


@require_POST
def cart_update(request, item_id):
    """Change the quantity of a line in the cart."""
    item = get_object_or_404(Item, pk=item_id)
    form = CartQuantityForm(request.POST)
    if form.is_valid():
        Cart(request).add(item, form.cleaned_data["quantity"], replace=True)
    else:
        messages.error(request, _("Please choose a quantity between 1 and %(max)s.") % {"max": MAX_QUANTITY})
    return redirect("orders:cart")


@require_POST
def cart_remove(request, item_id):
    """Remove a line from the cart."""
    item = get_object_or_404(Item, pk=item_id)
    Cart(request).remove(item)
    messages.info(request, _("%(item)s was removed from your cart.") % {"item": item.name})
    return redirect("orders:cart")