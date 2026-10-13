from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import CourseSerializer, CourseRoleSerializer
from .models import Course, CourseRole

from accounts.permissions import IsStudent, IsTeacher, IsAdmin
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)


class CourseListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List active courses",
        description="Return all active courses.",
        responses={
            200: CourseSerializer(many=True),
            401: OpenApiResponse(description="Authentication is required."),
        },
        tags=["Courses"],
    )
    def get(self, request):
        courses = Course.objects.filter(is_active=True)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StudentCourseListView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    @extend_schema(
        summary="List courses for the current student",
        description="Return active courses matching the authenticated student's fields and current month.",
        responses={
            200: CourseSerializer(many=True),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="The user is not a student."),
        },
        tags=["Courses"],
    )
    def get(self, request):
        # get student's current month
        student_month = request.user.student.month_used
        # Get student fields
        student_fields = request.user.student.fields.all()
        # Filter courses based on if the course fields duration is greater or equal to student's month and course field is in student's fields
        courses = Course.objects.filter(
            is_active=True,
            fields__duration__gte=student_month,
            fields__in=student_fields
        ).distinct()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class CourseCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher | IsAdmin]

    @extend_schema(
        summary="Create a course",
        description="Create a course. Only teachers and administrators may use this endpoint.",
        request=CourseSerializer,
        responses={
            201: CourseSerializer,
            400: OpenApiResponse(description="The submitted course data is invalid."),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="The user is not permitted to create courses."),
        },
        tags=["Courses"],
    )
    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class courseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Retrieve a course",
        description="Return an active course by its UUID.",
        parameters=[
            OpenApiParameter(
                name="course_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the course.",
            ),
        ],
        responses={
            200: CourseSerializer,
            401: OpenApiResponse(description="Authentication is required."),
            404: OpenApiResponse(description="The active course was not found."),
        },
        tags=["Courses"],
    )
    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id, is_active=True)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CourseUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher | IsAdmin]

    @extend_schema(
        summary="Update a course",
        description="Partially update a course by its UUID. Only teachers and administrators may use this endpoint.",
        parameters=[
            OpenApiParameter(
                name="course_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the course.",
            ),
        ],
        request=CourseSerializer(partial=True),
        responses={
            200: CourseSerializer,
            400: OpenApiResponse(description="The submitted course data is invalid."),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="The user is not permitted to update courses."),
            404: OpenApiResponse(description="The course was not found."),
        },
        tags=["Courses"],
    )
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
    
    @extend_schema(
        summary="Deactivate a course",
        description="Mark a course as inactive by its UUID. Only teachers and administrators may use this endpoint.",
        parameters=[
            OpenApiParameter(
                name="course_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the course.",
            ),
        ],
        responses={
            204: OpenApiResponse(description="The course was deactivated."),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="The user is not permitted to deactivate courses."),
            404: OpenApiResponse(description="The course was not found."),
        },
        tags=["Courses"],
    )
    def delete(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        
        course.is_active = False
        course.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
# class EnrollmentView(APIView):
#     permission_classes = [IsAuthenticated, IsStudent | IsAdmin]

#     def post(self, request):
#         serializer = EnrollmentSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(student=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     def get(self, request):
#         enrollments = Enrollment.objects.filter(student=request.user)
#         serializer = EnrollmentSerializer(enrollments, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
    
# class EnrollmentDetailView(APIView):
#     permission_classes = [IsAuthenticated, IsStudent | IsAdmin]

#     def get(self, request, enrollment_id):
#         try:
#             enrollment = Enrollment.objects.get(id=enrollment_id, student=request.user)
#         except Enrollment.DoesNotExist:
#             return Response({"detail": "Enrollment not found."}, status=status.HTTP_404_NOT_FOUND)
        
#         serializer = EnrollmentSerializer(enrollment)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def put(self, request, enrollment_id):
#         try:
#             enrollment = Enrollment.objects.get(id=enrollment_id, student=request.user)
#         except Enrollment.DoesNotExist:
#             return Response({"detail": "Enrollment not found."}, status=status.HTTP_404_NOT_FOUND)
        
#         serializer = EnrollmentSerializer(enrollment, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     def delete(self, request, enrollment_id):
#         try:
#             enrollment = Enrollment.objects.get(id=enrollment_id, student=request.user)
#         except Enrollment.DoesNotExist:
#             return Response({"detail": "Enrollment not found."}, status=status.HTTP_404_NOT_FOUND)
        
#         enrollment.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
    


class CourseRoleCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        summary="Create a course role",
        description="Create a course role. Only administrators may use this endpoint.",
        request=CourseRoleSerializer,
        responses={
            201: CourseRoleSerializer,
            400: OpenApiResponse(description="The submitted course-role data is invalid."),
            401: OpenApiResponse(description="Authentication is required."),
            403: OpenApiResponse(description="The user is not an administrator."),
        },
        tags=["Course roles"],
    )
    def post(self, request):
        serializer = CourseRoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CourseRoleListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List course roles",
        description="Return all course roles.",
        responses={
            200: CourseRoleSerializer(many=True),
            401: OpenApiResponse(description="Authentication is required."),
        },
        tags=["Course roles"],
    )
    def get(self, request):
        roles = CourseRole.objects.all()
        serializer = CourseRoleSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)