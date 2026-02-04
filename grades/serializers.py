from rest_framework import serializers
from .models import Grade
from courses.models import Course
from django.db.models import Avg, Min, Max, Count

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'enrollment', 'score', 'graded_at', "remark", 'graded_by', 'updated_at', 'updated_by']
        read_only_fields = ['id', 'graded_at', 'graded_by', 'updated_at']


class CourseStatsSerializer(serializers.Serializer):
    course_id = serializers.UUIDField()
    course_title = serializers.CharField()
    count = serializers.IntegerField()
    average = serializers.FloatField()
    minimum = serializers.FloatField()
    maximum = serializers.FloatField()
    buckets = serializers.DictField(child=serializers.IntegerField())

