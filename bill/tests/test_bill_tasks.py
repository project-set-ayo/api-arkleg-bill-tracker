from django.test import TestCase
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from bill.models import Bill, UserKeyword, UserBillInteraction
from bill.tasks import bills_for_user_keywords, is_upcoming_bill

from datetime import datetime, timedelta


User = get_user_model()


class IsUpcomingBillTest(TestCase):
    """Test suite for is_upcoming_bill(), now using only last_action_date."""

    def setUp(self):
        """Set up test dates."""
        self.today = datetime.today().date()
        self.past_date = (self.today - timedelta(days=5)).strftime("%Y-%m-%d")
        self.future_date = (self.today + timedelta(days=5)).strftime("%Y-%m-%d")

    def test_bill_with_future_last_action_date(self):
        """A bill with a future last_action_date should be considered upcoming."""
        bill = {"last_action_date": self.future_date}
        self.assertTrue(is_upcoming_bill(bill))

    def test_bill_with_today_last_action_date(self):
        """A bill with today's last_action_date should be considered upcoming."""
        bill = {"last_action_date": self.today.strftime("%Y-%m-%d")}
        self.assertTrue(is_upcoming_bill(bill))

    def test_bill_with_past_last_action_date(self):
        """A bill with a past last_action_date should not be considered upcoming."""
        bill = {"last_action_date": self.past_date}
        self.assertFalse(is_upcoming_bill(bill))

    def test_bill_with_no_last_action_date(self):
        """A bill with no last_action_date should not be considered upcoming."""
        bill = {}
        self.assertFalse(is_upcoming_bill(bill))
