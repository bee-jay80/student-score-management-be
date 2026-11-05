from django.urls import path
from .views import (GradeCreateView, GradeDetailView, GradeListView, 
    TeacherGradeListView, CourseStatsView, StudentCourseStatsView, 
    TeacherGradeDetailView, StudentGradeListView, StudentGradeDetailView)


urlpatterns = [
    path('grades/', GradeListView.as_view(), name='grade-list'),
    path('grades/create/', GradeCreateView.as_view(), name='grade-create'),
    path('grades/<uuid:grade_id>/', GradeDetailView.as_view(), name='grade-detail'),
    path('teacher/grades/', TeacherGradeListView.as_view(), name='teacher-grade-list'),
    path('teacher/grades/<uuid:grade_id>/', TeacherGradeDetailView.as_view(), name='teacher-grade-detail'),
    path('student/grades/', StudentGradeListView.as_view(), name='student-grade-list'),
    path('student/grades/<uuid:grade_id>/', StudentGradeDetailView.as_view(), name='student-grade-detail'),
    path('courses/<uuid:course_id>/stats/', CourseStatsView.as_view(), name='course-stats'),
    path('student/courses/<uuid:course_id>/stats/', StudentCourseStatsView.as_view(), name='student-course-stats'),
]
