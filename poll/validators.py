import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from django.core.exceptions import ValidationError
from .models import User  # Assuming your user model is named User

def validate_unique_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError('This email address is already in use.')

def validate_complex_password(password):
    # Check if the password contains at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        raise ValidationError(
            _("The password must contain at least one uppercase letter."),
            code='password_no_upper',
        )

    # Check if the password contains at least one lowercase letter
    if not re.search(r'[a-z]', password):
        raise ValidationError(
            _("The password must contain at least one lowercase letter."),
            code='password_no_lower',
        )

    # Check if the password contains at least one digit
    if not re.search(r'\d', password):
        raise ValidationError(
            _("The password must contain at least one digit."),
            code='password_no_digit',
        )

    # Check if the password contains at least one special character
    if not re.search(r'[!@#$%^&*()\-_=+{};:,<.>]', password):
        raise ValidationError(
            _("The password must contain at least one special character."),
            code='password_no_special',
        )