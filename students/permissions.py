from rest_framework.permissions import BasePermission

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "STUDENT"
        )


class IsStudentOwner(BasePermission):
    """
    Student can only access their own profile/data
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


from accounts.models import UserRole


class IsStudentOrAdminOrTeacher(BasePermission):
    """Allow access if user is authenticated and has role student, teacher or admin."""

    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and
            request.user.role in (UserRole.STUDENT, UserRole.TEACHER, UserRole.ADMIN)
        )


class IsStudentOwnerOrAdminOrTeacher(BasePermission):
    """Object-level: allow owner, admin or teacher access to student objects."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            obj.user == request.user or
            request.user.role in (UserRole.ADMIN, UserRole.TEACHER)
        )
