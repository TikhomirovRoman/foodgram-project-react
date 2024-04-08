from rest_framework import permissions


class PasswordPermission(permissions.BasePermission):
    message = "неверный пароль"

    def has_permission(self, request, view):
        if request.user.check_password(request.data['current_password']):
            return True
        return False
