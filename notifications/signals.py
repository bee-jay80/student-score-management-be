from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models.admin_notification import AdminNotification
from grades.models import Grade
from .models.student_grade_notification import StudentGradeNotification
from .utils.grade_notifications import send_grade_notification_email

User = get_user_model()


@receiver(post_save, sender=User)
def notify_admin_on_email_verification(sender, instance, created, **kwargs):
    if instance.is_email_verified and not instance.is_active:
        AdminNotification.objects.get_or_create(
            type="user_approval",
            related_user=instance
        )


@receiver(post_save, sender=Grade)
def notify_student_on_grade_creation(sender, instance, created, **kwargs):
    """Create notification and send email when a grade is created or updated."""
    if created:
        # Get the student from the enrollment
        student = instance.enrollment.student.user
        course_title = instance.enrollment.course.title
        
        # Create in-app notification
        StudentGradeNotification.objects.create(
            student=student,
            grade=instance,
            course_title=course_title,
            score=instance.score,
            total_mark=instance.total_mark,
            remark=instance.remark,
            is_emailed=False
        )
        
        # Send email notification
        try:
            send_grade_notification_email(
                student=student,
                course_title=course_title,
                score=instance.score,
                total_mark=instance.total_mark,
                remark=instance.remark
            )
            # Mark as emailed in the notification
            notification = StudentGradeNotification.objects.get(grade=instance)
            notification.is_emailed = True
            notification.save()
        except Exception as e:
            print(f"Error sending grade notification email: {str(e)}")
