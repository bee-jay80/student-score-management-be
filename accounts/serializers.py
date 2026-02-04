from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.models import UserRole, ImageUpload

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
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
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            user = User.objects.get(email=value)
            if user.is_email_verified:
                raise serializers.ValidationError("Email is already registered.")
        return value


# OTP Verify Serializer
class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)



# OTP Resend Serializer
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUpload
        fields = ['id', 'user', 'image', 'uploaded_at']
        read_only_fields = ['id', 'user', 'uploaded_at']
    