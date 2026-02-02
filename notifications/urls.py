from django.urls import path
from notifications.views.admin_notifications import AdminNotificationListView
from notifications.views.admin_user_approval import (
    PendingUsersView,
    ApproveUserView,
    RejectUserView,
)


urlpatterns = [
    path("admin/notifications/", AdminNotificationListView.as_view()),
    path("admin/pending-users/", PendingUsersView.as_view()),
    path("admin/users/<uuid:user_id>/approve/", ApproveUserView.as_view()),
    path("admin/users/<uuid:user_id>/reject/", RejectUserView.as_view()),
]
