"""Models for Ads."""

from django.db import models
from model_utils.models import TimeStampedModel


class Ad(TimeStampedModel):
    STYLE_CHOICES = [
        ("horizontal", "Horizontal"),
        ("vertical", "Vertical"),
        ("square", "Square"),
    ]
    title = models.CharField(max_length=255)
    image = models.FileField(upload_to="ads/", null=True, blank=True)
    link = models.URLField()
    weight = models.PositiveIntegerField(
        default=1
    )  # Higher weight = more frequent display
    is_active = models.BooleanField(default=True)
    style = models.CharField(
        max_length=20, choices=STYLE_CHOICES, blank=True, null=True
    )

    def __str__(self):
        return f"Ad: {self.title} (Weight: {self.weight})"
