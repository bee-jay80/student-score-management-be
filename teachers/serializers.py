from rest_framework import serializers
from .models import Teacher
from django.utils import timezone


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = [
            'id',
            'user',
            'department',
            'phone_number',
            'address',
            'gender',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        return Teacher.objects.create(**validated_data)
