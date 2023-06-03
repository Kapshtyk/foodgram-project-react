from django.contrib.auth import get_user_model
from djoser.views import UserViewSet as DjoserUserViewSet

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    ...
