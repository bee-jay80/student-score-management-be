from django.core.mail import send_mail
from accounts.models import User
from .tokens import email_verification_token
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string



def notify_admins_new_user(user):
    admins = User.objects.filter(role="ADMIN", is_active=True)
    emails = [admin.email for admin in admins]

    send_mail(
        subject="New account approval request",
        message=f"{user.email} requested access as {user.role}.",
        from_email=None,
        recipient_list=emails,
    )

def send_approval_email(user):
    """send email that confirms the user as been approved by admin"""
    send_mail(
        subject="Your account has been approved",
        message="Your account has been approved by the admin. You can now log in.",
        from_email=None,
        recipient_list=[user.email],
    )

def send_rejection_email(user):
    """send email that informs the user that their account has been rejected by admin"""
    send_mail(
        subject="Your account request has been rejected",
        message="We regret to inform you that your account request has been rejected by the admin.",
        from_email=None,
        recipient_list=[user.email],
    )

def send_reset_password_link_email(user):
    token = email_verification_token.make_token(user)
    url = f"{settings.FRONTEND_URL}/verify-email?uid={user.id}&token={token}"

    send_mail(
        subject="Verify your email",
        message=f"Click to verify your email: {url}",
        from_email=None,
        recipient_list=[user.email],
    )



# OTP MAIL SENDER
def send_otp_email(user, otp):
    subject = "Verify your email"
    html_content = render_to_string(
        "emails/email_otp_verification.html",
        {"user": user, "otp": otp}
    )

    email = EmailMultiAlternatives(
        subject,
        to=[user.email],
        from_email=settings.DEFAULT_FROM_EMAIL
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
