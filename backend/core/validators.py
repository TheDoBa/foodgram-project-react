import re

from rest_framework.exceptions import ValidationError


def username_validator(value):
    """Валидатор юзернейна на недопустимые символы и запрещенные слова."""
    cleaned_value = re.sub(r'[^\w.@+-]', '', value)
    if set(value) - set(cleaned_value):
        invalid_characters = set(value) - set(cleaned_value)
        raise ValidationError(
            f'Недопустимые символы {"".join(invalid_characters)}в username. '
            'username может содержать только буквы, цифры и '
            'знаки @/./+/-/_.'
        )
    return value


def slug_validator(value):
    """Валидатор slug."""
    if not re.fullmatch(r'^[-a-zA-Z0-9_]+$', value):
        raise ValidationError(
            'slug может содержать только буквы, цифры, '
            'знаки -, _, @ и .'
        )
    return value


def color_validator(value):
    """Валидатор цвета."""
    if not re.fullmatch(r'^#(?:[0-9a-fA-F]{3}){1,2}$', value):
        raise ValidationError(
            'color может содержать только буквы, цифры, '
            'знаки -, _, @ и .'
        )
    return value
