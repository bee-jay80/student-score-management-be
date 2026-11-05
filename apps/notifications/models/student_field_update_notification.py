from django.db import models
from django.conf import settings
import uuid


class StudentFieldUpdateNotification(models.Model):
    NOTIFICATION_TYPE_REQUEST = "field_update_request"
    NOTIFICATION_TYPE_APPROVED = "field_update_approved"
    NOTIFICATION_TYPE_REJECTED = "field_update_rejected"

    NOTIFICATION_TYPES = (
        (NOTIFICATION_TYPE_REQUEST, "Field Update Request"),
        (NOTIFICATION_TYPE_APPROVED, "Field Update Approved"),
        (NOTIFICATION_TYPE_REJECTED, "Field Update Rejected"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # The student making the request or receiving the decision
    student_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="field_update_notifications"
    )
    # The admin/teacher reviewing (null if notification is for student about request)
    reviewer_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="field_update_reviewed_notifications"
    )
    # Link to the actual request
    field_update_request = models.ForeignKey(
        'students.StudentFieldUpdateRequest',
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.TextField(blank=True)  # Optional reviewer message
    is_read = models.BooleanField(default=False)
    is_emailed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student_user', 'is_read']),
            models.Index(fields=['reviewer_user', 'is_read']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Field Update Notification - {self.student_user.email} - {self.notification_type}"
