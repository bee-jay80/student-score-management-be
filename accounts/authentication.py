# accounts/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

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

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            return user, validated_token

        except TokenError:
            # Access token expired → try refresh
            refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)

            if refresh_token is None:
                return None

            try:
                refresh = RefreshToken(refresh_token)

                # Generate new access token
                new_access_token = refresh.access_token

                request._new_access_token = str(new_access_token)

                validated_token = self.get_validated_token(str(new_access_token))
                user = self.get_user(validated_token)

                return user, validated_token

            except TokenError:
                return None
