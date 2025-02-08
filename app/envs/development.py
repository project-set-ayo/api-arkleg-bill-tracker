"""
Development settings for app project.
"""

from .base import *  # noqa

DEBUG = True
SECRET_KEY = (
    "django-insecure-!0%pkeilx*h-*iz@!^lfs_7irdbcaajph70s--6ibi_2pcz9y9"
)

BASE_FRONTEND_URL = "http://localhost:3000"

ALLOWED_HOSTS = ["backend", "localhost", "127.0.0.1"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost",
    "http://127.0.0.1",
    "http://0.0.0.0",
]

CORS_ALLOW_ALL_ORIGINS = True

# Email settings
# --- terminal
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# --- mail-service
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "")
EMAIL_USE_SSL = False
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")


# PayPal settings
PAYPAL_TEST = True

# ALLAUTH redirect URLs
EMAIL_CONFIRM_REDIRECT_BASE_URL = f"{BASE_FRONTEND_URL}/email/confirm/"
PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL = (
    f"{BASE_FRONTEND_URL}/password-reset/confirm/"
)
