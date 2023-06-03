from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"

    class Meta:
        ordering = ["name"]


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipes"
    )
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to="images/recipes/")
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient", related_name="recipes"
    )
    tags = models.ManyToManyField(Tag, related_name="recipes")
    cooking_time = models.PositiveIntegerField(help_text="in minutes")
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-pub_date"]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()

    class Meta:
        verbose_name_plural = "Recipe Ingredients"

    def __str__(self):
        return f"{self.ingredient} ({self.quantity})"


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorites"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorites"
    )

    class Meta:
        unique_together = ["user", "recipe"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_favorite",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.recipe}"
