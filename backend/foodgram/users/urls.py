from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UsersListViewSet

router = DefaultRouter()

router.register("", UsersListViewSet)

urlpatterns = [
    path("", include(router.urls)),
]