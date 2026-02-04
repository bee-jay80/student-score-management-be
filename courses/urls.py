from django.urls import path
from .views import (CourseCreateView, CourseListView, courseDetailView, CourseUpdateView, EnrollmentView, EnrollmentDetailView)

urlpatterns = [
    path("courses/", CourseListView.as_view(), name="course-list"),
    path("courses/create/", CourseCreateView.as_view(), name="course-create"),
    path("courses/<uuid:course_id>/", courseDetailView.as_view(), name="course-detail"),
    path("courses/<uuid:course_id>/update/", CourseUpdateView.as_view(), name="course-update"),
    path("courses/<uuid:course_id>/delete/", CourseUpdateView.as_view(), name="course-update"),
    path("courses/<uuid:course_id>/enroll/", EnrollmentView.as_view(), name="course-enroll"),
    path("enrollments/<uuid:enrollment_id>/", EnrollmentDetailView.as_view(), name="enrollment-detail"),
]