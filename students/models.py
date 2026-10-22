from django.db import models
from django.conf import settings
import uuid

from courses.models import CourseDetail, Course


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

    branch_location = models.CharField(max_length=100)
    matric_no = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    gender = models.CharField(max_length=10, choices=gender_choice)
    date_of_birth = models.DateField(blank=True, null=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    month_used = models.PositiveIntegerField(default=0)  # Track the number of months used
    fields = models.ManyToManyField(CourseDetail, related_name="students")

    def __str__(self):
        return self.user.email

    
class StudentFieldUpdateRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="field_update_requests"
    )
    requested_role = models.ForeignKey(CourseDetail, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def approve(self, reviewer):
        # Add the requested role to the student's fields and mark approved
        self.student.fields.add(self.requested_role)
        self.status = self.STATUS_APPROVED
        self.reviewed_by = reviewer
        from django.utils import timezone

        self.reviewed_at = timezone.now()
        self.save()

    def reject(self, reviewer):
        self.status = self.STATUS_REJECTED
        self.reviewed_by = reviewer
        from django.utils import timezone

        self.reviewed_at = timezone.now()
        self.save()


# Class StudentCourseField()