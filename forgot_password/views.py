from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .utils.emails import send_forgot_password_otp_email
from accounts.utils.otp import create_otp, verify_otp
from accounts.utils.verification_session import create_verification_token, verify_verification_token
from accounts.utils.cookies import set_pending_cookie
from .serializers import ForgotPasswordSerializer, ResetPasswordSerializer, OTPVerifySerializer
from .models import ForgotPasswordRequest
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.hashers import make_password
from django.core.cache import cache

User = get_user_model()


class ForgotPasswordRequestView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"detail": "Email not found."},
                status=status.HTTP_200_OK,
            )

        try:
            # rate limit: max 5 requests per 15 minutes per email using cache
            cache_key = f"forgot_otp:{email}"
            count = cache.get(cache_key)
            if count is None:
                cache.set(cache_key, 1, 15 * 60)
            else:
                if count >= 5:
                    return Response({"detail": "Too many OTP requests. Try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
                try:
                    cache.incr(cache_key)
                except Exception:
                    # Fallback to set if incr not supported
                    cache.set(cache_key, int(count) + 1, 15 * 60)

            otp = create_otp(user, purpose="FORGOT_PASSWORD")
            send_forgot_password_otp_email(user, otp)
            pending_token = create_verification_token(user.id)
            # store a hash of the OTP rather than plaintext
            otp_hash = make_password(otp)
            ForgotPasswordRequest.objects.create(email=email, otp_hash=otp_hash)
            response = Response(
                {"detail": "OTP sent to email."},
                status=status.HTTP_200_OK,
            )
            set_pending_cookie(response, pending_token)
            return response
        except Exception as e:
            return Response(
                {"detail": "Failed to send OTP email. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OTPVerifyView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data["otp"]

        try:
            user_id = verify_verification_token(request.COOKIES.get("verification_session"))
            user = User.objects.get(id=user_id)
        except Exception:
            return Response(
                {"detail": "Invalid or expired verification session."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        success, message = verify_otp(user, otp, purpose="FORGOT_PASSWORD")
        if not success:
            return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)

        response = Response(
            {"detail": "OTP verified. You can now reset your password."},
            status=status.HTTP_200_OK,
        )
        # Mark the most recent unused forgot-password request for this email as used.
        forgot_password_request = ForgotPasswordRequest.objects.filter(email=user.email, is_used=False).order_by("-created_at").first()
        if forgot_password_request:
            forgot_password_request.is_used = True
            forgot_password_request.save(update_fields=["is_used"])

        pending_token = create_verification_token(user.id)
        set_pending_cookie(response, pending_token)
        return response

class ResetPasswordView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data["new_password"]

        try:
            user_id = verify_verification_token(request.COOKIES.get("verification_session"))
            user = User.objects.get(id=user_id)
        except Exception:
            return Response(
                {"detail": "Invalid or expired verification session."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        forgot_password_request = ForgotPasswordRequest.objects.filter(email=user.email, is_used=True).last()
        if not forgot_password_request:
            return Response(
                {"detail": "OTP verification required before resetting password."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(new_password)
        user.save()
        # Delete all used forgot password requests for this user
        ForgotPasswordRequest.objects.filter(email=user.email, is_used=True).delete()
        return Response(
            {"detail": "Password reset successfully."},
            status=status.HTTP_200_OK,
        )
