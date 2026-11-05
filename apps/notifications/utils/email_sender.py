"""
Email utility module for field update notifications.
Handles sending HTML emails with template rendering.
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_field_update_request_email(reviewer_email, reviewer_first_name, student_first_name, 
                                     student_last_name, student_email, student_matric_no, 
                                     requested_role, message, approval_link):
    """
    Send HTML email to admin/teacher when student requests a field update.
    
    Args:
        reviewer_email: Email of the admin/teacher receiving the request
        reviewer_first_name: First name of reviewer
        student_first_name: First name of student making request
        student_last_name: Last name of student
        student_email: Email of student
        student_matric_no: Matric number of student
        requested_role: Name of the requested course role
        message: Optional message from student
        approval_link: Link to review/approve/reject the request
    """
    context = {
        'reviewer_first_name': reviewer_first_name,
        'student_first_name': student_first_name,
        'student_last_name': student_last_name,
        'student_email': student_email,
        'student_matric_no': student_matric_no,
        'requested_role': str(requested_role),
        'message': message,
        'approval_link': approval_link,
        'created_at': __import__('django.utils.timezone', fromlist=['now']).now().strftime('%B %d, %Y at %I:%M %p'),
    }

    subject = f"📋 New Field Update Request from {student_email}"
    
    html_content = render_to_string(
        "emails/email_field_update_request.html",
        context
    )
    
    email = EmailMultiAlternatives(
        subject=subject,
        body="New field update request",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[reviewer_email]
    )
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send(fail_silently=False)
        logger.info(f"Field update request email sent to {reviewer_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send field update request email to {reviewer_email}: {str(e)}")
        return False


def send_field_update_approval_email(student_email, student_first_name, requested_role, 
                                     reviewer_first_name, reviewer_last_name, 
                                     reviewer_message, dashboard_link):
    """
    Send HTML email to student when their field update request is approved.
    
    Args:
        student_email: Email of the student
        student_first_name: First name of student
        requested_role: Name of the approved role
        reviewer_first_name: First name of reviewer who approved
        reviewer_last_name: Last name of reviewer
        reviewer_message: Optional message from reviewer
        dashboard_link: Link to student dashboard
    """
    context = {
        'student_first_name': student_first_name,
        'requested_role': str(requested_role),
        'reviewer_first_name': reviewer_first_name,
        'reviewer_last_name': reviewer_last_name,
        'reviewer_message': reviewer_message,
        'dashboard_link': dashboard_link,
        'approved_at': __import__('django.utils.timezone', fromlist=['now']).now().strftime('%B %d, %Y at %I:%M %p'),
    }

    subject = f"✅ Your Field Update Request Has Been Approved!"
    
    html_content = render_to_string(
        "emails/email_field_update_approved.html",
        context
    )
    
    email = EmailMultiAlternatives(
        subject=subject,
        body="Your field update request has been approved",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[student_email]
    )
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send(fail_silently=False)
        logger.info(f"Field update approval email sent to {student_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send field update approval email to {student_email}: {str(e)}")
        return False


def send_field_update_rejection_email(student_email, student_first_name, requested_role, 
                                      reviewer_first_name, reviewer_last_name, 
                                      reviewer_message, dashboard_link):
    """
    Send HTML email to student when their field update request is rejected.
    
    Args:
        student_email: Email of the student
        student_first_name: First name of student
        requested_role: Name of the rejected role
        reviewer_first_name: First name of reviewer who rejected
        reviewer_last_name: Last name of reviewer
        reviewer_message: Optional message from reviewer explaining rejection
        dashboard_link: Link to student dashboard
    """
    context = {
        'student_first_name': student_first_name,
        'requested_role': str(requested_role),
        'reviewer_first_name': reviewer_first_name,
        'reviewer_last_name': reviewer_last_name,
        'reviewer_message': reviewer_message,
        'dashboard_link': dashboard_link,
        'reviewed_at': __import__('django.utils.timezone', fromlist=['now']).now().strftime('%B %d, %Y at %I:%M %p'),
    }

    subject = f"❌ Your Field Update Request Has Been Rejected"
    
    html_content = render_to_string(
        "emails/email_field_update_rejected.html",
        context
    )
    
    email = EmailMultiAlternatives(
        subject=subject,
        body="Your field update request has been rejected",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[student_email]
    )
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send(fail_silently=False)
        logger.info(f"Field update rejection email sent to {student_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send field update rejection email to {student_email}: {str(e)}")
        return False
