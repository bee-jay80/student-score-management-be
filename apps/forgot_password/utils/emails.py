# from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_forgot_password_otp_email(user, otp):
    """send email that contains OTP for password reset"""
    subject = "Password Reset OTP"
    html_content = render_to_string(
        "emails/email_forgot_password_otp.html",
        {"user": user, "otp": otp}
    )
    # Fallback plain text
    text_content = strip_tags(html_content) if html_content else f"Your password reset code is: {otp}"

    msg = EmailMultiAlternatives(subject, text_content, to=[user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)