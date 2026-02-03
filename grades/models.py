from django.db import models
import uuid
from courses.models import Enrollment
from teachers.models import Teacher

class Grade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="grade"
    )

    score = models.DecimalField(max_digits=5, decimal_places=2)  # e.g. 85.50, 92.00
    remark = models.CharField(max_length=50)  # Pass / Fail / Excellent
    graded_at = models.DateTimeField(auto_now_add=True)
    graded_by = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        related_name="graded_scores"
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.enrollment.student.user.email} - {self.score}"
