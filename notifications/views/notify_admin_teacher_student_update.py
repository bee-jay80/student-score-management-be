"""
Centralized notification handler for student field update requests.
This module coordinates email and in-app notifications for:
1. Students requesting to add a course role
2. Admins/teachers reviewing requests
3. Students receiving approval/rejection decisions
"""

from django.conf import settings
import logging
from notifications.services.student_field_update_notifier import (
    create_field_update_request_notifications,
    create_field_update_approval_notification,
    create_field_update_rejection_notification,
)
from notifications import tasks as notification_tasks
from notifications.utils import email_sender

logger = logging.getLogger(__name__)


def notify_admins_teachers_of_field_update_request(field_update_request):
    """
    Send email and create in-app notifications when a student requests to add a field/course role.
    
    Args:
        field_update_request: StudentFieldUpdateRequest instance
    """
    student = field_update_request.student
    student_user = student.user

    # Create in-app notifications for all admins and teachers
    create_field_update_request_notifications(field_update_request)

    # Send email to all admins and teachers
    from accounts.models import User, UserRole

    admin_teacher_users = User.objects.filter(
        role__in=[UserRole.ADMIN, UserRole.TEACHER]
    )

    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    approval_link = f"{frontend_url}/admin/field-requests/{field_update_request.id}"

    for user in admin_teacher_users:
        try:
            # Use Celery task when available, otherwise the task will fall back to synchronous send
            if getattr(notification_tasks, "CELERY_AVAILABLE", False):
                notification_tasks.send_field_update_request_email_async.delay(
                    reviewer_email=user.email,
                    reviewer_first_name=user.first_name,
                    student_first_name=student_user.first_name,
                    student_last_name=student_user.last_name,
                    student_email=student_user.email,
                    student_matric_no=student.matric_no,
                    requested_role=str(field_update_request.requested_role),
                    message=field_update_request.message,
                    approval_link=approval_link,
                )
            else:
                # Fallback synchronous call
                notification_tasks.send_field_update_request_email_async(
                    reviewer_email=user.email,
                    reviewer_first_name=user.first_name,
                    student_first_name=student_user.first_name,
                    student_last_name=student_user.last_name,
                    student_email=student_user.email,
                    student_matric_no=student.matric_no,
                    requested_role=field_update_request.requested_role,
                    message=field_update_request.message,
                    approval_link=approval_link,
                )
        except Exception as e:
            logger.error(f"Failed to queue/send notification email to {user.email}: {str(e)}")


def notify_student_of_field_update_approval(field_update_request, reviewer, reviewer_message=""):
    """
    Send email and create in-app notification when a student's field update request is approved.
    
    Args:
        field_update_request: StudentFieldUpdateRequest instance
        reviewer: User instance who approved the request
        reviewer_message: Optional message from reviewer
    """
    student_user = field_update_request.student.user

    # Create in-app notification
    create_field_update_approval_notification(field_update_request, reviewer, reviewer_message)

    # Send email to student
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    dashboard_link = f"{frontend_url}/student/dashboard"

    try:
        if getattr(notification_tasks, "CELERY_AVAILABLE", False):
            notification_tasks.send_field_update_approval_email_async.delay(
                student_email=student_user.email,
                student_first_name=student_user.first_name,
                requested_role=str(field_update_request.requested_role),
                reviewer_first_name=reviewer.first_name,
                reviewer_last_name=reviewer.last_name,
                reviewer_message=reviewer_message,
                dashboard_link=dashboard_link,
            )
        else:
            notification_tasks.send_field_update_approval_email_async(
                student_email=student_user.email,
                student_first_name=student_user.first_name,
                requested_role=field_update_request.requested_role,
                reviewer_first_name=reviewer.first_name,
                reviewer_last_name=reviewer.last_name,
                reviewer_message=reviewer_message,
                dashboard_link=dashboard_link,
            )
        logger.info(f"Approval email queued/sent to {student_user.email} for request {field_update_request.id}")
    except Exception as e:
        logger.error(f"Failed to queue/send approval email for request {field_update_request.id}: {str(e)}")


def notify_student_of_field_update_rejection(field_update_request, reviewer, reviewer_message=""):
    """
    Send email and create in-app notification when a student's field update request is rejected.
    
    Args:
        field_update_request: StudentFieldUpdateRequest instance
        reviewer: User instance who rejected the request
        reviewer_message: Optional message from reviewer (e.g., reason for rejection)
    """
    student_user = field_update_request.student.user

    # Create in-app notification
    create_field_update_rejection_notification(field_update_request, reviewer, reviewer_message)

    # Send email to student
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    dashboard_link = f"{frontend_url}/student/dashboard"

    try:
        if getattr(notification_tasks, "CELERY_AVAILABLE", False):
            notification_tasks.send_field_update_rejection_email_async.delay(
                student_email=student_user.email,
                student_first_name=student_user.first_name,
                requested_role=str(field_update_request.requested_role),
                reviewer_first_name=reviewer.first_name,
                reviewer_last_name=reviewer.last_name,
                reviewer_message=reviewer_message,
                dashboard_link=dashboard_link,
            )
        else:
            notification_tasks.send_field_update_rejection_email_async(
                student_email=student_user.email,
                student_first_name=student_user.first_name,
                requested_role=field_update_request.requested_role,
                reviewer_first_name=reviewer.first_name,
                reviewer_last_name=reviewer.last_name,
                reviewer_message=reviewer_message,
                dashboard_link=dashboard_link,
            )
        logger.info(f"Rejection email queued/sent to {student_user.email} for request {field_update_request.id}")
    except Exception as e:
        logger.error(f"Failed to queue/send rejection email for request {field_update_request.id}: {str(e)}")
