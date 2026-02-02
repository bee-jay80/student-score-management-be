from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from notifications.models.admin_notification import AdminNotification

from notifications.serializers.admin_notification import (
    AdminNotificationSerializer
)

from notifications.permissions import IsAdmin


class AdminNotificationListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        notifications = AdminNotification.objects.filter(
            is_read=False
        ).order_by("-created_at")

        serializer = AdminNotificationSerializer(notifications, many=True)
        return Response(serializer.data)
