"""Bill tasks."""

from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail
from django_q.tasks import Schedule, async_task

from .models import UserKeyword, UserBillInteraction
from .legiscan import text_search_state
from .emails import format_email_digest


def is_upcoming_bill(bill):
    """Checks if a bill has a status_date or last_action_date from today onward."""
    today = datetime.today().date().isoformat()
    return ("status_date" in bill and bill["status_date"] >= today) or (
        "last_action_date" in bill and bill["last_action_date"] >= today
    )


def format_bill(bill):
    """Formats a bill to include frontend URL."""
    return {
        "bill_number": bill["bill_number"],
        "title": bill["title"],
        "url": f"{settings.BASE_FRONTEND_URL}/bill/{bill['bill_id']}",
    }


def check_bills_for_keywords():
    """Fetch new bills and send a single HTML digest email per user."""
    user_bill_map = {}  # {(user, keyword): [bills]}

    # Get all users who have saved keywords
    users = set(UserKeyword.objects.values_list("user", flat=True))

    # Get ignored bills for each user
    ignored_bills_by_user = {
        user_id: set(
            UserBillInteraction.objects.filter(
                user_id=user_id, ignore=True
            ).values_list("bill__bill_number", flat=True)
        )
        for user_id in users
    }

    # Perform full-text search for each keyword
    for entry in UserKeyword.objects.select_related("user"):
        user = entry.user
        ignored_bill_numbers = ignored_bills_by_user.get(user.id, set())

        matching_bills = text_search_state(entry.keyword.lower())[1:]  # Skip summary

        # Use filter() to exclude ignored bills and non-upcoming bills
        filtered_bills = list(
            map(
                format_bill,
                filter(
                    lambda bill: is_upcoming_bill(bill)
                    and bill["bill_number"] not in ignored_bill_numbers,
                    matching_bills,
                ),
            )
        )

        if filtered_bills:
            user_bill_map.setdefault((user, entry.keyword), []).extend(filtered_bills)

    # Reorganize data to group by user
    user_emails = {}
    for (user, keyword), bills in user_bill_map.items():
        user_emails.setdefault(user, {})[keyword] = bills

    # Send a single email per user
    for user, keyword_dict in user_emails.items():
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

    return f"Sent {len(user_emails)} HTML digest emails."


# Scheduled Task
Schedule("bill.tasks.check_bills_for_keywords", schedule_type=Schedule.DAILY)
