from django.db import models
from django.conf import settings
import uuid


class StudentGradeNotification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="grade_notifications"
    )
    grade = models.ForeignKey(
        'grades.Grade',
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    course_title = models.CharField(max_length=200)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    total_mark = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    remark = models.CharField(max_length=50)
    is_read = models.BooleanField(default=False)
    is_emailed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'is_read']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Grade notification for {self.student.email} - {self.course_title}"
