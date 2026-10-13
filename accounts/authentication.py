# accounts/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CookieJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):
        header = self.get_header(request)

        raw_token = None

        if header is not None:
            raw_token = self.get_raw_token(header)
        else:
            raw_token = request.COOKIES.get(settings.JWT_ACCESS_COOKIE)

        if raw_token is None:
            return None

        # First, try validating the provided access token (from header or cookie).
        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            logger.debug("Access token valid for user %s", getattr(user, 'email', str(user)))
            return user, validated_token
        except TokenError:
            # Access token invalid/expired — attempt silent refresh using refresh token cookie.
            logger.debug("Access token invalid/expired; attempting refresh from cookie")
            refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)

            if not refresh_token:
                # No refresh token available — authentication fails silently.
                return None

            try:
                refresh = RefreshToken(refresh_token)
            except TokenError:
                # Refresh token invalid/expired
                logger.debug("Refresh token invalid or expired")
                return None

            try:
                # Build a new access token from the refresh token
                new_access_token = refresh.access_token
                str_new_access = str(new_access_token)

                # Save the new token so middleware can set it as a cookie on the response
                request._new_access_token = str_new_access

                # Also inject Authorization header so downstream permission checks validate the new token
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {str_new_access}'

                # Validate the newly created access token and return the associated user
                validated_token = self.get_validated_token(str_new_access)
                user = self.get_user(validated_token)
                logger.debug("Successfully refreshed access token for user %s", getattr(user, 'email', str(user)))
                return user, validated_token
            except TokenError:
                # If anything goes wrong validating the new token, fail silently
                logger.exception("Error validating new access token")
                return None
            except Exception:
                logger.exception("Unexpected error during silent refresh")
                return None
