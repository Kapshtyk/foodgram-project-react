from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from api.fields import Base64ImageField
from api.services import add_ingredients_to_recipe
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription

User = get_user_model()


class UserSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserCreateSerializer.Meta):
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
            "is_subscribed",
        )
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

    def get_is_subscribed(self, obj):
        request = self.context["request"]
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "color", "slug")
        read_only_fields = ("id", "slug")
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
        )


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.HiddenField(default=None)

    def validate_recipe(self, value):
        recipe_id = self.context["request"].parser_context["kwargs"]["pk"]
        return get_object_or_404(Recipe, pk=recipe_id)

    class Meta:
        fields = ("user", "recipe")
        model = Favorite


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.HiddenField(default=None)

    def validate_recipe(self, value):
        recipe_id = self.context["request"].parser_context["kwargs"]["pk"]
        return get_object_or_404(Recipe, pk=recipe_id)

    class Meta:
        fields = ("user", "recipe")
        model = ShoppingCart


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "amount",
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["name"] = instance.ingredient.name
        rep["measurement_unit"] = instance.ingredient.measurement_unit
        return rep


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True, source="recipe_ingredients", read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "is_subscribed",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = ("id", "author")
        model = Recipe

    def get_is_favorited(self, obj):
        request = self.context["request"]
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context["request"]
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_subscribed(self, obj):
        request = self.context["request"]
        if request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj.author
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = RecipeIngredientCreateSerializer(
        source="recipe_ingredients", many=True
    )
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate(self, data):
        data["tags"] = [item.id for item in data.get("tags")]
        if not data.get("tags"):
            raise serializers.ValidationError("Recipe must have tags")
        if len(data.get("tags")) != len(set(data.get("tags"))):
            raise serializers.ValidationError("Recipe must have unique tags")
        if not data.get("recipe_ingredients"):
            raise serializers.ValidationError("Recipe must have ingredients")
        if len(data.get("recipe_ingredients")) != len(
            set(
                [
                    item["ingredient"].name
                    for item in data.get("recipe_ingredients")
                ]
            )
        ):
            raise serializers.ValidationError(
                "Recipe must have unique ingredients"
            )

        return data

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("recipe_ingredients")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        add_ingredients_to_recipe(recipe, ingredients)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("recipe_ingredients")
        instance.tags.set(tags)
        instance.recipe_ingredients.all().delete()
        add_ingredients_to_recipe(instance, ingredients)

        return super().update(instance, validated_data)


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    author = serializers.HiddenField(default=None)

    def validate_author(self, value):
        user_id = self.context["request"].parser_context["kwargs"]["id"]
        return get_object_or_404(User, pk=user_id)

    def validate(self, data):
        if data["user"] == data["author"]:
            raise serializers.ValidationError(
                "You can't subscribe to yourself"
            )
        return data

    class Meta:
        fields = ("user", "author")
        model = Subscription


class RecipeSmallSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
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
