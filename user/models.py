"""User models."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField
from citext import CIEmailField

from .managers import UserManager


class User(AbstractUser):
    """Representation of User."""

    username = None
    email = CIEmailField(_("email address"), unique=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    img = models.ImageField(upload_to="user_images/", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        """Represent User as str."""
        return f"User: {self.email}"
