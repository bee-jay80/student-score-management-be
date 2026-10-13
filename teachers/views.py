from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Teacher
from .serializers import TeacherSerializer
from teachers.permissions import IsTeacher
from accounts.permissions import IsAdmin


class TeacherCreateView(APIView):
	permission_classes = [IsAuthenticated, IsAdmin|IsTeacher] if False else [IsAuthenticated, IsAdmin]

	def post(self, request):
		serializer = TeacherSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherDetailView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, teacher_id):
		try:
			teacher = Teacher.objects.get(id=teacher_id)
		except Teacher.DoesNotExist:
			return Response({"detail": "Teacher not found."}, status=status.HTTP_404_NOT_FOUND)

		serializer = TeacherSerializer(teacher)
		return Response(serializer.data, status=status.HTTP_200_OK)

	def put(self, request, teacher_id):
		try:
			teacher = Teacher.objects.get(id=teacher_id)
		except Teacher.DoesNotExist:
			return Response({"detail": "Teacher not found."}, status=status.HTTP_404_NOT_FOUND)

		serializer = TeacherSerializer(teacher, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, teacher_id):
		try:
			teacher = Teacher.objects.get(id=teacher_id)
		except Teacher.DoesNotExist:
			return Response({"detail": "Teacher not found."}, status=status.HTTP_404_NOT_FOUND)

		teacher.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
