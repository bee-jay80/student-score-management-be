from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from apps.notifications.models.student_grade_notification import StudentGradeNotification

from django.contrib.auth import get_user_model
User = get_user_model()

class StudentGradeNotificationSerializer(serializers.ModelSerializer):
    student_email = serializers.CharField(source='student.email', read_only=True)
    student_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = StudentGradeNotification
        fields = (
            'id',
            'student_email',
            'student_name',
            'course_title',
            'score',
            'total_mark',
            'remark',
            'is_read',
            'is_emailed',
            'created_at',
        )
        read_only_fields = ['id', 'student_email', 'is_emailed', 'created_at']

    @extend_schema_field(serializers.CharField())
    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"
