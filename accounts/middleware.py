# accounts/middleware.py
from django.conf import settings

class RefreshTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        new_access_token = getattr(request, "_new_access_token", None)

        if new_access_token:
            response.set_cookie(
                settings.JWT_ACCESS_COOKIE,
                new_access_token,
                httponly=True,
                secure=settings.JWT_COOKIE_SECURE,
                samesite=settings.JWT_COOKIE_SAMESITE,
                max_age=settings.ACCESS_TOKEN_LIFETIME.total_seconds(),
            )

        return response
