# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.utils import timezone
# from .models import Grade
# from courses.models import Enrollment, CourseRole
# from django.db import transaction


# @receiver(post_save, sender=Grade)
# def update_enrollment_status_on_grade_save(sender, instance, created, **kwargs):
#     """
#     Update enrollment status based on grade score vs pass_mark.
#     - If score >= pass_mark: set status to "completed"
#     - If score < pass_mark: set status to "failed"
#     """
#     enrollment = instance.enrollment
    
#     if instance.score >= instance.pass_mark:
#         enrollment.status = "completed"
#         enrollment.completed_at = timezone.now()
#     else:
#         enrollment.status = "failed"
#         enrollment.completed_at = None
    
#     enrollment.save()

    # # After updating the single enrollment, check if the student has been graded
    # # on all enrollments for their current month. If all are passed, either
    # # advance the student's month_used by 1 or mark the course role(s) as
    # # completed when a role's duration equals the student's current month.
    # student = enrollment.student
    # current_month = student.month_used

    # # Get enrollments that belong to the student for the same month
    # enrollments_for_month = Enrollment.objects.filter(student=student, month=current_month)

    # if not enrollments_for_month.exists():
    #     return

    # # Ensure all enrollments for this month have grades and are passing
    # all_passed = True
    # for e in enrollments_for_month:
    #     try:
    #         g = e.grade
    #     except Grade.DoesNotExist:
    #         all_passed = False
    #         break
    #     if g.score < g.pass_mark:
    #         all_passed = False
    #         break

    # if not all_passed:
    #     return

    # # At this point the student has passed all courses for the current month.
    # # If any course's field.duration equals the student's current month, mark
    # # those course roles (and their enrollments) as completed instead of
    # # incrementing the student's month_used. Otherwise, increment month_used.
    # roles_to_complete = set()
    # for e in enrollments_for_month:
    #     role = e.course.field
    #     if role and role.duration == current_month:
    #         roles_to_complete.add(role)

    # with transaction.atomic():
    #     if roles_to_complete:
    #         now = timezone.now()
    #         # Mark related enrollments completed (they should already be completed but ensure timestamps)
    #         for e in enrollments_for_month:
    #             if e.course.field in roles_to_complete:
    #                 e.status = "completed"
    #                 e.completed_at = now
    #                 e.save()
    #                 # Optionally update the CourseRole status — note this is global.
    #                 role = e.course.field
    #                 if role and role.status != "completed":
    #                     role.status = "completed"
    #                     role.save()
    #         # Do not increment student's month_used in this case
    #     else:
    #         # Advance student's month_used by one
    #         student.month_used = student.month_used + 1
    #         student.save()
