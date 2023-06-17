from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrIsAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "POST" and request.user:
            return True
        if request.user and request.user.is_staff:
            return True
        return request.method in SAFE_METHODS or obj.author == request.user


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_staff
        )
