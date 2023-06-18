from django.core.exceptions import ValidationError


def validate_ingredient_amount(value):
    if value <= 0:
        raise ValidationError(
            "Количество ингредиента должно быть положительным."
        )
