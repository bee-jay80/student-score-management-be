from rest_framework import serializers
from notifications.models.admin_notification import AdminNotification
from accounts.models import User


class PendingUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "role",
            "is_email_verified",
            "is_active",
            "created_at",
        )


class AdminNotificationSerializer(serializers.ModelSerializer):
    related_user = PendingUserSerializer(read_only=True)

    class Meta:
        model = AdminNotification
        fields = (
            "id",
            "type",
            "related_user",
            "is_read",
            "created_at",
        )
