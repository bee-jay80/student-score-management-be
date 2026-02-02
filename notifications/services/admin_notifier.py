# from django.contrib.auth import get_user_model
# from django.conf import settings
# from accounts.utils.emails import send_admin_pending_users_email

# User = get_user_model()


# def notify_admins_user_needs_approval(user):
#     """
#     Send email to all admins when a verified user
#     is awaiting approval.
#     """

#     if not user.is_email_verified or user.is_active:
#         return

#     admins = User.objects.filter(is_staff=True, is_active=True)

#     if not admins.exists():
#         return

#     approval_url = f"{settings.FRONTEND_URL}/admin/pending-users"

#     send_admin_pending_users_email(
#         admins=admins,
#         approval_url=approval_url,
#         pending_user=user,
#     )
