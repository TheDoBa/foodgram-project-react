from rest_framework import permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешение только администратору."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class IsAuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    """Разрешение только автору."""

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
