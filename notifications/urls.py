from django.urls import path
from notifications.views.admin_notifications import AdminNotificationListView
from notifications.views.admin_user_approval import (
    PendingUsersView,
    ApproveUserView,
    RejectUserView,
)
from notifications.views.student_grade_notification import (
    StudentGradeNotificationListView,
    StudentGradeNotificationDetailView,
    StudentGradeNotificationUnreadCountView,
    MarkNotificationAsReadView,
    MarkAllNotificationsAsReadView,
)
from notifications.views.student_field_update_notification import (
    StudentFieldUpdateNotificationListView,
    AdminTeacherFieldUpdateNotificationListView,
    FieldUpdateNotificationDetailView,
    StudentFieldUpdateNotificationUnreadCountView,
    AdminTeacherFieldUpdateNotificationUnreadCountView,
)


urlpatterns = [
    # Admin notifications
    path("admin/notifications/", AdminNotificationListView.as_view()),
    path("admin/pending-users/", PendingUsersView.as_view()),
    path("admin/users/<uuid:user_id>/approve/", ApproveUserView.as_view()),
    path("admin/users/<uuid:user_id>/reject/", RejectUserView.as_view()),
    
    # Student grade notifications
    path("student/grade-notifications/", StudentGradeNotificationListView.as_view(), name='student-grade-notifications-list'),
    path("student/grade-notifications/<uuid:notification_id>/", StudentGradeNotificationDetailView.as_view(), name='student-grade-notification-detail'),
    path("student/grade-notifications/unread-count/", StudentGradeNotificationUnreadCountView.as_view(), name='student-grade-notifications-unread-count'),
    path("student/grade-notifications/<uuid:notification_id>/read/", MarkNotificationAsReadView.as_view(), name='mark-notification-as-read'),
    path("student/grade-notifications/mark-all-read/", MarkAllNotificationsAsReadView.as_view(), name='mark-all-notifications-as-read'),
    
    # Student field update notifications
    path("student/field-update-notifications/", StudentFieldUpdateNotificationListView.as_view(), name='student-field-update-notifications'),
    path("admin-teacher/field-update-notifications/", AdminTeacherFieldUpdateNotificationListView.as_view(), name='admin-teacher-field-update-notifications'),
    path("field-update-notifications/<uuid:notification_id>/", FieldUpdateNotificationDetailView.as_view(), name='field-update-notification-detail'),
    path("student/field-update-notifications/unread-count/", StudentFieldUpdateNotificationUnreadCountView.as_view(), name='student-field-update-notifications-unread-count'),
    path("admin-teacher/field-update-notifications/unread-count/", AdminTeacherFieldUpdateNotificationUnreadCountView.as_view(), name='admin-teacher-field-update-notifications-unread-count'),
]
