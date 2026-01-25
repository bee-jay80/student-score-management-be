from django.urls import path
from .views import RegisterView, LoginView, RefreshView, LogoutView, CurrentUserView, StudentRoleTestView, VerifyOTPView

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("refresh/", RefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
    path("me/", CurrentUserView.as_view()),
    path("student-test/", StudentRoleTestView.as_view()),
]
