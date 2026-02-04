from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import CourseSerializer, EnrollmentSerializer
from .models import Course, Enrollment

from accounts.permissions import IsStudent, IsTeacher, IsAdmin
from rest_framework.permissions import IsAuthenticated


class CourseListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        courses = Course.objects.filter(is_active=True)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CourseCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher | IsAdmin]

    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class courseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id, is_active=True)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CourseUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher | IsAdmin]

    def put(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        
        course.is_active = False
        course.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
class EnrollmentView(APIView):
    permission_classes = [IsAuthenticated, IsStudent | IsAdmin]

    def post(self, request):
        serializer = EnrollmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        enrollments = Enrollment.objects.filter(student=request.user)
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class EnrollmentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsStudent | IsAdmin]

    def get(self, request, enrollment_id):
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id, student=request.user)
        except Enrollment.DoesNotExist:
            return Response({"detail": "Enrollment not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, enrollment_id):
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id, student=request.user)
        except Enrollment.DoesNotExist:
            return Response({"detail": "Enrollment not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EnrollmentSerializer(enrollment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, enrollment_id):
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id, student=request.user)
        except Enrollment.DoesNotExist:
            return Response({"detail": "Enrollment not found."}, status=status.HTTP_404_NOT_FOUND)
        
        enrollment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)