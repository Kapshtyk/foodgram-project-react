from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import FavoriteViewSet, UserViewSet, TagViewSet, RecipeViewSet

app_name = "api"

router = DefaultRouter()

router.register(
    r"recipes/(?P<recipe_id>[\d.]+)/favorite",
    FavoriteViewSet,
    basename="favorite",
)
router.register(
    r"recipes/(?P<recipe_id>[\d.]+)", RecipeViewSet, basename="recipes"
)
router.register("tags", TagViewSet, basename="tags")
router.register("users", UserViewSet, basename="users")

urlpatterns = (
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
)
