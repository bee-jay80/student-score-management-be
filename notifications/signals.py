from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models.admin_notification import AdminNotification
User = get_user_model()


@receiver(post_save, sender=User)
def notify_admin_on_email_verification(sender, instance, created, **kwargs):
    if instance.is_email_verified and not instance.is_active:
        AdminNotification.objects.get_or_create(
            type="user_approval",
            related_user=instance
        )
