from django.db import models
import uuid
# Avoid importing `Student` at module import time to prevent circular imports.
# Use string reference 'students.Student' in ForeignKey declarations instead.

class CourseRole(models.Model):

    STATUS_CHOICES = (
        ("ongoing", "Ongoing"),
        ("failed", "Failed"),
        ("completed", "Completed"),
    )


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)  # e.g. "Frontend Development", "Backend Development", "Data Science"
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField(default=1)  # Duration in months
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ongoing")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.name

class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)  # e.g. "Python Basics", "Django for Beginners", "Html"
    field = models.ForeignKey(CourseRole, on_delete=models.SET_NULL, null=True, related_name="courses")
    duration = models.PositiveIntegerField()  # e.g. "3" to represent the month
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title



# class Enrollment(models.Model):
#     STATUS_CHOICES = (
#         ("ongoing", "Ongoing"),
#         ("failed", "Failed"),
#         ("completed", "Completed"),
#     )

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     # student = models.ForeignKey(
#     #     "students.Student",
#     #     on_delete=models.CASCADE,
#     #     related_name="enrollments"
#     # )
#     course = models.ForeignKey(
#         Course,
#         on_delete=models.CASCADE,
#         related_name="enrollments"
#     )

#     month = models.PositiveIntegerField()
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ongoing")

#     enrolled_at = models.DateTimeField(auto_now_add=True)
#     completed_at = models.DateTimeField(null=True, blank=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         unique_together = ("student", "course", "month")  # 🔐 prevent duplicate enrollments

#     def __str__(self):
#         return f"{self.student.user.email} - {self.course.title}"
