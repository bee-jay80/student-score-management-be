from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.permissions import IsTeacher, IsAdmin, IsStudent
from rest_framework.permissions import IsAuthenticated
from .serializers import GradeSerializer, CourseStatsSerializer
from .models import Grade
from django.db.models import Avg, Min, Max, Count
from django.db.models import Q
from django.shortcuts import get_object_or_404

User = get_user_model()

class GradeCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher | IsAdmin]

    def post(self, request):
        serializer = GradeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(graded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GradeDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher | IsAdmin]

    def get(self, request, grade_id):
        try:
            grade = Grade.objects.get(id=grade_id)
        except Grade.DoesNotExist:
            return Response({"detail": "Grade not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = GradeSerializer(grade)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, grade_id):
        try:
            grade = Grade.objects.get(id=grade_id)
        except Grade.DoesNotExist:
            return Response({"detail": "Grade not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = GradeSerializer(grade, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, grade_id):
        try:
            grade = Grade.objects.get(id=grade_id)
        except Grade.DoesNotExist:
            return Response({"detail": "Grade not found."}, status=status.HTTP_404_NOT_FOUND)
        
        grade.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def grade_list_filter(enrollment_id=None, student_id=None, student_name=None, course_id=None, course_name=None, student_email=None, graded_by=None, updated_by=None):
    """Return a queryset of Grade filtered by the provided optional criteria."""
    grades = Grade.objects.all()

    if enrollment_id:
        grades = grades.filter(enrollment__id=enrollment_id)
    if student_id:
        grades = grades.filter(enrollment__student__id=student_id)
    if student_name:
        grades = grades.filter(
            Q(enrollment__student__user__first_name__icontains=student_name) |
            Q(enrollment__student__user__last_name__icontains=student_name)
        )
    if course_id:
        grades = grades.filter(enrollment__course__id=course_id)
    if course_name:
        grades = grades.filter(enrollment__course__name__icontains=course_name)
    if student_email:
        grades = grades.filter(enrollment__student__user__email__icontains=student_email)
    if graded_by:
        grades = grades.filter(graded_by__id=graded_by)
    if updated_by:
        grades = grades.filter(updated_by__id=updated_by)

    return grades

class GradeListView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher | IsAdmin]

    def get(self, request):
        enrollment_id = request.query_params.get("enrollment_id")
        student_id = request.query_params.get("student_id")
        student_name = request.query_params.get("student_name")
        course_id = request.query_params.get("course_id")
        course_name = request.query_params.get("course_name")
        student_email = request.query_params.get("student_email")

        grades = grade_list_filter(
            enrollment_id=enrollment_id,
            student_id=student_id,
            student_name=student_name,
            course_id=course_id,
            course_name=course_name,
            student_email=student_email
        )
        # avoid N+1
        grades = grades.select_related('enrollment__course', 'enrollment__student__user', 'graded_by', 'updated_by')
        serializer = GradeSerializer(grades, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class TeacherGradeListView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher | IsAdmin]

    def get(self, request):
        enrollment_id = request.query_params.get("enrollment_id")
        student_id = request.query_params.get("student_id")
        student_name = request.query_params.get("student_name")
        course_id = request.query_params.get("course_id")
        course_name = request.query_params.get("course_name")
        student_email = request.query_params.get("student_email")
        # graded_by = request.query_params.get("graded_by")
        # updated_by = request.query_params.get("updated_by")

        grades_by_user = grade_list_filter(
            enrollment_id=enrollment_id,
            student_id=student_id,
            student_name=student_name,
            course_id=course_id,
            course_name=course_name,
            student_email=student_email,
            graded_by=request.user.id,
        )

        grades_by_user_updated = grade_list_filter(
            enrollment_id=enrollment_id,
            student_id=student_id,
            student_name=student_name,
            course_id=course_id,
            course_name=course_name,
            student_email=student_email,
            updated_by=request.user.id,
        )
        # union and distinct to combine grades created or updated by this teacher
        grades = (grades_by_user | grades_by_user_updated).distinct()
        grades = grades.select_related('enrollment__course', 'enrollment__student__user', 'graded_by', 'updated_by')
        serializer = GradeSerializer(grades, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseStatsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher | IsAdmin]

    def get(self, request):
        course_id = request.query_params.get('course_id')
        if not course_id:
            return Response({'detail': 'course_id is required as query param.'}, status=status.HTTP_400_BAD_REQUEST)

        qs = Grade.objects.filter(enrollment__course__id=course_id)
        stats = qs.aggregate(average=Avg('score'), minimum=Min('score'), maximum=Max('score'), count=Count('id'))

        # buckets: 0-49,50-64,65-79,80-89,90-100
        buckets = {
            '0-49': qs.filter(score__lt=50).count(),
            '50-64': qs.filter(score__gte=50, score__lt=65).count(),
            '65-79': qs.filter(score__gte=65, score__lt=80).count(),
            '80-89': qs.filter(score__gte=80, score__lt=90).count(),
            '90-100': qs.filter(score__gte=90).count(),
        }

        data = {
            'course_id': course_id,
            'course_title': qs.first().enrollment.course.title if qs.exists() else '',
            'count': stats.get('count') or 0,
            'average': float(stats.get('average') or 0.0),
            'minimum': float(stats.get('minimum') or 0.0),
            'maximum': float(stats.get('maximum') or 0.0),
            'buckets': buckets,
        }

        serializer = CourseStatsSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StudentCourseStatsView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        user = request.user
        student = get_object_or_404(User.objects.filter(id=user.id).select_related('student_profile'), id=user.id).student_profile

        course_id = request.query_params.get('course_id')
        if not course_id:
            return Response({'detail': 'course_id is required as query param.'}, status=status.HTTP_400_BAD_REQUEST)

        qs = Grade.objects.filter(enrollment__course__id=course_id, enrollment__student=student)
        stats = qs.aggregate(average=Avg('score'), minimum=Min('score'), maximum=Max('score'), count=Count('id'))

        # buckets: 0-49,50-64,65-79,80-89,90-100
        buckets = {
            '0-49': qs.filter(score__lt=50).count(),
            '50-64': qs.filter(score__gte=50, score__lt=65).count(),
            '65-79': qs.filter(score__gte=65, score__lt=80).count(),
            '80-89': qs.filter(score__gte=80, score__lt=90).count(),
            '90-100': qs.filter(score__gte=90).count(),
        }

        data = {
            'course_id': course_id,
            'course_title': qs.first().enrollment.course.title if qs.exists() else '',
            'count': stats.get('count') or 0,
            'average': float(stats.get('average') or 0.0),
            'minimum': float(stats.get('minimum') or 0.0),
            'maximum': float(stats.get('maximum') or 0.0),
            'buckets': buckets,
        }

        serializer = CourseStatsSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)        



class TeacherGradeDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher | IsAdmin]

    def get(self, request, grade_id):
        user = request.user
        try:
            grade = Grade.objects.get(id=grade_id, graded_by=user)
        except Grade.DoesNotExist:
            return Response({"detail": "Grade not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = GradeSerializer(grade)
        return Response(serializer.data, status=status.HTTP_200_OK)

# function to filter students grades for student views
# filter by scores greater than, less than, equal to, between scores, date graded, course name, enrollment month
def student_grade_list_filter(min_score=None, max_score=None, graded_after=None, graded_before=None, course_name=None, enrollment_month=None):
    grades = Grade.objects.all()

    if min_score is not None:
        grades = grades.filter(score__gte=min_score)
    if max_score is not None:
        grades = grades.filter(score__lte=max_score)
    if graded_after is not None:
        grades = grades.filter(graded_at__gte=graded_after)
    if graded_before is not None:
        grades = grades.filter(graded_at__lte=graded_before)
    if course_name:
        grades = grades.filter(enrollment__course__name__icontains=course_name)
    if enrollment_month:
        grades = grades.filter(enrollment__month=enrollment_month)

    return grades

class StudentGradeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        min_score = request.query_params.get("min_score")
        max_score = request.query_params.get("max_score")
        graded_after = request.query_params.get("graded_after")
        graded_before = request.query_params.get("graded_before")
        course_name = request.query_params.get("course_name")
        enrollment_month = request.query_params.get("enrollment_month")

        grades = student_grade_list_filter(
            min_score=min_score,
            max_score=max_score,
            graded_after=graded_after,
            graded_before=graded_before,
            course_name=course_name,
            enrollment_month=enrollment_month
        ).filter(enrollment__student=user)

        serializer = GradeSerializer(grades, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StudentGradeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, grade_id):
        user = request.user
        try:
            grade = Grade.objects.get(id=grade_id, enrollment__student=user)
        except Grade.DoesNotExist:
            return Response({"detail": "Grade not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = GradeSerializer(grade)
        return Response(serializer.data, status=status.HTTP_200_OK)
