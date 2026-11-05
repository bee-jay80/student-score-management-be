from django.urls import path
from .views import ForgotPasswordRequestView, OTPVerifyView, ResetPasswordView


urlpatterns = [
    path('request-otp/', ForgotPasswordRequestView.as_view(), name='forgot-password-request-otp'),
    path('verify-otp/', OTPVerifyView.as_view(), name='forgot-password-verify-otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='forgot-password-reset-password'),
]
