from django.conf import settings
from django.http import HttpResponseRedirect

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView, RegisterView

from .serializers import CustomRegisterSerializer


def email_confirm_redirect(request, key):
    return HttpResponseRedirect(f"{settings.EMAIL_CONFIRM_REDIRECT_BASE_URL}{key}/")


def password_reset_confirm_redirect(request, uidb64, token):
    return HttpResponseRedirect(
        f"{settings.PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL}{uidb64}/{token}/"
    )


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.BASE_FRONTEND_URL
    client_class = OAuth2Client


class CustomRegisterView(RegisterView):
    """
    Override dj-rest-auth's default RegisterView to use
    the CustomRegisterSerializer with first_name & last_name.
    """

    serializer_class = CustomRegisterSerializer
