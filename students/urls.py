from django.urls import path
from .views import StudentDetailView, StudentCreateView, StudentFieldUpdateRequestListView, StudentFieldUpdateRequestActionView

urlpatterns = [
    path('students/create/', StudentCreateView.as_view(), name='student-create'),
    path('students/<uuid:student_id>/', StudentDetailView.as_view(), name='student-detail'),
    path('students/field-requests/', StudentFieldUpdateRequestListView.as_view(), name='student-field-requests'),
    path('students/field-requests/<uuid:request_id>/action/', StudentFieldUpdateRequestActionView.as_view(), name='student-field-request-action'),
]