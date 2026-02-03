import uuid
from django.conf import settings
from django.db import models
from courses.models import Course

class Teacher(models.Model):
    gender_choice = (
        ("male", "Male"),
        ("female", "Female"),
        ("others", "Others")
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile"
    )

    department = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    gender = models.CharField(max_length=10, choices=gender_choice)

    def __str__(self):
        return self.user.email    