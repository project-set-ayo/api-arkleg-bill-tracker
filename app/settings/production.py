"""
Production settings for app project.
"""

from .base import *

print("Using production settings...")

DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

BASE_FRONTEND_URL = os.environ.get("BASE_FRONTEND_URL", "http://localhost:3000")

ALLOWED_HOSTS = [
    "localhost",  # remove
    "52.36.229.71",
    "arklegbilltracker.com",
    "staging.arklegbilltracker.com",
    "www.arklegbilltracker.com",
    "www.staging.arklegbilltracker.com",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost",  # remove
    "http://52.36.229.71",
    "https://arklegbilltracker.com",
    "https://staging.arklegbilltracker.com",
    BASE_FRONTEND_URL,
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
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True

# Static files
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
