from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from core.forms import BootstrapFormMixin

User = get_user_model()


def email_is_taken(email, exclude_pk=None):
    """True if another account already uses this email (ignoring upper/lower case)."""
    users = User.objects.filter(email__iexact=email)
    if exclude_pk is not None:
        users = users.exclude(pk=exclude_pk)
    return users.exists()


class SignUpForm(BootstrapFormMixin, UserCreationForm):
    """Registration: username, name, email and password (twice)."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if email_is_taken(email):
            raise forms.ValidationError(_("An account with this email already exists."))
        return email


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    """Django's login form, with Bootstrap styling."""


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    """The details a user can change about themselves."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "city"]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if email_is_taken(email, exclude_pk=self.instance.pk):
            raise forms.ValidationError(_("An account with this email already exists."))
        return email