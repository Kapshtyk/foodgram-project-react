from recipes.models import Recipe, RecipeIngredient, Ingredient


def add_ingredients_to_recipe(recipe, ingredients):
    for ingredient_data in ingredients:
        amount = ingredient_data["amount"]
        ingredient = Ingredient.objects.get(id=ingredient_data["id"])
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            amount=amount,
        )
