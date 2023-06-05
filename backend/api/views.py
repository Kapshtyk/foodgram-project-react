from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeSerializer, ShoppingCartSerializer,
                             SubscriptionListSerializer,
                             SubscriptionSerializer, TagSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription

from .services import RecipeFilter, process_recipe_saving

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    http_method_names = ["get", "post", "delete"]
    pagination_class = PageNumberPagination

    @action(detail=True, methods=["post", "delete"])
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == "POST":
            serializer = SubscriptionSerializer(
                data={
                    "author": author.id,
                    "user": request.user.id,
                },
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        Subscription.objects.filter(author=author, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def subscriptions(self, request):
        queryset = Subscription.objects.filter(user=request.user)
        paginator = PageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = SubscriptionListSerializer(
            paginated_queryset,
            many=True,
            context={"request": request},
        )
        return paginator.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    http_method_names = ["get"]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)
    filter_backends = [
        filters.OrderingFilter,
        RecipeFilter,
    ]
    http_method_names = [
        "get",
        "post",
        "delete",
        "patch",
    ]

    @action(detail=True, methods=["post", "delete"])
    def favorite(self, request, pk):
        return process_recipe_saving(request, pk, FavoriteSerializer, Favorite)

    @action(detail=True, methods=["post", "delete"])
    def shopping_cart(self, request, pk):
        return process_recipe_saving(
            request, pk, ShoppingCartSerializer, ShoppingCart
        )

    @action(detail=False, methods=["get"])
    def download_shopping_cart(self, request):
        shopping_carts = ShoppingCart.objects.filter(user=request.user)

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
        response["Content-Disposition"] = 'attachment; filename="ingredients.pdf"'

        p = canvas.Canvas(response, pagesize=A4)

        y = 700
        for ingredient_name, ingredient_info in ingredients.items():
            amount = ingredient_info["amount"]
            units = ingredient_info["units"]
            p.drawString(100, y, f"{ingredient_name}: {amount} {units}")
            y -= 20

        p.showPage()
        p.save()

        return response


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
            return Ingredient.objects.filter(name__icontains=name.lower())
        return super().get_queryset()
