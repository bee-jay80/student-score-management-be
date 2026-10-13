from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import OpenApiResponse, extend_schema

from notifications.models.admin_notification import AdminNotification

from notifications.serializers.admin_notification import (
    AdminNotificationSerializer
)

from notifications.permissions import IsAdmin


class AdminNotificationListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        summary="List unread administrator notifications",
        description="Return unread notifications for administrators, newest first.",
        responses={
            200: AdminNotificationSerializer(many=True),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="Administrator access is required."),
        },
        tags=["Notifications"],
    )
    def get(self, request):
        notifications = AdminNotification.objects.filter(
            is_read=False
        ).order_by("-created_at")

        serializer = AdminNotificationSerializer(notifications, many=True)
        return Response(serializer.data)
