from django.contrib.auth import get_user_model
from django.db import models

from recipes.validators import validate_ingredient_amount

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200, verbose_name="название ингредиента"
    )
    measurement_unit = models.CharField(
        max_length=200, verbose_name="единица измерения"
    )

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"

    class Meta:
        ordering = ["name"]
        verbose_name = "ингредиент"
        verbose_name_plural = "ингредиенты"


class Tag(models.Model):
    name = models.CharField(
        max_length=200, unique=True, verbose_name="название тега"
    )
    color = models.CharField(
        max_length=7, unique=True, verbose_name="цвет тега"
    )
    slug = models.SlugField(
        max_length=200, unique=True, verbose_name="слаг тега"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "тег"
        verbose_name_plural = "теги"


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="автор",
    )
    name = models.CharField(max_length=200, verbose_name="название рецепта")
    image = models.ImageField(
        upload_to="images/recipes/", verbose_name="изображение"
    )
    text = models.TextField(verbose_name="описание рецепта")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="ингредиенты",
    )
    tags = models.ManyToManyField(
        Tag, related_name="recipes", verbose_name="теги"
    )
    cooking_time = models.PositiveIntegerField(
        help_text="in minutes", verbose_name="время приготовления"
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name="дата публикации"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "рецепт"
        verbose_name_plural = "рецепты"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="ингредиент",
    )
    amount = models.FloatField(validators=[validate_ingredient_amount])

    class Meta:
        verbose_name = "ингредиент рецепта"
        verbose_name_plural = "ингредиенты рецепта"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient",
            )
        ]

    def __str__(self):
        return f"{self.ingredient} ({self.amount})"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="рецепт",
    )

    class Meta:
        verbose_name = "избранное"
        verbose_name_plural = "избранные"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_favorite",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="рецепт",
    )

    class Meta:
        verbose_name = "список покупок"
        verbose_name_plural = "списки покупок"
        unique_together = ["user", "recipe"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_shopping_cart",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.recipe}"
