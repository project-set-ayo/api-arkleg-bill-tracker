"""Development settings for app project."""

from .base import *  # noqa

print("Using development settings...")

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
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# --- mail-service
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = os.getenv("EMAIL_HOST")
# EMAIL_PORT = os.getenv("EMAIL_PORT")
# EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "")
# EMAIL_USE_SSL = False
# EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")


# ALLAUTH - verify through email
ACCOUNT_EMAIL_VERIFICATION = True  # Always verify through email
# <EMAIL_CONFIRM_REDIRECT_BASE_URL>/<key>
EMAIL_CONFIRM_REDIRECT_BASE_URL = f"{BASE_FRONTEND_URL}/email/confirm/"
# <PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL>/<uidb64>/<token>/
PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL = (
    f"{BASE_FRONTEND_URL}/password-reset/confirm/"
)
