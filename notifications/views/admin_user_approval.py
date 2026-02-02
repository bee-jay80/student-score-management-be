from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from notifications.serializers.admin_notification import PendingUserSerializer
from notifications.permissions import IsAdmin

from rest_framework import status
from django.shortcuts import get_object_or_404

from notifications.models.admin_notification import AdminNotification
from accounts.utils.emails import send_approval_email, send_rejection_email



class PendingUsersView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        users = User.objects.filter(
            is_email_verified=True,
            is_active=False
        ).order_by("-created_at")

        serializer = PendingUserSerializer(users, many=True)
        return Response(serializer.data)




class ApproveUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

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
