from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Item

# Items marked "Any event" suit every event, so "Any" isn't offered as a filter value.
EVENT_TYPE_CHOICES = [("", _("All event types"))] + [
    choice for choice in Item.EventType.choices if choice[0] != Item.EventType.ANY
]
STYLE_CHOICES = [("", _("All styles"))] + Item.Style.choices
SORT_CHOICES = [
    ("newest", _("Newest")),
    ("price_asc", _("Price: low to high")),
    ("price_desc", _("Price: high to low")),
    ("name", _("Name A–Z")),
]


class ItemFilterForm(forms.Form):
    """Search and filter form for the shop. Submitted with GET, so results can be bookmarked."""

    q = forms.CharField(label=_("Search by name"), required=False, max_length=100)
    event_type = forms.ChoiceField(label=_("Event type"), required=False, choices=EVENT_TYPE_CHOICES)
    style = forms.ChoiceField(label=_("Style"), required=False, choices=STYLE_CHOICES)
    min_price = forms.DecimalField(label=_("Min price (€)"), required=False, min_value=0, decimal_places=2)
    max_price = forms.DecimalField(label=_("Max price (€)"), required=False, min_value=0, decimal_places=2)
    sort = forms.ChoiceField(label=_("Sort by"), required=False, choices=SORT_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Give every field its Bootstrap class once, instead of repeating it per field.
        for field in self.fields.values():
            is_select = isinstance(field.widget, forms.Select)
            field.widget.attrs["class"] = "form-select" if is_select else "form-control"

    def clean(self):
        """Check rules that involve more than one field."""
        cleaned_data = super().clean()
        low = cleaned_data.get("min_price")
        high = cleaned_data.get("max_price")
        if low is not None and high is not None and low > high:
            raise forms.ValidationError(_("The minimum price can't be higher than the maximum price."))
        return cleaned_data