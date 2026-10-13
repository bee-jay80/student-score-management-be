from rest_framework import serializers
from notifications.models.student_field_update_notification import StudentFieldUpdateNotification
from accounts.models import User
from students.models import StudentFieldUpdateRequest


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email"]


class StudentFieldUpdateRequestBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFieldUpdateRequest
        fields = ["id", "requested_role", "status", "created_at"]


class StudentFieldUpdateNotificationSerializer(serializers.ModelSerializer):
    student_user = UserBasicSerializer(read_only=True)
    reviewer_user = UserBasicSerializer(read_only=True)
    field_update_request = StudentFieldUpdateRequestBasicSerializer(read_only=True)

    class Meta:
        model = StudentFieldUpdateNotification
        fields = [
            "id",
            "student_user",
            "reviewer_user",
            "field_update_request",
            "notification_type",
            "message",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["id", "student_user", "reviewer_user", "field_update_request", "created_at"]
