from django.core.mail import send_mail
from .models import User
from .tokens import email_verification_token
from django.conf import settings


def set_jwt_cookies(response, access, refresh):
    response.set_cookie(
        key="access_token",
        value=access,
        httponly=True,
        samesite="Lax",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        samesite="Lax",
    )


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


def send_verification_otp(user, otp):
    send_mail(
        subject="Your email verification OTP",
        message=f"Your OTP for email verification is: {otp}",
        from_email=None,
        recipient_list=[user.email],
    )
