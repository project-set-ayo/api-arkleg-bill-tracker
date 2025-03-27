"""Models for Bill app."""

from django.contrib.auth import get_user_model
from django.db import models
from model_utils.models import TimeStampedModel

from .legiscan import fetch_bill

User = get_user_model()


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
        """Represent Tag as str."""
        return f"Tag: {self.name}"


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
        """Represent Bill as str."""
        return f"Bill: {self.bill_number}"

    @classmethod
    def get_or_create_bill(cls, legiscan_bill_id):
        """
        Retrieve a Bill from the database.

        Create and populate it with legiscan data if necessary.
        """
        bill, created = cls.objects.get_or_create(
            legiscan_bill_id=legiscan_bill_id,
            defaults={"bill_title": None, "bill_number": None},
        )

        # If bill was just created or lacks essential data, fetch from API
        if created or not bill.bill_title or not bill.bill_number:
            bill_data = fetch_bill(legiscan_bill_id)
            if bill_data:
                bill.bill_title = bill_data.get("title", "Unknown Title")
                bill.bill_number = bill_data.get("bill_number", "Unknown Number")
                bill.save()

        return bill


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
        """Represent UserBillInteraction as str."""
        return f"UserBillInteraction: {self.id} - Bill {self.bill_id}"


class BillAnalysis(models.Model):
    """Represents an expanded analysis document attached to a bill."""

    bill = models.ForeignKey(
        Bill, on_delete=models.CASCADE, related_name="bill_analyses"
    )
    file = models.FileField(upload_to="bill_analyses/", null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Bill Analysis"
        verbose_name_plural = "Bill Analyses"

    def __str__(self):
        """Represent BillAnalysis as str."""
        return f"BillAnalysis: {self.bill.bill_number} - {self.file.name}"


class UserKeyword(TimeStampedModel):
    """Represents keyword monitored by user."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="keywords")
    keyword = models.CharField(max_length=255)

    class Meta:
        ordering = ["created"]

    def __str__(self):
        """Represent UserKeyword as str."""
        return f"Keyword: '{self.keyword}' for {self.user}"
