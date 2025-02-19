import requests
from django.conf import settings
from typing import Union
from typing_extensions import TypeAlias


LegResponse: TypeAlias = Union[str, Union[dict, list[dict]]]


LEGISCAN_BILL_URL = "https://api.legiscan.com/?key={key}&op=getBill&id={bill_id}"
LEGISCAN_TEXT_SEARCH_URL = (
    "https://api.legiscan.com/?key={key}&op=getSearch&state={state}&query={query}"
)
LEGISCAN_SESSION_TEXT_SEARCH_URL = "https://api.legiscan.com/?key={key}&op=getSearch&id={session_id}&query={query}&page={page}"


def fetch_bill(legiscan_bill_id) -> LegResponse:
    """Fetch bill data from Legiscan."""
    url = LEGISCAN_BILL_URL.format(
        key=settings.LEGISCAN_API_KEY,
        bill_id=legiscan_bill_id,
    )
    response = requests.get(url)

    if response.status_code != 200:
        return f"bill fetch failed: status_code {response.status_code}"

    return response.json().get("bill")


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
