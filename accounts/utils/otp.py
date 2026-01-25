# accounts/utils/otp.py
import secrets
from datetime import timedelta
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password, check_password
from accounts.models import EmailOTP

OTP_EXPIRY_MINUTES = 10
MAX_OTP_ATTEMPTS = 5

def generate_otp(length=6):
    return ''.join(str(secrets.randbelow(10)) for _ in range(length))


def create_otp(user, purpose):
    otp = generate_otp()
    EmailOTP.objects.create(
        user=user,
        otp_hash=make_password(otp),
        purpose=purpose,
        expires_at=now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
    )
    return otp


def verify_otp(user, submitted_otp, purpose):
    otp_record = EmailOTP.objects.filter(
        user=user,
        purpose=purpose,
        is_used=False,
    ).order_by("-created_at").first()

    if not otp_record:
        return False, "OTP not found"

    if now() > otp_record.expires_at:
        return False, "OTP expired"

    if otp_record.attempts >= MAX_OTP_ATTEMPTS:
        return False, "Too many attempts"

    if not check_password(submitted_otp, otp_record.otp_hash):
        otp_record.attempts += 1
        otp_record.save(update_fields=["attempts"])
        return False, "Invalid OTP"

    otp_record.is_used = True
    otp_record.save(update_fields=["is_used"])
    return True, "OTP verified"
