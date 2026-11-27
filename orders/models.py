from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from accounts.models import phone_validator
from catalog.models import Item


class Order(models.Model):
    """A placed order. Prices are copied in, so later price changes never alter old orders."""

    class Status(models.TextChoices):
        CONFIRMED = "confirmed", _("Confirmed")
        SHIPPED = "shipped", _("Shipped")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(_("status"), max_length=20, choices=Status.choices, default=Status.CONFIRMED)
    full_name = models.CharField(_("full name"), max_length=150)
    email = models.EmailField(_("email"))
    phone = models.CharField(_("phone"), max_length=16, validators=[phone_validator])
    address = models.CharField(_("address"), max_length=200)
    city = models.CharField(_("city"), max_length=100)
    postal_code = models.CharField(_("postal code"), max_length=10)
    total = models.DecimalField(_("total"), max_digits=10, decimal_places=2)
    payment_reference = models.CharField(_("payment reference"), max_length=100, blank=True)
    created_at = models.DateTimeField(_("placed at"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk}"

    def get_absolute_url(self):
        return reverse("orders:order_detail", args=[self.pk])


class OrderItem(models.Model):
    """One product in an order, with its name and price as they were at checkout."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="lines")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="order_lines")
    item_name = models.CharField(max_length=150)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} × {self.item_name}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity