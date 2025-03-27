"""Legiscan related operations."""

import requests
from django.conf import settings
from enum import Enum
from typing import Union, Callable
from typing_extensions import TypeAlias


LegResponse: TypeAlias = Union[str, Union[dict, list[dict]]]


LEGISCAN_BILL_URL = "https://api.legiscan.com/?key={key}&op=getBill&id={bill_id}"
LEGISCAN_TEXT_SEARCH_URL = (
    "https://api.legiscan.com/?key={key}&op=getSearch&state={state}&query={query}"
)
LEGISCAN_SESSION_TEXT_SEARCH_URL = "https://api.legiscan.com/?key={key}&op=getSearch&id={session_id}&query={query}&page={page}"


class LegiscanStatus(Enum):
    """Legiscan Status."""

    NA = (0, "N/A", "Pre-filed or pre-introduction")
    INTRODUCED = (1, "Introduced", "")
    ENGROSSED = (2, "Engrossed", "")
    ENROLLED = (3, "Enrolled", "")
    PASSED = (4, "Passed", "")
    VETOED = (5, "Vetoed", "")
    FAILED = (6, "Failed", "Limited support based on state")
    OVERRIDE = (7, "Override", "Progress array only")
    CHAPTERED = (8, "Chaptered", "Progress array only")
    REFER = (9, "Refer", "Progress array only")
    REPORT_PASS = (10, "Report Pass", "Progress array only")
    REPORT_DNP = (11, "Report DNP", "Progress array only")
    DRAFT = (12, "Draft", "Progress array only")

    def __init__(self, code, description, notes):
        self._code_ = code
        self.description = description
        self.notes = notes

    def __str__(self):
        """Represent LegiscanStatus as str."""
        return f"{self.value} - {self.description}"

    @property
    def code(self):
        return self._code_

    @classmethod
    def from_code(cls, code: int):
        """Get status from code."""
        for status in cls:
            if status.code == code:
                return status
        raise ValueError(f"No LegiscanStatus found for code {code}")

    @classmethod
    def code_to_text(cls, code: int) -> str:
        """Get textual representation of status_code."""
        try:
            status_enum = cls.from_code(code)
            return status_enum.description + (
                f"- {status_enum.notes}" if status_enum.notes else ""
            )
        except ValueError:
            return "Unknown Status"


def fetch_bill(legiscan_bill_id) -> LegResponse:
    """Fetch bill data from Legiscan."""
    url = LEGISCAN_BILL_URL.format(
        key=settings.LEGISCAN_API_KEY,
        bill_id=legiscan_bill_id,
    )
    response = requests.get(url)

    if response.status_code != 200:
        return f"bill fetch failed: status_code {response.status_code}"

    def process_bill_data(obj: dict) -> dict:
        """
        Process bill data.

        - replace status code with text
        """
        if "status" in obj:
            obj["status"] = LegiscanStatus.code_to_text(obj["status"])

        return obj

    bill = response.json().get("bill")
    bill = process_bill_data(bill)

    return bill


def text_search_state(query) -> LegResponse:
    """
    Perform a full-text search for bills with Legiscan.

    :param query: The search term (e.g., keyword or phrase).
    :return: List of matching bills.
    """
    url = LEGISCAN_TEXT_SEARCH_URL.format(
        key=settings.LEGISCAN_API_KEY,
        state=settings.LEGISCAN_STATE,
        query=query,
    )
    response = requests.get(url)

    if response.status_code != 200:
        return f"text search failed: status_code {response.status_code}"

    return list(response.json().get("searchresult", {}).values())


def text_search_state_no_summary(query: str) -> Callable[[str], list]:
    """Run text search without summary."""
    return text_search_state(query)[1:]  # Skip summary


def text_search_session(session_id, query, page) -> LegResponse:
    """
    Perform a full-text search for bills with Legiscan.

    :param query: The search term (e.g., keyword or phrase).
    :return: List of matching bills.
    """
    url = LEGISCAN_SESSION_TEXT_SEARCH_URL.format(
        key=settings.LEGISCAN_API_KEY,
        session_id=session_id,
        query=query,
        page=page,
    )
    response = requests.get(url)

    if response.status_code != 200:
        return f"text search failed: status_code {response.status_code}"

    return response.json().get("searchresult", {})
