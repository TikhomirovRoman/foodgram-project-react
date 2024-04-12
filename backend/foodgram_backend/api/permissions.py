from rest_framework import permissions


class PasswordPermission(permissions.BasePermission):
    message = "неверный пароль"

    def has_permission(self, request, view):
        return request.user.check_password(request.data['current_password'])


class AuthorOrReadOnly(permissions.BasePermission):
    message = 'AuthorOrReadOnly violeted'

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):

        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class ReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
