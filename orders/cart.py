from decimal import Decimal

from catalog.models import Item

CART_SESSION_KEY = "cart"
MAX_QUANTITY = 20


class Cart:
    """The shopping cart, stored in the visitor's session as {item_id: quantity}.

    Only ids and quantities are stored. Names and prices are always read fresh from
    the database, so an old or tampered session can never set a price.
    """

    def __init__(self, request):
        self.session = request.session
        self.items = self.session.get(CART_SESSION_KEY, {})

    def save(self):
        # Assigning (not just changing the dict) tells Django the session must be saved.
        self.session[CART_SESSION_KEY] = self.items

    def add(self, item, quantity=1, replace=False):
        """Add `quantity` of an item (or set it, with replace=True). Returns the new quantity."""
        key = str(item.pk)
        current = 0 if replace else self.items.get(key, 0)
        new_quantity = min(current + quantity, item.stock, MAX_QUANTITY)
        if new_quantity > 0:
            self.items[key] = new_quantity
        else:
            self.items.pop(key, None)
        self.save()
        return new_quantity

    def remove(self, item):
        self.items.pop(str(item.pk), None)
        self.save()

    def clear(self):
        self.session.pop(CART_SESSION_KEY, None)

    @property
    def count(self):
        """Total number of pieces in the cart (for the navbar badge)."""
        return sum(self.items.values())

    def summary(self):
        """Return (lines, total). Each line has the item, quantity, line total and availability."""
        items = Item.objects.filter(pk__in=self.items.keys(), is_active=True).select_related("category")
        lines = []
        total = Decimal("0.00")
        for item in items:
            quantity = self.items[str(item.pk)]
            line_total = item.price * quantity
            total += line_total
            lines.append({
                "item": item,
                "quantity": quantity,
                "line_total": line_total,
                "available": item.stock >= quantity,
            })
        return lines, total