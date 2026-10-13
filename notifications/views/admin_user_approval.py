from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from notifications.serializers.admin_notification import PendingUserSerializer
from notifications.permissions import IsAdmin

from rest_framework import serializers, status
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)

from notifications.models.admin_notification import AdminNotification
from accounts.utils.emails import send_approval_email, send_rejection_email



class PendingUsersView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        summary="List pending users",
        description="Return email-verified user accounts awaiting administrator approval.",
        responses={
            200: PendingUserSerializer(many=True),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="Administrator access is required."),
        },
        tags=["User administration"],
    )
    def get(self, request):
        users = User.objects.filter(
            is_email_verified=True,
            is_active=False
        ).order_by("-created_at")

        serializer = PendingUserSerializer(users, many=True)
        return Response(serializer.data)




class ApproveUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        summary="Approve a pending user",
        description="Activate a pending account and send an approval email. An optional role may be assigned.",
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the user to approve.",
            ),
        ],
        request=inline_serializer(
            name="ApprovePendingUserRequest",
            fields={"role": serializers.CharField(required=False)},
        ),
        responses={
            200: inline_serializer(
                name="ApprovePendingUserResponse",
                fields={"detail": serializers.CharField()},
            ),
            400: OpenApiResponse(description="The user has already been approved."),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="Administrator access is required."),
            404: OpenApiResponse(description="The user was not found."),
        },
        tags=["User administration"],
    )
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        role = request.data.get("role")
        if role:
            user.role = role

        if user.is_active:
            return Response(
                {"detail": "User already approved"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.save()

        AdminNotification.objects.filter(
            related_user=user,
            type=AdminNotification.USER_APPROVAL
        ).update(is_read=True)

        send_approval_email(user)

        return Response(
            {"detail": "User approved successfully"},
            status=status.HTTP_200_OK,
        )




class RejectUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        summary="Reject a pending user",
        description="Send a rejection email and remove the user account.",
        request=None,
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
                name="RejectPendingUserResponse",
                fields={"detail": serializers.CharField()},
            ),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="Administrator access is required."),
            404: OpenApiResponse(description="The user was not found."),
        },
        tags=["User administration"],
    )
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        send_rejection_email(user)

        AdminNotification.objects.filter(
            related_user=user,
            type=AdminNotification.USER_APPROVAL
        ).delete()

        user.delete()

        return Response(
            {"detail": "User rejected and removed"},
            status=status.HTTP_200_OK,
        )
