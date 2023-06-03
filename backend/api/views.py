from django.contrib.auth import get_user_model
from django.forms import ValidationError
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from api.serializers import TagSerializer, RecipeSerializer
from recipes.models import Tag, Recipe

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
