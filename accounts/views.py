from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated

from .serializers import RegisterSerializer, User, ImageUploadSerializer
from .models import EmailOTP, ImageUpload
from .utils.emails import (
    notify_admins_new_user,
    send_rejection_email,
    send_approval_email,
    send_otp_email,
)

from .utils.cookies import set_jwt_cookies, set_pending_cookie
from .utils.verification_session import create_verification_token, verify_verification_token

from .utils.otp import (create_otp, verify_otp)
from .utils.registration import register_or_resend_otp
from .permissions import IsAdmin, IsTeacher, IsStudent
from notifications.services.notification_create import create_user_approval_notification
from .throttles import OTPRateThrottle
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)




class RegisterView(APIView):
    permission_classes = []
    authentication_classes = []
    throttle_classes = [OTPRateThrottle]

    @extend_schema(
        summary="Register a student account",
        description="Submit registration details and start email OTP verification.",
        request=RegisterSerializer,
        responses={
            201: inline_serializer(
                name="RegistrationResponse",
                fields={
                    "ststus": serializers.CharField(),
                    "detail": serializers.CharField(),
                },
            ),
            400: OpenApiResponse(description="The registration data is invalid or the email is already registered."),
            429: OpenApiResponse(description="The registration OTP rate limit was exceeded."),
            500: OpenApiResponse(description="Registration could not be processed."),
        },
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user, response = register_or_resend_otp(serializer.validated_data)
            return response
        except ValueError as ve:
            return Response({"detail": str(ve)}, status=status.HTTP_400_BAD_REQUEST)




class LoginView(APIView):
    permission_classes = []
    authentication_classes = []

    @extend_schema(
        summary="Log in",
        description="Authenticate with email and password and set access and refresh cookies.",
        request=inline_serializer(
            name="LoginRequest",
            fields={
                "email": serializers.EmailField(),
                "password": serializers.CharField(write_only=True),
            },
        ),
        responses={
            200: inline_serializer(
                name="LoginResponse",
                fields={
                    "status": serializers.CharField(),
                    "id": serializers.UUIDField(),
                    "email": serializers.EmailField(),
                    "role": serializers.CharField(),
                },
            ),
            401: OpenApiResponse(description="The email or password is invalid."),
        },
        tags=["Authentication"],
    )
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

    @extend_schema(
        summary="Refresh the access token",
        description="Exchange the refresh-token cookie for a new access token and update authentication cookies.",
        request=None,
        parameters=[
            OpenApiParameter(
                name="refresh_token",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.COOKIE,
                description="Refresh-token cookie.",
            ),
        ],
        responses={
            200: inline_serializer(
                name="RefreshTokenResponse",
                fields={"access": serializers.CharField()},
            ),
            401: OpenApiResponse(description="The refresh-token cookie is missing or invalid."),
        },
        tags=["Authentication"],
    )
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"detail": "No refresh token"}, status=401)

        refresh = RefreshToken(refresh_token)
        access = refresh.access_token

        response = Response({"access": str(access)})
        set_jwt_cookies(response, str(access), str(refresh))

        return response


class LogoutView(APIView):
    @extend_schema(
        summary="Log out",
        description="Blacklist the refresh token and clear the authentication cookies.",
        request=None,
        responses={
            204: OpenApiResponse(description="Logged out successfully."),
            401: OpenApiResponse(description="Authentication is required or the refresh token is invalid."),
        },
        tags=["Authentication"],
    )
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

    @extend_schema(
        summary="Approve a user",
        description="Activate a user account and send an approval email. Administrator access is required.",
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the user to approve.",
            ),
        ],
        responses={
            200: inline_serializer(
                name="ApproveUserResponse",
                fields={"detail": serializers.CharField()},
            ),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="Administrator access is required."),
            404: OpenApiResponse(description="The user was not found."),
        },
        tags=["User administration"],
    )
    def post(self, request, user_id):
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save()

        send_approval_email(user)

        return Response({"detail": "User approved successfully"})


class RejectUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        summary="Reject a user",
        description="Send a rejection email and remove the user account. Administrator access is required.",
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the user to reject.",
            ),
        ],
        responses={
            200: inline_serializer(
                name="RejectUserResponse",
                fields={"detail": serializers.CharField()},
            ),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="Administrator access is required."),
            404: OpenApiResponse(description="The user was not found."),
        },
        tags=["User administration"],
    )
    def post(self, request, user_id):
        user = User.objects.get(id=user_id)

        send_rejection_email(user)
        user.delete()

        return Response({"detail": "User rejected and removed"})


class ResendOTPView(APIView):
    permission_classes = []
    authentication_classes = []
    throttle_classes = [OTPRateThrottle]

    @extend_schema(
        summary="Resend the email verification OTP",
        description="Send a new email-verification OTP using the verification-session cookie.",
        request=None,
        parameters=[
            OpenApiParameter(
                name="verification_session",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.COOKIE,
                description="Verification-session cookie issued during registration.",
            ),
        ],
        responses={
            200: inline_serializer(
                name="ResendOTPResponse",
                fields={"detail": serializers.CharField()},
            ),
            400: OpenApiResponse(description="The verification session is invalid or expired."),
            429: OpenApiResponse(description="The OTP resend rate limit was exceeded."),
        },
        tags=["Authentication"],
    )
    def post(self, request):
        try:
            user_id = verify_verification_token(request.COOKIES.get("verification_session"))
        
        except Exception:
            return Response({"detail": "Invalid or expired verification session"}, status=400)
            

        user = User.objects.get(id=user_id)
        otp = create_otp(user, purpose="EMAIL_VERIFICATION")
        send_otp_email(user, otp)

        return Response({"detail": "OTP resent successfully"})

