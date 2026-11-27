from .cart import MAX_QUANTITY, Cart


def cart(request):
    """Make the cart's item count and the quantity limit available in every template."""
    return {
        "cart_count": Cart(request).count,
        "cart_max_quantity": MAX_QUANTITY,
    }