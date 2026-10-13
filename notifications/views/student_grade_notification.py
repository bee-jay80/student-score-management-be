from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)

from notifications.models.student_grade_notification import StudentGradeNotification
from notifications.serializers.student_grade_notification import StudentGradeNotificationSerializer
from accounts.permissions import IsStudent


class StudentGradeNotificationListView(APIView):
    """List all grade notifications for the authenticated student."""
    permission_classes = [IsAuthenticated, IsStudent]

    @extend_schema(
        summary="List grade notifications",
        description="Return grade notifications belonging to the authenticated student.",
        responses={
            200: StudentGradeNotificationSerializer(many=True),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="Student access is required."),
        },
        tags=["Grade notifications"],
    )
    def get(self, request):
        notifications = StudentGradeNotification.objects.filter(
            student=request.user
        ).select_related('grade__enrollment__course')
        
        serializer = StudentGradeNotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentGradeNotificationDetailView(APIView):
    """Retrieve a specific grade notification and mark as read."""
    permission_classes = [IsAuthenticated, IsStudent]

    @extend_schema(
        summary="Retrieve a grade notification",
        description="Return a grade notification belonging to the authenticated student and mark it as read.",
        parameters=[
            OpenApiParameter(
                name="notification_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the grade notification.",
            ),
        ],
        responses={
            200: StudentGradeNotificationSerializer,
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="Student access is required."),
            404: OpenApiResponse(description="The notification was not found."),
        },
        tags=["Grade notifications"],
    )
    def get(self, request, notification_id):
        try:
            notification = StudentGradeNotification.objects.get(
                id=notification_id,
                student=request.user
            )
        except StudentGradeNotification.DoesNotExist:
            return Response(
                {"detail": "Notification not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Mark as read
        if not notification.is_read:
            notification.is_read = True
            notification.save()
        
        serializer = StudentGradeNotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentGradeNotificationUnreadCountView(APIView):
    """Get count of unread grade notifications for the authenticated student."""
    permission_classes = [IsAuthenticated, IsStudent]

    @extend_schema(
        summary="Count unread grade notifications",
        description="Return the number of unread grade notifications for the authenticated student.",
        responses={
            200: inline_serializer(
                name="UnreadGradeNotificationCount",
                fields={"unread_count": serializers.IntegerField()},
            ),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="Student access is required."),
        },
        tags=["Grade notifications"],
    )
    def get(self, request):
        unread_count = StudentGradeNotification.objects.filter(
            student=request.user,
            is_read=False
        ).count()
        
        return Response(
            {"unread_count": unread_count},
            status=status.HTTP_200_OK
        )


class MarkNotificationAsReadView(APIView):
    """Mark a notification as read."""
    permission_classes = [IsAuthenticated, IsStudent]

    @extend_schema(
        summary="Mark a grade notification as read",
        description="Mark a grade notification belonging to the authenticated student as read.",
        request=None,
        parameters=[
            OpenApiParameter(
                name="notification_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the grade notification.",
            ),
        ],
        responses={
            200: StudentGradeNotificationSerializer,
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="Student access is required."),
            404: OpenApiResponse(description="The notification was not found."),
        },
        tags=["Grade notifications"],
    )
    def put(self, request, notification_id):
        try:
            notification = StudentGradeNotification.objects.get(
                id=notification_id,
                student=request.user
            )
        except StudentGradeNotification.DoesNotExist:
            return Response(
                {"detail": "Notification not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        notification.is_read = True
        notification.save()
        
        serializer = StudentGradeNotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MarkAllNotificationsAsReadView(APIView):
    """Mark all notifications as read for the authenticated student."""
    permission_classes = [IsAuthenticated, IsStudent]

    @extend_schema(
        summary="Mark all grade notifications as read",
        description="Mark all unread grade notifications belonging to the authenticated student as read.",
        request=None,
        responses={
            200: inline_serializer(
                name="MarkAllGradeNotificationsReadResponse",
                fields={"message": serializers.CharField()},
            ),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="Student access is required."),
        },
        tags=["Grade notifications"],
    )
    def put(self, request):
        updated_count = StudentGradeNotification.objects.filter(
            student=request.user,
            is_read=False
        ).update(is_read=True)
        
        return Response(
            {"message": f"{updated_count} notification(s) marked as read."},
            status=status.HTTP_200_OK
        )
