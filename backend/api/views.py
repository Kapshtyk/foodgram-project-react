from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from django.db.models import Q
from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.pagination import PageNumberPagination

from api.serializers import (
    TagSerializer,
    RecipeSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    SubscriptionSerializer,
    SubscriptionListSerializer,
    IngredientSerializer,
)
from recipes.models import (
    Tag,
    Recipe,
    Favorite,
    ShoppingCart,
    Ingredient,
    RecipeIngredient,
)
from users.models import Subscription

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    http_method_names = ["get", "post"]
    pagination_class = PageNumberPagination

    @action(detail=False, methods=["get"])
    def subscriptions(self, request):
        queryset = Subscription.objects.filter(user=request.user)
        paginator = PageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = SubscriptionListSerializer(
            paginated_queryset, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    http_method_names = ["get"]
    pagination_class = None


class RecipeFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        is_in_shopping_cart = request.query_params.get("is_in_shopping_cart")
        is_favorited = request.query_params.get("is_favorited")
        author = request.query_params.get("author")
        tags = request.query_params.getlist("tags")
        print(tags)

        if is_in_shopping_cart == "1":
            return queryset.filter(shopping_cart__user=request.user)
        elif is_favorited == "1":
            return queryset.filter(favorites__user=request.user)
        elif author:
            return queryset.filter(author__id=author)
        elif tags:
            return queryset.filter(tags__slug__in=tags).distinct()
        else:
            return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)
    filter_backends = [filters.OrderingFilter, RecipeFilter]
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
                amount = recipe_ingredient.amount
                if ingredient.name in ingredients:
                    ingredients[ingredient.name]["amount"] += amount
                else:
                    ingredients[ingredient.name] = {
                        "amount": amount,
                        "units": units,
                    }

        response = HttpResponse(content_type="application/pdf")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="ingredients.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        p.setFont(psfontname="Arial", size=14)

        y = 700
        for ingredient_name, ingredient_info in ingredients.items():
            amount = ingredient_info["amount"]
            units = ingredient_info["units"]
            p.drawString(100, y, f"{ingredient_name}: {amount} {units}")
            y -= 20

        p.showPage()
        p.save()

        return response


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (AllowAny,)
    http_method_names = ["post", "delete"]
    pagination_class = None

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
    pagination_class = None

    def get_queryset(self):
        recipe_id = self.kwargs.get("recipe_id")
        get_object_or_404(Recipe, pk=recipe_id)
        return Favorite.objects.filter(recipe_id=recipe_id)

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get("recipe_id"))
        serializer.save(user=self.request.user, recipe=recipe)

    def perform_destroy(self, instance):
        instance.delete()


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)
    http_method_names = ["get"]
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get("name")
        if name:
            return Ingredient.objects.filter(Q(name__icontains=name.lower()))
        return super().get_queryset()


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ["post", "delete"]
    pagination_class = None

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        get_object_or_404(User, pk=user_id)
        return Subscription.objects.filter(user_id=user_id)

    def perform_create(self, serializer):
        user = get_object_or_404(User, id=self.kwargs.get("user_id"))
        serializer.save(author=self.request.user, user=user)

    def perform_destroy(self, instance):
        instance.delete()
