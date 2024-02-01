import re

from rest_framework.exceptions import ValidationError


def slug_validator(slug):
    """Валидатор slug."""
    if not re.fullmatch(r'^[-a-zA-Z0-9_]+$', slug):
        raise ValidationError(
            'slug может содержать только буквы, цифры, '
            'знаки -, _, @ и .'
        )
    return slug


def color_validator(color):
    """Валидатор цвета."""
    if not re.fullmatch(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color):
        raise ValidationError(
            'color может содержать только буквы, цифры, '
            'знаки -, _, @ и .'
        )
    return color
