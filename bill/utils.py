import requests
from django.conf import settings

from .models import Bill

# TODO consolidate functionality between get-bills and full-text-search (query)
LEGISCAN_API_KEY = settings.LEGISCAN_API_KEY
LEGISCAN_SEARCH_URL = (
    "https://api.legiscan.com/?key={key}&op=getSearch&state={state}&query={query}"
)


def fetch_legiscan_bill_data(legiscan_bill_id):
    """
    Fetches bill details from LegiScan API and returns relevant fields.
    """
    URL = "https://api.legiscan.com/?key={api_key}&op=getBill&id={bill_id}"

    url = URL.format(api_key=LEGISCAN_API_KEY, bill_id=legiscan_bill_id)
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        bill_data = data.get("bill", {})
        return {
            "bill_number": bill_data.get("bill_number"),
            "bill_title": bill_data.get("title"),
        }

    return None


# TODO: separate admin_data from bill_data coming from legiscan
def process_bill(bill_data):
    """Add admin data to bill."""
    bill_number = bill_data.get(
        "number"
    )  # getMasterList endpoint uses number instead of bill_number
    stored_bill = Bill.objects.filter(bill_number=bill_number).first()

    # Merge admin notes if the bill exists
    if stored_bill:
        bill_data["admin_stance"] = stored_bill.admin_stance
        bill_data["admin_note"] = stored_bill.admin_note
        bill_data["admin_expanded_analysis_url"] = (
            stored_bill.admin_expanded_analysis_url
        )
    else:
        # If no stored bill, set admin fields to None
        bill_data["admin_stance"] = None
        bill_data["admin_note"] = None
        bill_data["admin_expanded_analysis_url"] = None
    return bill_data


def fetch_bills():
    results = list()
    search_url = f"https://api.legiscan.com/?key={settings.LEGISCAN_API_KEY}&op=getSearch&state={settings.LEGISCAN_STATE}"
    response = requests.get(search_url)
    if response.status_code == 200:
        results = list(response.json().get("searchresult", {}).values())

    return results


def fetch_bill(legiscan_bill_id):
    search_url = f"https://api.legiscan.com/?key={settings.LEGISCAN_API_KEY}&op=getBill&id={legiscan_bill_id}"
    response = requests.get(search_url)
    if response.status_code == 200:
        return response.json().get("bill")


def full_text_search(query):
    """
    Perform a full-text search for bills using the LegiScan API.

    :param query: The search term (e.g., keyword or phrase).
    :return: List of matching bills.
    """
    url = LEGISCAN_SEARCH_URL.format(
        key=settings.LEGISCAN_API_KEY,
        state=settings.LEGISCAN_STATE,
        query=query,
    )
    response = requests.get(url)

    if response.status_code != 200:
        return []

    return list(response.json().get("searchresult", {}).values())


def get_or_create_bill(legiscan_bill_id):
    """
    Retrieves a Bill from the database, or creates and prepopulates it
    using data from the LegiScan API if necessary.
    """
    bill, created = Bill.objects.get_or_create(
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
