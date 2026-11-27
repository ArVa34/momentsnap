import uuid

from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import F

from accounts.roles import EVENT_HOSTS
from catalog.models import Item

from .models import OrderItem


class OutOfStock(Exception):
    """Raised when a product no longer has enough stock; the whole order is cancelled."""

    def __init__(self, item):
        self.item = item
        super().__init__(item.name)


@transaction.atomic
def place_order(user, lines, total, form):
    """Create the order, reduce stock safely and grant the Event host role if a package was bought.

    Everything runs in one transaction: if any product is out of stock, nothing is saved.
    """
    order = form.save(commit=False)
    order.user = user
    order.total = total
    order.payment_reference = f"SIM-{uuid.uuid4().hex[:10].upper()}"
    order.save()

    for line in lines:
        item = line["item"]
        quantity = line["quantity"]

        # One SQL statement: "reduce stock by N only if at least N are left".
        updated = Item.objects.filter(pk=item.pk, is_active=True, stock__gte=quantity).update(
            stock=F("stock") - quantity
        )
        if updated == 0:
            raise OutOfStock(item)

        OrderItem.objects.create(
            order=order,
            item=item,
            item_name=item.name,
            unit_price=item.price,
            quantity=quantity,
        )

    if any(line["item"].is_event_package for line in lines):
        hosts, _created = Group.objects.get_or_create(name=EVENT_HOSTS)
        user.groups.add(hosts)

    return order