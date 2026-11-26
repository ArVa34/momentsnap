from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

phone_validator = RegexValidator(
    regex=r"^\+?[0-9]{10,15}$",
    message=_("Enter a phone number with 10 to 15 digits, optionally starting with +."),
)


class User(AbstractUser):
    """MomentSnap user. Inherits username, password, names etc. from Django."""

    email = models.EmailField(_("email address"), unique=True)
    phone = models.CharField(_("phone"), max_length=16, blank=True, validators=[phone_validator])
    city = models.CharField(_("city"), max_length=100, blank=True)