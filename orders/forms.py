from django import forms
from django.utils.translation import gettext_lazy as _

from core.forms import BootstrapFormMixin

from .cart import MAX_QUANTITY


class CartQuantityForm(BootstrapFormMixin, forms.Form):
    """Validates a quantity sent from the product page or the cart."""

    quantity = forms.IntegerField(label=_("Quantity"), min_value=1, max_value=MAX_QUANTITY, initial=1)