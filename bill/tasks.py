from collections import defaultdict

from django.conf import settings
from django.core.mail import send_mail
from django_q.tasks import Schedule, async_task

from .models import UserKeyword
from .utils import format_email_digest, full_text_search


def check_bills_for_keywords():
    """Fetches new bills and sends a single HTML digest email per user."""

    user_keywords = UserKeyword.objects.select_related("user").all()

    # Create a mapping of {user: {keyword: [bills]}}
    user_bill_map = defaultdict(lambda: defaultdict(list))

    # Perform full-text search for each keyword
    for entry in user_keywords:
        matching_bills = full_text_search(entry.keyword.lower())[
            1:
        ]  # first item is summary, skip that

        if matching_bills:
            user_bill_map[entry.user][entry.keyword].extend(matching_bills)

    # Send a single email per user
    for user, keyword_dict in user_bill_map.items():
        email_subject, email_body = format_email_digest(user, keyword_dict)

        async_task(
            send_mail,
            email_subject,
            "",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
            html_message=email_body,
        )

    return f"Sent {len(user_bill_map)} HTML digest emails."


# Scheduled Tasks
Schedule("bill.tasks.check_bills_for_keywords", schedule_type="H")
