import re

BILL_NUMBER_KEY = "bill_number"


def filter_by_chamber(chamber, bills):
    """
    Filter bills based on the chamber (House or Senate) using bill_number prefixes.

    :param bills: List of bill dictionaries with 'number' keys.
    :param chamber: "House" or "Senate".
    :return: Filtered list of bills belonging to the specified chamber.
    """
    chamber_patterns = {
        "House": re.compile(r"^H[A-Z]+"),  # Matches HB, HR, HJR, etc.
        "Senate": re.compile(r"^S[A-Z]+"),  # Matches SB, SR, SJR, etc.
    }

    pattern = chamber_patterns.get(chamber)
    return [
        bill for bill in bills if pattern.match(bill.get(BILL_NUMBER_KEY, ""))
    ]


def filter_by_type(bill_type, bills):
    """
    Filter bills based on type using bill_number prefixes.

    :param bills: List of bill dictionaries with 'number' keys.
    :param bill_type: "Bill", "Resolution", or "Joint Resolution".
    :return: Filtered list of bills belonging to the specified type.
    """
    type_patterns = {
        "Bill": re.compile(
            r"^[HS]B"
        ),  # Matches HB, SB (House Bill, Senate Bill)
        "Resolution": re.compile(
            r"^[HS]R"
        ),  # Matches HR, SR (House Resolution, Senate Resolution)
        "Joint Resolution": re.compile(
            r"^[HS]JR"
        ),  # Matches HJR, SJR (House/Senate Joint Resolution)
    }

    pattern = type_patterns.get(bill_type)
    return [
        bill for bill in bills if pattern.match(bill.get(BILL_NUMBER_KEY, ""))
    ]


def search_by_bill_number(search_term, bills):
    """
    Searches for bills that match a given bill_number pattern.
    - Matches full or partial bill numbers.
    - Supports chamber (H/S) and type (B/R/JR).
    - Returns all reasonable matches.

    :param bills: List of bill dictionaries with 'number' keys.
    :param search_term: The search input (e.g., 'HB100', 'SJR20', '200').
    :return: List of matching bills.
    """

    # Regex pattern to extract chamber, type, and digits
    match = re.match(r"^(H|S)?(B|R|JR)?(\d+)?$", search_term, re.IGNORECASE)

    if not match:
        return []

    chamber, bill_type, digits = match.groups()

    return list(
        filter(
            lambda bill: (
                (
                    not chamber
                    or bill.get(BILL_NUMBER_KEY, "").startswith(
                        chamber.upper()
                    )
                )
                and (
                    not bill_type
                    or bill.get(BILL_NUMBER_KEY, "")[1:].startswith(
                        bill_type.upper()
                    )
                )
                and (not digits or digits in bill.get(BILL_NUMBER_KEY, ""))
            ),
            bills,
        )
    )
