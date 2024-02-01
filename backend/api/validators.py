import re

from rest_framework.exceptions import ValidationError


def username_validator(username):
    """Валидатор юзернейна на недопустимые символы и запрещенные слова."""
    cleaned_value = re.sub(r'[^\w.@+-]', '', username)
    if set(username) - set(cleaned_value):
        invalid_characters = set(username) - set(cleaned_value)
        invalid_chars_str = ''.join(invalid_characters)
        raise ValidationError(
            f'Недопустимые символы {invalid_chars_str} в username. '
            'Username может содержать только буквы, цифры и '
            'знаки @/./+/-/_.'
        )
    return username
