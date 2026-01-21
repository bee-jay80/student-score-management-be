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
