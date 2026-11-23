from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


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
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} › {self.name}"
        return self.name


class Item(models.Model):
    """A product in the catalogue."""

    class EventType(models.TextChoices):
        ANY = "any", "Any event"
        WEDDING = "wedding", "Wedding"
        CHRISTENING = "christening", "Christening"
        BIRTHDAY = "birthday", "Birthday"
        CORPORATE = "corporate", "Corporate"

    class Style(models.TextChoices):
        MINIMAL = "minimal", "Minimal"
        FLORAL = "floral", "Floral"
        RUSTIC = "rustic", "Rustic"
        CLASSIC = "classic", "Classic"

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="items",
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    description = models.TextField()
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