"""
Celery tasks for asynchronous email sending (optional).

To use these tasks, you need to:
1. Install Celery: pip install celery
2. Install Redis (or RabbitMQ): pip install redis
3. Configure CELERY_BROKER_URL in settings.py
4. Run Celery worker: celery -A config worker -l info

Then replace direct send_mail calls with these async tasks.
"""

try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    shared_task = lambda x: x  # No-op decorator if Celery not installed

import logging

logger = logging.getLogger(__name__)


if CELERY_AVAILABLE:
    @shared_task(bind=True, max_retries=3)
    def send_field_update_request_email_async(self, reviewer_email, reviewer_first_name, 
                                               student_first_name, student_last_name, 
                                               student_email, student_matric_no, 
                                               requested_role, message, approval_link):
        """
        Async task to send field update request email to admin/teacher.
        """
        try:
            from notifications.utils.email_sender import send_field_update_request_email
            send_field_update_request_email(
                reviewer_email=reviewer_email,
                reviewer_first_name=reviewer_first_name,
                student_first_name=student_first_name,
                student_last_name=student_last_name,
                student_email=student_email,
                student_matric_no=student_matric_no,
                requested_role=requested_role,
                message=message,
                approval_link=approval_link,
            )
            logger.info(f"Async: Field update request email sent to {reviewer_email}")
        except Exception as exc:
            logger.error(f"Async: Failed to send email to {reviewer_email}: {str(exc)}")
            # Retry with exponential backoff: 60s, 120s, 240s
            raise self.retry(exc=exc, countdown=2 ** self.request.retries * 60)

    @shared_task(bind=True, max_retries=3)
    def send_field_update_approval_email_async(self, student_email, student_first_name, 
                                                requested_role, reviewer_first_name, 
                                                reviewer_last_name, reviewer_message, 
                                                dashboard_link):
        """
        Async task to send field update approval email to student.
        """
        try:
            from notifications.utils.email_sender import send_field_update_approval_email
            send_field_update_approval_email(
                student_email=student_email,
                student_first_name=student_first_name,
                requested_role=requested_role,
                reviewer_first_name=reviewer_first_name,
                reviewer_last_name=reviewer_last_name,
                reviewer_message=reviewer_message,
                dashboard_link=dashboard_link,
            )
            logger.info(f"Async: Field update approval email sent to {student_email}")
        except Exception as exc:
            logger.error(f"Async: Failed to send approval email to {student_email}: {str(exc)}")
            raise self.retry(exc=exc, countdown=2 ** self.request.retries * 60)

    @shared_task(bind=True, max_retries=3)
    def send_field_update_rejection_email_async(self, student_email, student_first_name, 
                                                 requested_role, reviewer_first_name, 
                                                 reviewer_last_name, reviewer_message, 
                                                 dashboard_link):
        """
        Async task to send field update rejection email to student.
        """
        try:
            from notifications.utils.email_sender import send_field_update_rejection_email
            send_field_update_rejection_email(
                student_email=student_email,
                student_first_name=student_first_name,
                requested_role=requested_role,
                reviewer_first_name=reviewer_first_name,
                reviewer_last_name=reviewer_last_name,
                reviewer_message=reviewer_message,
                dashboard_link=dashboard_link,
            )
            logger.info(f"Async: Field update rejection email sent to {student_email}")
        except Exception as exc:
            logger.error(f"Async: Failed to send rejection email to {student_email}: {str(exc)}")
            raise self.retry(exc=exc, countdown=2 ** self.request.retries * 60)

else:
    # Fallback: Simple functions that log if Celery is not available
    def send_field_update_request_email_async(*args, **kwargs):
        logger.warning("Celery not available. Using synchronous email sending.")
        from notifications.utils.email_sender import send_field_update_request_email
        return send_field_update_request_email(*args, **kwargs)

    def send_field_update_approval_email_async(*args, **kwargs):
        logger.warning("Celery not available. Using synchronous email sending.")
        from notifications.utils.email_sender import send_field_update_approval_email
        return send_field_update_approval_email(*args, **kwargs)

    def send_field_update_rejection_email_async(*args, **kwargs):
        logger.warning("Celery not available. Using synchronous email sending.")
        from notifications.utils.email_sender import send_field_update_rejection_email
        return send_field_update_rejection_email(*args, **kwargs)
