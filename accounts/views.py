from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from .utils import (set_jwt_cookies, notify_admins_new_user,
    send_rejection_email,send_verification_otp, send_approval_email)
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdmin





class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        notify_admins_new_user(user)
        send_verification_otp(user)

        return Response(
            {"detail": "Registration submitted. Await admin approval."},
            status=201
        )




class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid credentials")

        refresh = RefreshToken.for_user(user)

        response = Response({
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
