"""Models for Bill app."""

from django.contrib.auth import get_user_model
from django.db import models
from model_utils.models import TimeStampedModel

User = get_user_model()

# Common stance choices used in both Bill and UserBillInteraction
STANCE_CHOICES = [
    ("support", "Support"),
    ("oppose", "Oppose"),
    ("watch", "Watch"),
]


class Tag(models.Model):
    """
    Represents tag.

    Tag bills to organize them.
    """

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Bill(models.Model):
    """Represents bill."""

    legiscan_bill_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True
    )
    bill_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    bill_title = models.CharField(max_length=255, null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name="bills", blank=True)
    admin_stance = models.CharField(
        max_length=10, choices=STANCE_CHOICES, null=True, blank=True
    )
    admin_note = models.TextField(null=True, blank=True)
    admin_expanded_analysis_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"Bill {self.bill_number}"


class UserBillInteraction(TimeStampedModel):
    """Represents a users interaction with a bill."""

    note = models.TextField(null=True, blank=True)
    stance = models.CharField(
        max_length=10, choices=STANCE_CHOICES, null=True, blank=True
    )
    ignore = models.BooleanField(default=False)
    bill = models.ForeignKey(
        Bill, on_delete=models.CASCADE, related_name="interactions"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bill_interactions"
    )

    class Meta:
        unique_together = ("user", "bill")
        ordering = ["modified"]

    def __str__(self):
        return f"Interaction {self.id} - Bill {self.bill_id}"


class UserKeyword(TimeStampedModel):
    """Represents keyword monitored by user."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="keywords")
    keyword = models.CharField(max_length=255)

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return f"Keyword '{self.keyword}' for {self.user}"
