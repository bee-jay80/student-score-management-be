from notifications.models.admin_notification import AdminNotification

def create_user_approval_notification(user, is_emailed):
    AdminNotification.objects.create(
        type=AdminNotification.USER_APPROVAL,
        related_user=user,
        is_emailed=is_emailed
    )