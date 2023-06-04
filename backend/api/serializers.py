import base64
from django.forms import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
)

from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    RecipeIngredient,
    Favorite,
    ShoppingCart,
)
from users.models import Subscription

from .services import add_ingredients_to_recipe

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


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


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.HiddenField(default=None)

    def validate_recipe(self, value):
        recipe_id = self.context["request"].parser_context["kwargs"][
            "recipe_id"
        ]
        return get_object_or_404(Recipe, pk=recipe_id)

    class Meta:
        fields = ("user", "recipe")
        model = Favorite

    # реализовать удаление рецепта из избранного


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.HiddenField(default=None)

    def validate_recipe(self, value):
        recipe_id = self.context["request"].parser_context["kwargs"][
            "recipe_id"
        ]
        return get_object_or_404(Recipe, pk=recipe_id)

    class Meta:
        fields = ("user", "recipe")
        model = ShoppingCart

    # реализовать удаление рецепта из корзины


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True)

    class Meta:
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
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
            ingredient_data.append(
                {
                    "id": recipe_ingredient.ingredient.id,
                    "name": recipe_ingredient.ingredient.name,
                    "measurement_unit": recipe_ingredient.ingredient.measurement_unit,
                    "amount": recipe_ingredient.amount,
                }
            )
        return ingredient_data

    def get_is_favorited(self, obj):
        request = self.context["request"]
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context["request"]
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def validate(self, data):
        tags_data = self.initial_data.get("tags")
        ingredients_data = self.initial_data.get("ingredients")

        if not tags_data or not ingredients_data:
            raise ValidationError("Tags and ingredients are required.")

        tags = Tag.objects.filter(id__in=tags_data)
        ingredient_ids = [
            ingredient_data.get("id") for ingredient_data in ingredients_data
        ]
        ingredients = Ingredient.objects.filter(id__in=ingredient_ids)

        if len(tags_data) != len(tags) or len(ingredients_data) != len(
            ingredients
        ):
            raise ValidationError("Invalid tags or ingredients.")

        data["tags"] = tags_data
        data["ingredients"] = ingredients_data
        return data

    def create(self, validated_data):
        tag_ids = validated_data.pop("tags", [])
        tags = Tag.objects.filter(id__in=tag_ids)
        ingredients = validated_data.pop("ingredients", [])
        request = self.context["request"]
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        add_ingredients_to_recipe(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop("tags", [])
        tags = Tag.objects.filter(id__in=tag_ids)
        ingredients = validated_data.pop("ingredients", [])
        instance.tags.set(tags)
        instance.recipe_ingredients.all().delete()
        add_ingredients_to_recipe(instance, ingredients)

        return super().update(instance, validated_data)


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    author = serializers.HiddenField(default=None)

    def validate_author(self, value):
        user_id = self.context["request"].parser_context["kwargs"]["user_id"]
        return get_object_or_404(User, pk=user_id)

    class Meta:
        fields = ("user", "author")
        model = Subscription


class RecipeSmallSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "image", "cooking_time")
        model = Recipe


class SubscriptionListSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="author.email")
    id = serializers.IntegerField(source="author.id")
    username = serializers.CharField(source="author.username")
    first_name = serializers.CharField(source="author.first_name")
    last_name = serializers.CharField(source="author.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        request = self.context["request"]
        limit = request.query_params.get("recipes_limit")
        if limit:
            recipes = recipes[: int(limit)]
        return RecipeSmallSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_is_subscribed(self, obj):
        request = self.context["request"]
        return Subscription.objects.filter(
            user=request.user, author=obj.author
        ).exists()
