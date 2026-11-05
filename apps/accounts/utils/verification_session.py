# accounts/utils/verification_session.py
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

signer = TimestampSigner()

def create_verification_token(user_id):
    return signer.sign(str(user_id))


def verify_verification_token(token, max_age=900):  # 15 minutes
    try:
        user_id = signer.unsign(token, max_age=max_age)
        return user_id
    except (BadSignature, SignatureExpired):
        return None
