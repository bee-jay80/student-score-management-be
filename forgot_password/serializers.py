from rest_framework import serializers
from .models import ForgotPasswordRequest


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    # class Meta:
    #     model = ForgotPasswordRequest
    #     fields = ['email']


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
class OTPVerifySerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)