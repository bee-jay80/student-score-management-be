import os
from datetime import timedelta
from pathlib import Path

import cloudinary
import dj_database_url
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR, ".env"))


def env_bool(name, default=False):
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in ("true", "1", "t", "yes", "on")


def env_list(name, default=()):
    value = os.getenv(name)
    if value is None:
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

DEBUG = env_bool("DEBUG", default=False)
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
if not DEBUG and not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set when DEBUG is false.")

ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    default=("localhost", "127.0.0.1") if DEBUG else (),
)
if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured("Set ALLOWED_HOSTS to the production hostnames.")

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'cloudinary',
    'corsheaders',
    'drf_spectacular',

    'accounts',
    'notifications',
    'courses',
    'students',
    'grades',
    'teachers',
    'forgot_password'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.RefreshTokenMiddleware',
]

ROOT_URLCONF = 'config.urls'

AUTH_USER_MODEL = 'accounts.User'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

# Default database if testing locally but online MYSQL database for production
# Database Configuration


# Database Configuration

if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    required_db_vars = [
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
        "DB_HOST",
        "DB_PORT",
    ]

    missing_vars = [
        name for name in required_db_vars
        if not os.getenv(name)
    ]

    if missing_vars:
        raise ImproperlyConfigured(
            f"Missing database environment variables: {', '.join(missing_vars)}"
        )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST"),
            "PORT": os.getenv("DB_PORT"),
            "CONN_MAX_AGE": 600,
            "CONN_HEALTH_CHECKS": True,
            # "OPTIONS": {
            #     "sslmode": os.getenv("DB_SSLMODE", "require"),
            # },
        }
    }

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# REST FRAMEWORK CONFIGURATION
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.authentication.CookieJWTAuthentication",
    ],

    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "10/min",
        "user": "5/min",
        "otp": "3/min",
        "notifications": "30/min",
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


# JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),

    "TOKEN_BLACKLIST_ENABLED": True,
}


# Cookie settings for JWT
JWT_ACCESS_COOKIE = "access_token"
JWT_REFRESH_COOKIE = "refresh_token"

JWT_COOKIE_SECURE = not DEBUG
JWT_COOKIE_HTTP_ONLY = True
JWT_COOKIE_SAMESITE = os.getenv("JWT_COOKIE_SAMESITE", "Lax")



# Email config for password reset (production-ready via .env)
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("SMTP_SERVER", default="localhost")
EMAIL_PORT = int(os.getenv("SMTP_PORT", default="587"))
EMAIL_HOST_USER = os.getenv("MAIL_USERNAME", default="")
EMAIL_HOST_PASSWORD = os.getenv("MAIL_PASSWORD", default="")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", default=True)
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", default=False)
DEFAULT_FROM_EMAIL = os.getenv("EMAIL", default=EMAIL_HOST_USER or "webmaster@localhost")



# Frontend Url
FRONTEND_URL = os.getenv("FRONTEND_URL", default="https://sfea.netlify.app").rstrip("/")

# Cloudinary Configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


# CORS Configuration
CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    default=("http://localhost:5173", FRONTEND_URL),
)

CORS_ALLOW_CREDENTIALS = True


CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    default=("http://localhost:5173", FRONTEND_URL),
)

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000" if not DEBUG else "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False)
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", default=False)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = (
    ("HTTP_X_FORWARDED_PROTO", "https")
    if env_bool("TRUST_PROXY_SSL_HEADER")
    else None
)


APP_API_SECRET_KEY = os.getenv("APP_SECRET_KEY", "")