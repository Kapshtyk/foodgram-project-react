from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from api.serializers import (
    TagSerializer,
    RecipeSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
)
from recipes.models import (
    Tag,
    Recipe,
    Favorite,
    ShoppingCart,
    RecipeIngredient,
)

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    http_method_names = ["get", "post"]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    http_method_names = ["get"]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    http_method_names = ["get", "post", "delete", "patch"]

    @action(detail=True)
    def download_shopping_cart(self, request, pk):
        shopping_carts = ShoppingCart.objects.filter(user=self.request.user)

        ingredients = {}
        for shopping_cart in shopping_carts:
            recipe = shopping_cart.recipe
            recipe_ingredients = RecipeIngredient.objects.filter(recipe=recipe)

            for recipe_ingredient in recipe_ingredients:
                ingredient = recipe_ingredient.ingredient
                units = ingredient.measurement_unit
                quantity = recipe_ingredient.quantity
                if ingredient.name in ingredients:
                    ingredients[ingredient.name]["quantity"] += quantity
                else:
                    ingredients[ingredient.name] = {
                        "quantity": quantity,
                        "units": units,
                    }

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="ingredients.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        p.setFont(psfontname='Arial', size=14)

        y = 700
        for ingredient_name, ingredient_info in ingredients.items():
            quantity = ingredient_info["quantity"]
            units = ingredient_info["units"]
            p.drawString(100, y, f"{ingredient_name}: {quantity} {units}")
            y -= 20

        p.showPage()
        p.save()

        return response


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (AllowAny,)
    http_method_names = ["post", "delete"]

    def get_queryset(self):
        recipe_id = self.kwargs.get("recipe_id")
        get_object_or_404(Recipe, pk=recipe_id)
        return Favorite.objects.filter(recipe_id=recipe_id)

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get("recipe_id"))
        serializer.save(user=self.request.user, recipe=recipe)

    def perform_destroy(self, instance):
        instance.delete()

    class FavoriteViewSet(viewsets.ModelViewSet):
        queryset = Recipe.objects.all()
        serializer_class = FavoriteSerializer
        permission_classes = (IsAuthenticatedOrReadOnly,)
        http_method_names = ["post", "delete"]

        def get_queryset(self):
            recipe_id = self.kwargs.get("recipe_id")
            get_object_or_404(Recipe, pk=recipe_id)
            return Favorite.objects.filter(recipe_id=recipe_id)

        def perform_create(self, serializer):
            recipe = get_object_or_404(Recipe, id=self.kwargs.get("recipe_id"))
            serializer.save(user=self.request.user, recipe=recipe)

        def perform_destroy(self, instance):
            instance.delete()


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ["post", "delete"]

    def get_queryset(self):
        recipe_id = self.kwargs.get("recipe_id")
        get_object_or_404(Recipe, pk=recipe_id)
        return Favorite.objects.filter(recipe_id=recipe_id)

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get("recipe_id"))
        serializer.save(user=self.request.user, recipe=recipe)

    def perform_destroy(self, instance):
        instance.delete()
