from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts.serializers import RegisterSerializer
from accounts.utils.registration import register_or_resend_otp
from courses.models import Course


User = get_user_model()


class RegisterCoursesTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Django Basics",
            duration=3,
            description="Introduction to Django.",
        )

    def test_registration_serializer_saves_selected_courses(self):
        serializer = RegisterSerializer(
            data={
                "email": "student@example.com",
                "first_name": "First",
                "last_name": "Student",
                "role": "student",
                "password": "Strong-password-123",
                "courses": [str(self.course.id)],
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertQuerySetEqual(user.courses.all(), [self.course])

    def test_registration_flow_saves_selected_courses(self):
        registration_data = {
            "email": "pending@example.com",
            "first_name": "Pending",
            "last_name": "Student",
            "courses": [self.course],
        }
        with (
            patch("accounts.utils.registration.create_otp", return_value="123456"),
            patch("accounts.utils.registration.threading.Thread"),
            patch("accounts.utils.registration.create_verification_token", return_value="token"),
            patch("accounts.utils.registration.set_pending_cookie"),
        ):
            user, response = register_or_resend_otp(registration_data)

        self.assertEqual(response.status_code, 201)
        self.assertQuerySetEqual(user.courses.all(), [self.course])

    def test_registration_serializer_rejects_inactive_courses(self):
        inactive_course = Course.objects.create(
            title="Archived course",
            duration=1,
            description="No longer available.",
            is_active=False,
        )
        serializer = RegisterSerializer(
            data={
                "email": "student@example.com",
                "first_name": "First",
                "last_name": "Student",
                "role": "student",
                "password": "Strong-password-123",
                "courses": [str(inactive_course.id)],
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("courses", serializer.errors)

# Create your tests here.
