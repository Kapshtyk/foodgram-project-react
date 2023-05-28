from django.http import JsonResponse
from .serializers import UsersSerializer
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

User = get_user_model()


class UsersListViewSet(viewsets.ModelViewSet):
    serializer_class = UsersSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]
