from rest_framework import serializers
from .models import Course, Enrollment

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "duration",
            "description",
            "created_at",
            "is_active",
        )

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = (
            "id",
            "student",
            "course",
            "month",
            "status",
            "enrolled_at",
            "completed_at",
            "updated_at",
        )