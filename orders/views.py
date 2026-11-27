from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from catalog.models import Item

from .cart import MAX_QUANTITY, Cart
from .forms import CartQuantityForm, CheckoutForm
from .models import Order
from .services import OutOfStock, place_order


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

@login_required
def checkout(request):
    """Delivery details and order summary; placing the order happens in services.place_order."""
    cart = Cart(request)
    lines, total = cart.summary()
    if not lines:
        messages.info(request, _("Your cart is empty."))
        return redirect("orders:cart")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                order = place_order(request.user, lines, total, form)
            except OutOfStock as error:
                messages.error(
                    request,
                    _("Sorry, %(item)s doesn't have enough stock left. Please update your cart.")
                    % {"item": error.item.name},
                )
                return redirect("orders:cart")

            cart.clear()
            messages.success(request, _("Thank you! Your order #%(number)s is confirmed.") % {"number": order.pk})
            if any(line["item"].is_event_package for line in lines):
                messages.info(request, _("Your event package is active: you are now an Event host."))
            return redirect(order.get_absolute_url())
    else:
        user = request.user
        form = CheckoutForm(initial={
            "full_name": user.get_full_name(),
            "email": user.email,
            "phone": user.phone,
            "city": user.city,
        })

    return render(request, "orders/checkout.html", {"form": form, "lines": lines, "total": total})


@login_required
def order_list(request):
    """The logged-in user's own orders."""
    orders = request.user.orders.prefetch_related("lines")
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
def order_detail(request, pk):
    """One of the logged-in user's own orders. Other people's orders return 404."""
    order = get_object_or_404(Order.objects.prefetch_related("lines"), pk=pk, user=request.user)
    return render(request, "orders/order_detail.html", {"order": order})