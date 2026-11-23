from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """MomentSnap user. Inherits username, password, etc. from Django."""

    email = models.EmailField(unique=True)