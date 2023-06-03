from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from requests import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from api.serializers import TagSerializer, RecipeSerializer, FavoriteSerializer
from recipes.models import Tag, Recipe, Favorite

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
    http_method_names = ["get", "post", "delete", "patch"]


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
        http_method_names = ["DELETE", "post"]

        def get_queryset(self):
            recipe_id = self.kwargs.get("recipe_id")
            get_object_or_404(Recipe, pk=recipe_id)
            return Favorite.objects.filter(recipe_id=recipe_id)

        def perform_create(self, serializer):
            recipe = get_object_or_404(Recipe, id=self.kwargs.get("recipe_id"))
            serializer.save(user=self.request.user, recipe=recipe)

        def perform_destroy(self, instance):
            instance.delete()