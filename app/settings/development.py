"""Development settings for app project."""

import os
from .base import *  # noqa

print("Using development settings...")

INSTALLED_APPS += ["django_extensions"]

BASE_FRONTEND_URL = "http://localhost:3000"

DEBUG = True
SECRET_KEY = "django-insecure-!0%pkeilx*h-*iz@!^lfs_7irdbcaajph70s--6ibi_2pcz9y9"

ALLOWED_HOSTS = ["backend", "localhost", "127.0.0.1"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    "http://0.0.0.0",
    BASE_FRONTEND_URL,
]

CORS_ALLOW_ALL_ORIGINS = True

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Email settings
# --- terminal
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# --- mail-service
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")


# ALLAUTH - verify through email
ACCOUNT_EMAIL_VERIFICATION = True  # Always verify through email
# <EMAIL_CONFIRM_REDIRECT_BASE_URL>/<key>
EMAIL_CONFIRM_REDIRECT_BASE_URL = f"{BASE_FRONTEND_URL}/email/confirm/"
# <PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL>/<uidb64>/<token>/
PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL = (
    f"{BASE_FRONTEND_URL}/password-reset/confirm/"
)

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Storage
INSTALLED_APPS += ["storages"]

# AWS Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv(
    "AWS_S3_REGION_NAME", "us-east-1"
)  # Default to us-east-1
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

# Storage settings
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# Optional settings
AWS_QUERYSTRING_AUTH = False  # Public access, remove if using signed URLs
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}  # Cache for 1 day

# Media Files
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"


# MJML
MJML_BACKEND_MODE = os.getenv("MJML_BACKEND_MODE")
MJML_EXEC_CMD = os.getenv("MJML_EXEC_CMD")
# MJML_URL = os.getenv("MJML_URL")
# MJML_API_ID = os.getenv("MJML_API_ID")
# MJML_SECRET_KEY = os.getenv("MJML_SECRET_KEY")

# MJML_HTTPSERVERS = [
#    {
#        "URL": MJML_URL,
#        "HTTP_AUTH": (MJML_API_ID, MJML_SECRET_KEY),
#    },
# ]
