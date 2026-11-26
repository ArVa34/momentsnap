from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (_("Contact"), {"fields": ("phone", "city")}),
    )
    # Add the email field to the "Add user" form in the admin,
    # because our model requires a unique email.
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("email",)}),
    )