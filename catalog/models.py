import uuid
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from core.validators import validate_image_size

def item_image_path(instance, filename):
    """Save item images as items/<random-name>.<ext>, ignoring the uploaded name."""
    extension = Path(filename).suffix.lower()
    return f"items/{uuid.uuid4().hex}{extension}"

class Category(models.Model):
    """A catalogue category. A category with a parent is a sub-category."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
    )

    class Meta:
        verbose_name_plural = _("categories")
        ordering = ["name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} › {self.name}"
        return self.name

    def get_absolute_url(self):
        return reverse("catalog:category_items", args=[self.slug])


class Item(models.Model):
    """A product in the catalogue."""

    class EventType(models.TextChoices):
        ANY = "any", _("Any event")
        WEDDING = "wedding", _("Wedding")
        CHRISTENING = "christening", _("Christening")
        BIRTHDAY = "birthday", _("Birthday")
        CORPORATE = "corporate", _("Corporate")

    class Style(models.TextChoices):
        MINIMAL = "minimal", _("Minimal")
        FLORAL = "floral", _("Floral")
        RUSTIC = "rustic", _("Rustic")
        CLASSIC = "classic", _("Classic")

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="items",
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    description = models.TextField()

    image = models.ImageField(
    upload_to=item_image_path,
    blank=True,
    validators=[
        FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
        validate_image_size,
        ],
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    stock = models.PositiveIntegerField(default=0)
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.ANY,
    )
    style = models.CharField(max_length=20, choices=Style.choices, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("catalog:item_detail", args=[self.slug])

class SearchQuery(models.Model):
    """One search made in the shop. Feeds the analytics dashboard and recommendations."""

    term = models.CharField(max_length=100)
    results_count = models.PositiveIntegerField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="searches",
    )
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = _("search queries")
        ordering = ["-searched_at"]

    def __str__(self):
        return f'"{self.term}" ({self.results_count} results)'