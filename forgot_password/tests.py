from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework import status
from unittest.mock import patch
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.hashers import make_password
from django.core.cache import cache

from accounts.utils.verification_session import create_verification_token

from .views import ForgotPasswordRequestView, OTPVerifyView, ResetPasswordView
from accounts.utils.otp import generate_otp
from accounts.models import EmailOTP

User = get_user_model()


class ForgotPasswordFlowTests(TestCase):
	def setUp(self):
		self.factory = RequestFactory()
		self.user = User.objects.create_user(email="test@example.com", password="oldpass")
		cache.clear()

	@patch('forgot_password.utils.emails.send_forgot_password_otp_email')
	@patch('accounts.utils.otp.generate_otp', return_value='123456')
	def test_full_forgot_password_flow(self, mocked_generate, mocked_send_email):
		# Request OTP
		req = self.factory.post('/', {'email': self.user.email}, content_type='application/json')
		view = ForgotPasswordRequestView.as_view()
		resp = view(req)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)

		# Grab verification_session cookie set by the response
		cookie = resp.cookies.get('verification_session')
		self.assertIsNotNone(cookie)
		token = cookie.value

		# Verify OTP
		req2 = self.factory.post('/', {'otp': '123456'}, content_type='application/json')
		req2.COOKIES['verification_session'] = token
		view_verify = OTPVerifyView.as_view()
		resp2 = view_verify(req2)
		self.assertEqual(resp2.status_code, status.HTTP_200_OK)

		# Reset password
		req3 = self.factory.post('/', {'new_password': 'newpass', 'confirm_password': 'newpass'}, content_type='application/json')
		# after OTP verify, a new pending cookie is set; reuse the cookie from resp2
		cookie2 = resp2.cookies.get('verification_session')
		self.assertIsNotNone(cookie2)
		req3.COOKIES['verification_session'] = cookie2.value
		view_reset = ResetPasswordView.as_view()
		resp3 = view_reset(req3)
		self.assertEqual(resp3.status_code, status.HTTP_200_OK)

		# Confirm password changed
		self.user.refresh_from_db()
		self.assertTrue(self.user.check_password('newpass'))

	@patch('forgot_password.utils.emails.send_forgot_password_otp_email')
	@patch('accounts.utils.otp.generate_otp', return_value='999999')
	def test_rate_limit_on_otp_requests(self, mocked_generate, mocked_send_email):
		view = ForgotPasswordRequestView.as_view()
		# make 5 requests within window
		for _ in range(5):
			req = self.factory.post('/', {'email': self.user.email}, content_type='application/json')
			resp = view(req)
			self.assertEqual(resp.status_code, status.HTTP_200_OK)

		# 6th request should be rate-limited
		req6 = self.factory.post('/', {'email': self.user.email}, content_type='application/json')
		resp6 = view(req6)
		self.assertEqual(resp6.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

	@patch('forgot_password.utils.emails.send_forgot_password_otp_email')
	@patch('accounts.utils.otp.generate_otp', return_value='222222')
	def test_invalid_otp(self, mocked_generate, mocked_send_email):
		# Request OTP
		req = self.factory.post('/', {'email': self.user.email}, content_type='application/json')
		resp = ForgotPasswordRequestView.as_view()(req)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)

		cookie = resp.cookies.get('verification_session')
		self.assertIsNotNone(cookie)
		token = cookie.value

		# Try verifying with wrong OTP
		req2 = self.factory.post('/', {'otp': '000000'}, content_type='application/json')
		req2.COOKIES['verification_session'] = token
		resp2 = OTPVerifyView.as_view()(req2)
		self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)

	def test_expired_otp(self):
		# create an expired EmailOTP record for the user
		expired = EmailOTP.objects.create(
			user=self.user,
			otp_hash=make_password('555555'),
			purpose='FORGOT_PASSWORD',
			expires_at=now() - timedelta(minutes=5),
		)

		# set verification cookie
		token = create_verification_token(self.user.id)
		req = self.factory.post('/', {'otp': '555555'}, content_type='application/json')
		req.COOKIES['verification_session'] = token
		resp = OTPVerifyView.as_view()(req)
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

	def test_invalid_verification_cookie(self):
		# No cookie provided
		req = self.factory.post('/', {'otp': '123456'}, content_type='application/json')
		resp = OTPVerifyView.as_view()(req)
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

	def test_reset_requires_verification(self):
		# Provide a valid verification token but no used ForgotPasswordRequest
		token = create_verification_token(self.user.id)
		req = self.factory.post('/', {'new_password': 'x', 'confirm_password': 'x'}, content_type='application/json')
		req.COOKIES['verification_session'] = token
		resp = ResetPasswordView.as_view()(req)
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
