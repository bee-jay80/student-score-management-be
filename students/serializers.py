from rest_framework import serializers
from .models import Student
from django.utils import timezone
from .models import StudentFieldUpdateRequest
from courses.models import CourseRole
from accounts.models import User

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id',
            'user',
            'matric_no',
            'branch_location',
            'phone_number',
            'address',
            'gender',
            'date_of_birth',
            'enrolled_at',
        ]
        read_only_fields = ['id', 'enrolled_at']

    def validate_date_of_birth(self, value):
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    def create(self, validated_data):
        return Student.objects.create(**validated_data)


class StudentFieldUpdateRequestSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    requested_role = serializers.PrimaryKeyRelatedField(queryset=CourseRole.objects.all())

    class Meta:
        model = StudentFieldUpdateRequest
        fields = [
            'id', 'student', 'requested_role', 'message', 'status', 'created_at', 'reviewed_by', 'reviewed_at'
        ]
        read_only_fields = ['id', 'student', 'status', 'created_at', 'reviewed_by', 'reviewed_at']

class AdminStudentFieldUpdateRequestSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    requested_role = serializers.StringRelatedField()
    reviewed_by = serializers.StringRelatedField()

    class Meta:
        model = StudentFieldUpdateRequest
        fields = ['id', 'student', 'requested_role', 'message', 'status', 'created_at', 'reviewed_by', 'reviewed_at']