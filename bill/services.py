"""Bill services."""

import logging
from .models import AppSettings, UserBillInteraction

logger = logging.getLogger(__name__)


def archive_all_active_interactions() -> int:
    """Archives all non-archived user bill interactions."""
    old_bill_interactions = UserBillInteraction.objects.filter(
        is_archived=False,
    )
    logger.info(
        "Archiving %s bill interactions",
        old_bill_interactions.count(),
    )
    return old_bill_interactions.update(is_archived=True)


def transition_session(latest_session_id: str) -> bool:
    """
    Returns True is interactions were archived during transition.

    Compares latest_session_id against the database.
    Archives bills and updates the DB if a new session is detected.
    """
    app_settings, _ = AppSettings.objects.get_or_create(id=1)

    # 1. Initialization bypass (first run ever)
    if app_settings.current_session_id is None:
        app_settings.current_session_id = latest_session_id
        app_settings.save()
        return False

    # 2. Session change detected
    if app_settings.current_session_id != latest_session_id:
        archive_all_active_interactions()
        app_settings.current_session_id = latest_session_id
        app_settings.save()
        return True

    return False
