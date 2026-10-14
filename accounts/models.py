from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
import uuid
from .managers import UserManager
from django.conf import settings

# image upload using cloudinary storing the image url in the model
import cloudinary.models
from courses.models import Course




class UserRole:
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

    CHOICES = (
        (STUDENT, "Student"),
        (TEACHER, "Teacher"),
        (ADMIN, "Admin"),
    )



class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    
    reg_no = models.CharField(max_length=50, unique=True, null=True,
    blank=True)
    phone_number = models.CharField(max_length=20)



    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    role = models.CharField(
        max_length=20,
        choices=UserRole.CHOICES,
        default=UserRole.STUDENT
    )
    courses = models.ManyToManyField(
        Course,
        blank=True,
        related_name="users",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email


class EmailOTP(models.Model):
    PURPOSE_CHOICES = (
        ("email_verification", "Email Verification"),
        ("password_reset", "Password Reset"),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_otp",
    )
    otp_hash = models.CharField(max_length=255)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["purpose"]),
        ]

class ImageUpload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = cloudinary.models.CloudinaryField('image') 
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image uploaded by {self.user.email} at {self.uploaded_at}"