from rest_framework.permissions import BasePermission
from accounts.models import UserRole


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and
            request.user.role == UserRole.TEACHER
        )
