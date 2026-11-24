from django import forms

from .models import Item

# Items marked "Any event" suit every event, so "Any" isn't offered as a filter value.
EVENT_TYPE_CHOICES = [("", "All event types")] + [
    choice for choice in Item.EventType.choices if choice[0] != Item.EventType.ANY
]
STYLE_CHOICES = [("", "All styles")] + Item.Style.choices
SORT_CHOICES = [
    ("newest", "Newest"),
    ("price_asc", "Price: low to high"),
    ("price_desc", "Price: high to low"),
    ("name", "Name A–Z"),
]


class ItemFilterForm(forms.Form):
    """Search and filter form for the shop. Submitted with GET, so results can be bookmarked."""

    q = forms.CharField(label="Search by name", required=False, max_length=100)
    event_type = forms.ChoiceField(label="Event type", required=False, choices=EVENT_TYPE_CHOICES)
    style = forms.ChoiceField(label="Style", required=False, choices=STYLE_CHOICES)
    min_price = forms.DecimalField(label="Min price (€)", required=False, min_value=0, decimal_places=2)
    max_price = forms.DecimalField(label="Max price (€)", required=False, min_value=0, decimal_places=2)
    sort = forms.ChoiceField(label="Sort by", required=False, choices=SORT_CHOICES)

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
            raise forms.ValidationError("The minimum price can't be higher than the maximum price.")
        return cleaned_data