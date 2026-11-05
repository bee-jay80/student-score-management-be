from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.accounts import urls as accounts_urls
from apps.courses import urls as courses_urls
from apps.forgot_password import urls as forgot_password_urls
from apps.notifications import urls as notifications_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/auth/", include(accounts_urls)),
    path("api/notifications/", include(notifications_urls)),
    path("api/courses/", include(courses_urls)),
    path("api/forgot-password/", include(forgot_password_urls)),

    # DRF Spectacular
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
