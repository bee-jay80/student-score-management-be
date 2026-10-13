from django.urls import path
from .views import TeacherCreateView, TeacherDetailView

urlpatterns = [
    path('teachers/create/', TeacherCreateView.as_view(), name='teacher-create'),
    path('teachers/<uuid:teacher_id>/', TeacherDetailView.as_view(), name='teacher-detail'),
]
