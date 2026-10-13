from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers, status
from rest_framework.pagination import PageNumberPagination
from notifications.models.student_field_update_notification import StudentFieldUpdateNotification
from notifications.serializers.student_field_update_notification import StudentFieldUpdateNotificationSerializer
from accounts.models import UserRole
from rest_framework.exceptions import PermissionDenied
from notifications.throttles import NotificationListThrottle
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)


def _paginated_field_update_notifications():
    return inline_serializer(
        name="PaginatedStudentFieldUpdateNotifications",
        fields={
            "count": serializers.IntegerField(),
            "next": serializers.URLField(allow_null=True),
            "previous": serializers.URLField(allow_null=True),
            "results": StudentFieldUpdateNotificationSerializer(many=True),
        },
    )


class StudentFieldUpdateNotificationListView(APIView):
    """
    Students see notifications about their field update requests:
    - When their request is created (seen by admins/teachers)
    - When their request is approved/rejected
    """
    permission_classes = [IsAuthenticated]

    throttle_classes = [NotificationListThrottle]

    @extend_schema(
        summary="List student field-update notifications",
        description="Return the authenticated student's field-update notifications, newest first, in pages of 20.",
        parameters=[
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number to retrieve.",
            ),
        ],
        responses={
            200: _paginated_field_update_notifications(),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="Only students may access this list."),
        },
        tags=["Field-update notifications"],
    )
    def get(self, request):
        if request.user.role != UserRole.STUDENT:
            raise PermissionDenied("Only students can access their field update notifications")

        qs = StudentFieldUpdateNotification.objects.filter(
            student_user=request.user
        ).select_related('reviewer_user', 'field_update_request')
        qs = qs.order_by("-created_at")

        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(qs, request)
        serializer = StudentFieldUpdateNotificationSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Mark a student field-update notification as read",
        description=(
            "When the view receives a notification ID, it marks the notification as read and returns it. "
            "The current list route does not provide that ID, so requests through that route return not found."
        ),
        request=None,
        responses={
            200: StudentFieldUpdateNotificationSerializer,
            404: OpenApiResponse(description="The notification was not found."),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="The notification does not belong to the current student."),
        },
        tags=["Field-update notifications"],
    )
    def post(self, request, notification_id=None):
        """Mark a notification as read"""
        try:
            notification = StudentFieldUpdateNotification.objects.get(id=notification_id)
        except StudentFieldUpdateNotification.DoesNotExist:
            return Response({"detail": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)

        if notification.student_user != request.user:
            raise PermissionDenied("You cannot mark this notification as read")

        notification.is_read = True
        notification.save()
        serializer = StudentFieldUpdateNotificationSerializer(notification)
        return Response(serializer.data)


class AdminTeacherFieldUpdateNotificationListView(APIView):
    """
    Admins and teachers see notifications about student field update requests they need to review.
    """
    permission_classes = [IsAuthenticated]

    throttle_classes = [NotificationListThrottle]

    @extend_schema(
        summary="List field-update notifications for reviewers",
        description="Return unread field-update notifications assigned to the authenticated administrator or teacher, newest first, in pages of 30.",
        parameters=[
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number to retrieve.",
            ),
        ],
        responses={
            200: inline_serializer(
                name="PaginatedReviewerFieldUpdateNotifications",
                fields={
                    "count": serializers.IntegerField(),
                    "next": serializers.URLField(allow_null=True),
                    "previous": serializers.URLField(allow_null=True),
                    "results": StudentFieldUpdateNotificationSerializer(many=True),
                },
            ),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="Only administrators and teachers may access this list."),
        },
        tags=["Field-update notifications"],
    )
    def get(self, request):
        if request.user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
            raise PermissionDenied("Only admins and teachers can access field update request notifications")

        # Unread notifications for this admin/teacher
        qs = StudentFieldUpdateNotification.objects.filter(
            reviewer_user=request.user,
            is_read=False
        ).select_related('student_user', 'field_update_request', 'field_update_request__requested_role')
        qs = qs.order_by("-created_at")

        paginator = PageNumberPagination()
        paginator.page_size = 30
        page = paginator.paginate_queryset(qs, request)
        serializer = StudentFieldUpdateNotificationSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Mark a reviewer field-update notification as read",
        description=(
            "When the view receives a notification ID, it marks the notification as read and returns it. "
            "The current reviewer list route does not provide that ID, so requests through that route return not found."
        ),
        request=None,
        responses={
            200: StudentFieldUpdateNotificationSerializer,
            404: OpenApiResponse(description="The notification was not found."),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="The notification is not assigned to the current reviewer."),
        },
        tags=["Field-update notifications"],
    )
    def post(self, request, notification_id=None):
        """Mark a notification as read"""
        try:
            notification = StudentFieldUpdateNotification.objects.get(id=notification_id)
        except StudentFieldUpdateNotification.DoesNotExist:
            return Response({"detail": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)

        if notification.reviewer_user != request.user:
            raise PermissionDenied("You cannot mark this notification as read")

        notification.is_read = True
        notification.save()
        serializer = StudentFieldUpdateNotificationSerializer(notification)
        return Response(serializer.data)


class FieldUpdateNotificationDetailView(APIView):
    """Get a single notification detail"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Retrieve a field-update notification",
        description="Return a notification accessible to its student or assigned reviewer.",
        parameters=[
            OpenApiParameter(
                name="notification_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the field-update notification.",
            ),
        ],
        responses={
            200: StudentFieldUpdateNotificationSerializer,
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="The user is neither the student nor the assigned reviewer."),
            404: OpenApiResponse(description="The notification was not found."),
        },
        tags=["Field-update notifications"],
    )
    def get(self, request, notification_id):
        try:
            notification = StudentFieldUpdateNotification.objects.get(id=notification_id)
        except StudentFieldUpdateNotification.DoesNotExist:
            return Response({"detail": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check permission: either the student or the reviewer
        if not (notification.student_user == request.user or notification.reviewer_user == request.user):
            raise PermissionDenied("You do not have access to this notification")

        serializer = StudentFieldUpdateNotificationSerializer(notification)
        return Response(serializer.data)


class StudentFieldUpdateNotificationUnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Count unread student field-update notifications",
        description="Return the number of unread field-update notifications for the authenticated student.",
        responses={
            200: inline_serializer(
                name="StudentFieldUpdateUnreadCount",
                fields={"unread_count": serializers.IntegerField()},
            ),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="Only students may access this count."),
        },
        tags=["Field-update notifications"],
    )
    def get(self, request):
        if request.user.role != UserRole.STUDENT:
            raise PermissionDenied("Only students can access this endpoint")

        count = StudentFieldUpdateNotification.objects.filter(student_user=request.user, is_read=False).count()
        return Response({"unread_count": count})


class AdminTeacherFieldUpdateNotificationUnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Count unread reviewer field-update notifications",
        description="Return the number of unread field-update notifications assigned to the authenticated administrator or teacher.",
        responses={
            200: inline_serializer(
                name="ReviewerFieldUpdateUnreadCount",
                fields={"unread_count": serializers.IntegerField()},
            ),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="Only administrators and teachers may access this count."),
        },
        tags=["Field-update notifications"],
    )
    def get(self, request):
        if request.user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
            raise PermissionDenied("Only admins and teachers can access this endpoint")

        count = StudentFieldUpdateNotification.objects.filter(reviewer_user=request.user, is_read=False).count()
        return Response({"unread_count": count})
