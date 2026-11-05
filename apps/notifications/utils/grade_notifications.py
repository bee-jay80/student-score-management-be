from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_grade_notification_email(student, course_title, score, total_mark, remark):
    """Send email notification when a student receives a grade."""
    subject = f"You received a grade for {course_title}"
    html_content = render_to_string(
        "emails/email_grade_notification.html",
        {
            "student": student,
            "course_title": course_title,
            "score": score,
            "total_mark": total_mark,
            "remark": remark,
            "frontend_url": settings.FRONTEND_URL
        }
    )
    email = EmailMultiAlternatives(
        subject,
        to=[student.email],
        from_email=settings.DEFAULT_FROM_EMAIL
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
