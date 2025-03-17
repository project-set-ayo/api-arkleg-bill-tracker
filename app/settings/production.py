"""Production settings for app project."""

import os
from .base import *

print("Using production settings...")

DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

SUBDOMAIN = os.getenv("SUBDOMAIN", "")
DOMAIN = os.getenv("DOMAIN", "")

BASE_FRONTEND_URL = f"https://{SUBDOMAIN}.{DOMAIN}"


ALLOWED_HOSTS = [
    "api.arklegbilltracker.com",
    DOMAIN,
    f"{SUBDOMAIN}.{DOMAIN}",
]

CORS_ALLOWED_ORIGINS = [
    "https://api.arklegbilltracker.com",
    f"https://{DOMAIN}",
    f"https://{SUBDOMAIN}.{DOMAIN}",
]

CORS_ALLOW_ALL_ORIGINS = False

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = "DENY"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv("DB_HOST"),
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASS"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}


# ALLAUTH - verify through email
ACCOUNT_EMAIL_VERIFICATION = True  # Always verify through email
# <EMAIL_CONFIRM_REDIRECT_BASE_URL>/<key>
EMAIL_CONFIRM_REDIRECT_BASE_URL = f"{BASE_FRONTEND_URL}/email/confirm/"
# <PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL>/<uidb64>/<token>/
PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL = (
    f"{BASE_FRONTEND_URL}/password-reset/confirm/"
)

# Email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

# Static files
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
STATIC_URL = "static/"
STATIC_ROOT = "/var/www/api-arkleg-bill-tracker/static"

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
# MJML_BACKEND_MODE = os.getenv("MJML_BACKEND_MODE")
# MJML_EXEC_CMD = os.getenv("MJML_EXEC_CMD")
MJML_BACKEND_MODE = os.getenv("MJML_BACKEND_MODE")
MJML_URL = os.getenv("MJML_URL")
MJML_API_ID = os.getenv("MJML_API_ID")
MJML_SECRET_KEY = os.getenv("MJML_SECRET_KEY")

MJML_HTTPSERVERS = [
    {
        "URL": MJML_URL,
        "HTTP_AUTH": (MJML_API_ID, MJML_SECRET_KEY),
    },
]


# Django Q - TODO configure redis
Q_CLUSTER = {
    "name": "DjangoQ",
    "workers": int(os.getenv("Q_CLUSTER_WORKERS", 4)),  # Default to 4 workers
    "timeout": int(os.getenv("Q_CLUSTER_TIMEOUT", 60)),  # Execution timeout in seconds
    "retry": int(os.getenv("Q_CLUSTER_RETRY", 200)),  # Retry failed tasks after 200s
    "queue_limit": int(os.getenv("Q_CLUSTER_QUEUE_LIMIT", 50)),  # Max queued tasks
    "bulk": int(
        os.getenv("Q_CLUSTER_BULK", 10)
    ),  # Number of tasks workers process at a time
    "orm": "default",
}
