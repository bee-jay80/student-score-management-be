from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/courses/", include("courses.urls")),
    path("api/forgot-password/", include("forgot_password.urls")),
]