class VerifyOTPView(APIView):
    permission_classes = []
    authentication_classes = []

    @extend_schema(
        summary="Verify the email OTP",
        description="Verify the OTP using the registration verification-session cookie.",
        parameters=[
            OpenApiParameter(
                name="verification_session",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.COOKIE,
                description="Verification-session cookie issued during registration.",
            ),
        ],
        request=inline_serializer(
            name="EmailOTPRequest",
            fields={"otp": serializers.CharField(max_length=6)},
        ),
        responses={
            200: inline_serializer(
                name="EmailOTPVerificationResponse",
                fields={
                    "detail": serializers.CharField(required=False),
                    "Error": serializers.CharField(required=False),
                },
            ),
            400: OpenApiResponse(description="The verification session or OTP is invalid or expired."),
        },
        tags=["Authentication"],
    )
    def post(self, request):
        otp = request.data.get("otp")

        try:
            user_id = verify_verification_token(request.COOKIES.get("verification_session"))
        
        except Exception:
            return Response({"detail": "Invalid or expired verification session"}, status=400)
            
        user = User.objects.get(id=user_id)
        user.is_email_verified = True

        if verify_otp(user, otp, purpose="EMAIL_VERIFICATION"):
            
            user.save()
            try:
                notify_admins_new_user(user)
                create_user_approval_notification(user, True)
                return Response({"detail": "Email verified successfully"})
            except Exception as e:
                create_user_approval_notification(user, False)
                return Response({"Error":str(e)})
        else:
            return Response({"detail": "Invalid or expired OTP"}, status=400)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get the current user",
        description="Return identity and role details for the authenticated user.",
        responses={
            200: inline_serializer(
                name="CurrentUserResponse",
                fields={
                    "id": serializers.UUIDField(),
                    "email": serializers.EmailField(),
                    "first_name": serializers.CharField(),
                    "last_name": serializers.CharField(),
                    "role": serializers.CharField(),
                },
            ),
            401: OpenApiResponse(description="Authentication is required."),
        },
        tags=["Authentication"],
    )
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

    @extend_schema(
        summary="Check student access",
        description="Return a greeting for the authenticated student.",
        responses={
            200: inline_serializer(
                name="StudentRoleTestResponse",
                fields={"message": serializers.CharField()},
            ),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="The user does not have the student role."),
        },
        tags=["Authentication"],
    )
    def get(self, request):
        user = request.user
        return Response({
            "message": f"Hello Student {user.first_name} {user.last_name}!"
        })


class ImageUploadView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ImageUploadSerializer

    @extend_schema(
        summary="Upload a profile image",
        description="Upload an image for the authenticated user.",
        request=ImageUploadSerializer,
        responses={
            201: ImageUploadSerializer,
            400: OpenApiResponse(description="The image upload data is invalid."),
            401: OpenApiResponse(description="Authentication is required."),
        },
        tags=["Image uploads"],
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ImageUploadDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Retrieve an image upload",
        description="Return an image upload owned by the authenticated user.",
        parameters=[
            OpenApiParameter(
                name="image_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the image upload.",
            ),
        ],
        responses={
            200: ImageUploadSerializer,
            401: OpenApiResponse(description="Authentication is required."),
            404: OpenApiResponse(description="The image upload was not found."),
        },
        tags=["Image uploads"],
    )
    def get(self, request, upload_id):
        try:
            upload = ImageUpload.objects.get(id=upload_id, user=request.user)
        except ImageUpload.DoesNotExist:
            return Response({"detail": "Image upload not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ImageUploadSerializer(upload)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update an image upload",
        description="Partially update an image upload owned by the authenticated user.",
        parameters=[
            OpenApiParameter(
                name="image_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the image upload.",
            ),
        ],
        request=ImageUploadSerializer(partial=True),
        responses={
            200: ImageUploadSerializer,
            400: OpenApiResponse(description="The image upload data is invalid."),
            401: OpenApiResponse(description="Authentication is required."),
            404: OpenApiResponse(description="The image upload was not found."),
        },
        tags=["Image uploads"],
    )
    def put(self, request, upload_id):
        try:
            upload = ImageUpload.objects.get(id=upload_id, user=request.user)
        except ImageUpload.DoesNotExist:
            return Response({"detail": "Image upload not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ImageUploadSerializer(upload, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete an image upload",
        description="Delete an image upload owned by the authenticated user.",
        parameters=[
            OpenApiParameter(
                name="image_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the image upload.",
            ),
        ],
        responses={
            204: OpenApiResponse(description="The image upload was deleted."),
            401: OpenApiResponse(description="Authentication is required."),
            404: OpenApiResponse(description="The image upload was not found."),
        },
        tags=["Image uploads"],
    )
    def delete(self, request, upload_id):
        try:
            upload = ImageUpload.objects.get(id=upload_id, user=request.user)
        except ImageUpload.DoesNotExist:
            return Response({"detail": "Image upload not found."}, status=status.HTTP_404_NOT_FOUND)

        upload.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    