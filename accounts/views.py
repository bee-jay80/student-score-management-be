from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated

from .serializers import RegisterSerializer, User
from .models import EmailOTP
from .utils.emails import (
    notify_admins_new_user,
    send_rejection_email,
    send_approval_email,
    send_otp_email,
)

from .utils.cookies import set_jwt_cookies, set_pending_cookie
from .utils.verification_session import create_verification_token, verify_verification_token

from .utils.otp import (create_otp, verify_otp)
from .permissions import IsAdmin, IsTeacher, IsStudent






class RegisterView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # notify_admins_new_user(user)
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
            user.delete()
            return Response(
                {"detail": "Failed to send OTP email. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

        return response




class LoginView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid credentials")

        refresh = RefreshToken.for_user(user)

        response = Response({
            "status":"success",
            "id": user.id,
            "email": user.email,
            "role": user.role,
        })

        set_jwt_cookies(response, str(refresh.access_token), str(refresh))
        return response


class RefreshView(APIView):
    permission_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"detail": "No refresh token"}, status=401)

        refresh = RefreshToken(refresh_token)
        access = refresh.access_token

        response = Response({"access": str(access)})
        response.set_cookie("access_token", str(access), httponly=True)

        return response


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        token = RefreshToken(refresh_token)
        token.blacklist()

        response = Response(status=204)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response



class ApproveUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, user_id):
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save()

        send_approval_email(user)

        return Response({"detail": "User approved successfully"})


class RejectUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, user_id):
        user = User.objects.get(id=user_id)

        send_rejection_email(user)
        user.delete()

        return Response({"detail": "User rejected and removed"})



class VerifyOTPView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        otp = request.data.get("otp")

        try:
            user_id = verify_verification_token(request.COOKIES.get("verification_session"))
        
        except Exception:
            return Response({"detail": "Invalid or expired verification session"}, status=400)
            
        user = User.objects.get(id=user_id)

        if verify_otp(user, otp, purpose="EMAIL_VERIFICATION"):
            user.is_email_verified = True
            user.save()
            return Response({"detail": "Email verified successfully"})
        else:
            return Response({"detail": "Invalid or expired OTP"}, status=400)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        })

class StudentRoleTestView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        user = request.user
        return Response({
            "message": f"Hello Student {user.first_name} {user.last_name}!"
        })