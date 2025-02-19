"""Models for Ads."""

from django.db import models
from model_utils.models import TimeStampedModel


class Ad(TimeStampedModel):
    title = models.CharField(max_length=255)
    image = models.URLField()  # Using URLField for external images
    link = models.URLField()
    weight = models.PositiveIntegerField(
        default=1
    )  # Higher weight = more frequent display
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Ad: {self.title} (Weight: {self.weight})"
