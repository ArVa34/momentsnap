from django import forms
from django.utils.translation import gettext_lazy as _

from core.forms import BootstrapFormMixin

from .models import Item, Rating

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


class ItemFilterForm(BootstrapFormMixin, forms.Form):
    """Search and filter form for the shop. Submitted with GET, so results can be bookmarked."""

    q = forms.CharField(label=_("Search by name"), required=False, max_length=100)
    event_type = forms.ChoiceField(label=_("Event type"), required=False, choices=EVENT_TYPE_CHOICES)
    style = forms.ChoiceField(label=_("Style"), required=False, choices=STYLE_CHOICES)
    min_price = forms.DecimalField(label=_("Min price (€)"), required=False, min_value=0, decimal_places=2)
    max_price = forms.DecimalField(label=_("Max price (€)"), required=False, min_value=0, decimal_places=2)
    sort = forms.ChoiceField(label=_("Sort by"), required=False, choices=SORT_CHOICES)

    def clean(self):
        """Check rules that involve more than one field."""
        cleaned_data = super().clean()
        low = cleaned_data.get("min_price")
        high = cleaned_data.get("max_price")
        if low is not None and high is not None and low > high:
            raise forms.ValidationError(_("The minimum price can't be higher than the maximum price."))
        return cleaned_data


class RatingForm(BootstrapFormMixin, forms.ModelForm):
    """1–5 stars and an optional review."""

    stars = forms.TypedChoiceField(
        label=_("Stars"),
        choices=[(n, str(n)) for n in range(1, 6)],
        coerce=int,
        widget=forms.RadioSelect(attrs={"class": "btn-check"}),
    )

    class Meta:
        model = Rating
        fields = ["stars", "review"]
        widgets = {"review": forms.Textarea(attrs={"rows": 3})}