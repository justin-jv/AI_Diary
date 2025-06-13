from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class CustomLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if user.is_blocked:
            raise ValidationError("Your account has been blocked by the admin. ")