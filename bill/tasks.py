"""Bill tasks."""

from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail
from django_q.tasks import Schedule, async_task

from typing import Callable, Dict, List
from typing_extensions import TypeAlias

from .models import User, UserKeyword, UserBillInteraction
from .legiscan import text_search_state_no_summary
from .emails import format_email_digest


KeywordBills: TypeAlias = Dict[str, List[dict]]
UserKeywordsBills: TypeAlias = Dict[User, KeywordBills]


def is_upcoming_bill(bill: dict) -> bool:
    """Checks if a bill has a status_date or last_action_date from today onward."""
    today = datetime.today().date()

    def is_upcoming_date(date_str):
        """date_str is today or in the future."""
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        return date >= today

    return is_upcoming_date(bill["last_action_date"])


def format_bill(bill: dict) -> dict:
    """Formats a bill to include frontend URL."""
    return {
        "bill_number": bill["bill_number"],
        "title": bill["title"],
        "url": f"{settings.BASE_FRONTEND_URL}/bill/{bill['bill_id']}",
    }


def get_matching_bills_for_keyword(
    keyword: str, text_search_func: Callable[[str], list], keyword_cache: dict
) -> list:
    """
    Retrieve matching bills for a given keyword.

    Uses caching to avoid redundant API calls.
    """
    keyword = keyword.lower()

    if keyword not in keyword_cache:
        keyword_cache[keyword] = text_search_func(keyword)

    return keyword_cache[keyword]


def bills_for_user_keywords(
    text_search_func: Callable[[str], list] = text_search_state_no_summary,
) -> UserKeywordsBills:
    """Fetch new bills and send a single HTML digest email per user, optimizing for shared keywords."""
    user_bill_map = {}  # {(user, keyword): [bills]}
    keyword_cache = {}  # Cache to store search results per keyword

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

    # Iterate through UserKeyword entries
    for entry in UserKeyword.objects.select_related("user"):
        user = entry.user
        keyword = entry.keyword.lower()
        ignored_bill_numbers = ignored_bills_by_user.get(user.id, set())

        # Get matching bills using caching function
        matching_bills = get_matching_bills_for_keyword(
            keyword, text_search_func, keyword_cache
        )

        # Filter out ignored and non-upcoming bills
        filtered_bills = list(
            map(
                format_bill,
                filter(
                    lambda bill: bill["bill_number"] not in ignored_bill_numbers,
                    matching_bills,
                ),
            )
        )

        if filtered_bills:
            user_bill_map.setdefault((user, keyword), []).extend(filtered_bills)

    # Reorganize data to group by user
    user_emails = {}
    for (user, keyword), bills in user_bill_map.items():
        user_emails.setdefault(user, {})[keyword] = bills

    return user_emails


def send_mail_for_keywords() -> None:
    """Send mail for keywords."""
    user_emails_data = bills_for_user_keywords(text_search_state_no_summary)

    # Send a single email per user
    for user, keyword_dict in user_emails_data.items():
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

    return f"Queued {len(user_emails_data)} HTML digest emails."
