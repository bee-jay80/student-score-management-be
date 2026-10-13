from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Student
from .serializers import StudentSerializer
from rest_framework.permissions import IsAuthenticated
from notifications.throttles import NotificationListThrottle

from .permissions import IsStudentOrAdminOrTeacher, IsStudentOwnerOrAdminOrTeacher
from .models import StudentFieldUpdateRequest
from courses.models import CourseRole
from .serializers import StudentFieldUpdateRequestSerializer, AdminStudentFieldUpdateRequestSerializer
from accounts.models import UserRole, User
from rest_framework.exceptions import PermissionDenied
from notifications.views.notify_admin_teacher_student_update import (
    notify_admins_teachers_of_field_update_request,
    notify_student_of_field_update_approval,
    notify_student_of_field_update_rejection,
)

class StudentCreateView(APIView):
    permission_classes = [IsAuthenticated, IsStudentOrAdminOrTeacher]

    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class StudentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsStudentOwnerOrAdminOrTeacher]

    def get(self, request, student_id):
        try:
            # Eager-load related user and roles to avoid N+1
            student = Student.objects.select_related('user').prefetch_related('fields').get(id=student_id)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        # If the payload includes a requested role id, create a request instead of applying immediately
        requested_role_id = request.data.get("requested_role_id")
        message = request.data.get("message", "")

        # Only the student themself should create a request for their profile
        if requested_role_id:
            if not (request.user == student.user or request.user.role in (UserRole.ADMIN, UserRole.TEACHER)):
                raise PermissionDenied("You do not have permission to request this change.")

            try:
                role = CourseRole.objects.get(id=requested_role_id)
            except Exception:
                return Response({"detail": "Requested role not found."}, status=status.HTTP_400_BAD_REQUEST)

            req = StudentFieldUpdateRequest.objects.create(
                student=student,
                requested_role=role,
                message=message,
            )

            # Send notifications to admins and teachers (both email and in-app)
            notify_admins_teachers_of_field_update_request(req)

            serializer = StudentFieldUpdateRequestSerializer(req)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        serializer = StudentSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentFieldUpdateRequestListView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [NotificationListThrottle]

    def get(self, request):
        # Only teachers and admins can view student field update requests
        if request.user.role not in (UserRole.TEACHER, UserRole.ADMIN):
            raise PermissionDenied("Not authorized")
        qs = StudentFieldUpdateRequest.objects.select_related('student__user', 'requested_role', 'reviewed_by').order_by("-created_at")

        paginator = PageNumberPagination()
        paginator.page_size = 25
        page = paginator.paginate_queryset(qs, request)
        serializer = AdminStudentFieldUpdateRequestSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class StudentFieldUpdateRequestActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        # Only teachers and admins can approve/reject
        if request.user.role not in (UserRole.TEACHER, UserRole.ADMIN):
            raise PermissionDenied("Not authorized")

        try:
            req = StudentFieldUpdateRequest.objects.get(id=request_id)
        except StudentFieldUpdateRequest.DoesNotExist:
            return Response({"detail": "Request not found."}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get("action")
        reviewer_message = request.data.get("message", "")

        if action == "approve":
            req.approve(request.user)
            # Notify student of approval (both email and in-app)
            notify_student_of_field_update_approval(req, request.user, reviewer_message)
        elif action == "reject":
            req.reject(request.user)
            # Notify student of rejection (both email and in-app)
            notify_student_of_field_update_rejection(req, request.user, reviewer_message)
        else:
            return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AdminStudentFieldUpdateRequestSerializer(req)
        return Response(serializer.data)