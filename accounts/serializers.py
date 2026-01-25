from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.models import UserRole

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "role",
            "password",
        )

    def create(self, validated_data):
        validated_data.pop("role",None)
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            role=UserRole.STUDENT, 
            is_active=False,            
            is_email_verified=False,
        )
        return user

# OTP Verify Serializer
class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)



# OTP Resend Serializer
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
