import re

from rest_framework.exceptions import ValidationError


def username_validator(username):
    """Валидатор юзернейна на недопустимые символы и запрещенные слова."""
    cleaned_value = re.sub(r'[^\w.@+-]', '', username)
    if set(username) - set(cleaned_value):
        invalid_characters = set(username) - set(cleaned_value)
        invalid_chars_str = "".join(invalid_characters)
        raise ValidationError(
            f"Недопустимые символы {invalid_chars_str} в username. "
            "Username может содержать только буквы, цифры и "
            "знаки @/./+/-/_."
        )
    return username


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
