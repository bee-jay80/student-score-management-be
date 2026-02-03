from django.db import models
from django.conf import settings
import uuid

class Student(models.Model):

    gender_choice = (
        ("male", "Male"),
        ("female", "Female"),
        ("others", "Others")
    )



    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    matric_no = models.CharField(max_length=50, unique=True)
    branch_location = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    gender = models.CharField(max_length=10, choices=gender_choice)
    date_of_birth = models.DateField()
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email
