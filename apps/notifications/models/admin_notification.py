from django.db import models
from django.conf import settings
import uuid

class AdminNotification(models.Model):
    USER_APPROVAL = "user_approval"

    NOTIFICATION_TYPES = (
        (USER_APPROVAL, "User Approval"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    related_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_notifications"
    )
    is_read = models.BooleanField(default=False)
    is_emailed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
