from api.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeSerializer,
                             ShoppingCartSerializer,
                             SubscriptionListSerializer,
                             SubscriptionSerializer, TagSerializer)
from api.services import RecipeFilter, process_recipe_saving
from django.contrib.auth import get_user_model
from django.db.models import IntegerField, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    http_method_names = ["get", "post", "delete"]

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
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
    http_method_names = ["get"]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    filter_backends = [
        filters.OrderingFilter,
        RecipeFilter,
    ]
    permission_classes = (IsAdminOrReadOnly, IsOwnerOrReadOnly)
    http_method_names = [
        "get",
        "post",
        "delete",
        "patch",
    ]

    def get_queryset(self):
        return Recipe.objects.filter(author__is_active=True)

    def get_serializer_class(self):
        if self.action in ["create", "partial_update"]:
            return RecipeCreateSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        return process_recipe_saving(request, pk, FavoriteSerializer, Favorite)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        return process_recipe_saving(
            request, pk, ShoppingCartSerializer, ShoppingCart
        )

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        shopping_carts = (
            ShoppingCart.objects.filter(user=request.user)
            .values_list(
                "recipe__recipe_ingredients__ingredient__name",
                "recipe__recipe_ingredients__ingredient__measurement_unit",
            )
            .annotate(
                amount=Coalesce(
                    Sum(
                        "recipe__recipe_ingredients__amount",
                        output_field=IntegerField(),
                    ),
                    0,
                )
            )
        )

        with open("ingredients.txt", "w") as file:
            file.write("Список покупок" + "\n")
            for ingredient_name, units, amount in shopping_carts:
                file.write(f"{ingredient_name}: {amount} {units}" + "\n")

            response = HttpResponse(file, content_type="text/plain")
            response[
                "Content-Disposition"
            ] = 'attachment; filename="ingredients.txt"'

        return response


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)
    http_method_names = ["get"]
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get("name")
        if name:
            return Ingredient.objects.filter(name__icontains=name.lower())
        return super().get_queryset()
