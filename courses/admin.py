from django.contrib import admin
from .models import Course, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'is_active', 'created_at')
    search_fields = ('title',)
    list_filter = ('is_active', 'created_at')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'get_course_titles', 'status', 'enrolled_at', 'completed_at')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'course__title')
    list_filter = ('status', 'enrolled_at', 'completed_at')

    def get_course_titles(self, obj):
        return ", ".join([course.title for course in obj.course.all()])
    get_course_titles.short_description = 'Courses'