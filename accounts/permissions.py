# accounts/permissions.py
from rest_framework.permissions import BasePermission
from accounts.models import UserRole
from django.conf import settings

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.STUDENT


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.TEACHER


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.ADMIN


class IsAuthenticatedOrValidAPIKey(BasePermission):
    message = "Authentication or a valid API key is required."

    def has_permission(self, request, view):
        # Allow authenticated users
        if request.user and request.user.is_authenticated:
            return True

        # Otherwise, check the API key
        api_key = request.query_params.get("api_key")

        return bool(
            api_key
            and settings.APP_API_SECRET_KEY
            and api_key == settings.APP_API_SECRET_KEY
        )

