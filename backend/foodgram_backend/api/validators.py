import re

from django.core.exceptions import ValidationError


def validate_hex_color(value):
    pattern = re.compile('^#([0-9A-Fa-f]{3}){1,2}$')
    if not pattern.match(value):
        raise ValidationError(
            f"{value} is not an valid color hex code"
        )
