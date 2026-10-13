from notifications.models.student_field_update_notification import StudentFieldUpdateNotification
from accounts.models import User, UserRole
import logging

logger = logging.getLogger(__name__)


def create_field_update_request_notifications(field_update_request):
    """
    When a student submits a field update request, create notifications for all admins and teachers.
    """
    student_user = field_update_request.student.user
    admin_teacher_users = User.objects.filter(role__in=[UserRole.ADMIN, UserRole.TEACHER])

    for user in admin_teacher_users:
        StudentFieldUpdateNotification.objects.create(
            student_user=student_user,
            reviewer_user=user,
            field_update_request=field_update_request,
            notification_type=StudentFieldUpdateNotification.NOTIFICATION_TYPE_REQUEST,
            is_emailed=False,
        )
    logger.info(f"Created field update request notifications for request {field_update_request.id}")


def create_field_update_approval_notification(field_update_request, reviewer, reviewer_message=""):
    """
    When an admin/teacher approves a field update request, notify the student.
    """
    StudentFieldUpdateNotification.objects.create(
        student_user=field_update_request.student.user,
        reviewer_user=reviewer,
        field_update_request=field_update_request,
        notification_type=StudentFieldUpdateNotification.NOTIFICATION_TYPE_APPROVED,
        message=reviewer_message,
        is_emailed=False,
    )
    logger.info(f"Created field update approval notification for request {field_update_request.id}")


def create_field_update_rejection_notification(field_update_request, reviewer, reviewer_message=""):
    """
    When an admin/teacher rejects a field update request, notify the student.
    """
    StudentFieldUpdateNotification.objects.create(
        student_user=field_update_request.student.user,
        reviewer_user=reviewer,
        field_update_request=field_update_request,
        notification_type=StudentFieldUpdateNotification.NOTIFICATION_TYPE_REJECTED,
        message=reviewer_message,
        is_emailed=False,
    )
    logger.info(f"Created field update rejection notification for request {field_update_request.id}")
