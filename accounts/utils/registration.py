from django.utils import timezone
from datetime import timedelta
from accounts.models import User
# from accounts.utils.otp import generate_and_send_otp

from .emails import send_otp_email

from .cookies import set_pending_cookie

from .verification_session import create_verification_token

from .otp import create_otp

from rest_framework.response import Response
from rest_framework import status


OTP_EXPIRY_MINUTES = 15


def register_or_resend_otp(data):
    email = data["email"]

    user = User.objects.filter(email=email).first()

    if user:
        if user.is_email_verified:
            raise ValueError("Email already exists")

        # User exists but not verified → resend OTP
        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        user.email_verification_expires_at = (
            timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        )
        user.save()

        try:
            otp = create_otp(user, purpose="EMAIL_VERIFICATION")
            send_otp_email(user, otp)

            pending_token = create_verification_token(user.id)
            response = Response(
                {
                    "ststus":"success",
                    "detail": "Registration submitted, Verify OTP and Await Admin Approval. Await admin approval."
                },
                status=201
            )
            set_pending_cookie(response, pending_token)
        except Exception as e:
            # user.delete()
            response =  Response(
                {"detail": "Failed to send OTP email. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return user, response

    # New user
    user = User.objects.create_user(
        email=email,
        first_name=data["first_name"],
        last_name=data["last_name"],
        is_active=False,
    )

    user.email_verification_expires_at = (
        timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    )
    user.save()

    try:
        otp = create_otp(user, purpose="EMAIL_VERIFICATION")
        send_otp_email(user, otp)

        pending_token = create_verification_token(user.id)
        response = Response(
            {
                "ststus":"success",
                "detail": "Registration submitted, Verify OTP and Await Admin Approval. Await admin approval."
            },
            status=201
        )
        set_pending_cookie(response, pending_token)
    except Exception as e:
        # user.delete()
        response = Response(
            {"detail": "Failed to send OTP email. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return user, response
