from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
)

from recipes.models import Ingredient, Tag, Recipe, RecipeIngredient

User = get_user_model()


class UserSerializer(DjoserUserCreateSerializer):
    class Meta(DjoserUserCreateSerializer.Meta):
        fields = ("email", "username", "first_name", "last_name", "password")
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def run_validation(self, data=serializers.empty):
        if self.context["request"].method == "POST":
            self.fields["password"].required = True
        return super().run_validation(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "color", "slug")
        read_only_fields = ("id", "slug")
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name")


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = ("id", "author")
        model = Recipe

    def get_ingredients(self, obj):
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=obj)
        ingredient_data = []
        for recipe_ingredient in recipe_ingredients:
            ingredient_data.append({
                "id": recipe_ingredient.ingredient.id,
                "name": recipe_ingredient.ingredient.name,
                "measurement_unit": recipe_ingredient.ingredient.measurement_unit,
                "amount": recipe_ingredient.quantity,
            })
        return ingredient_data
