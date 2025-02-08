from django.test import TestCase

from ..filters import filter_by_chamber, filter_by_type, search_by_bill_number


class BillFilterTests(TestCase):
    """
    Tests for filtering bills by bill number, chamber, and type in a Django project.
    """

    @classmethod
    def setUpTestData(cls):
        """Define test bill data once for all test cases."""
        cls.bills = [
            {"bill_number": "HB1001", "title": "House Bill 1001"},
            {"bill_number": "SB2001", "title": "Senate Bill 2001"},
            {"bill_number": "HR3001", "title": "House Resolution 3001"},
            {
                "bill_number": "SJR4001",
                "title": "Senate Joint Resolution 4001",
            },
            {"bill_number": "HB200", "title": "House Bill 200"},
            {"bill_number": "SB200", "title": "Senate Bill 200"},
        ]

    # 1. Test for search_by_bill_number
    def test_search_by_bill_number_exact_match(self):
        result = search_by_bill_number("HB1001", self.bills)
        self.assertEqual(
            result, [{"bill_number": "HB1001", "title": "House Bill 1001"}]
        )

    def test_search_by_bill_number_partial_match(self):
        result = search_by_bill_number("200", self.bills)
        expected = [
            {"bill_number": "SB2001", "title": "Senate Bill 2001"},
            {"bill_number": "HB200", "title": "House Bill 200"},
            {"bill_number": "SB200", "title": "Senate Bill 200"},
        ]
        self.assertEqual(result, expected)

    def test_search_by_bill_number_chamber_filter(self):
        result = search_by_bill_number("H", self.bills)
        expected = [
            {"bill_number": "HB1001", "title": "House Bill 1001"},
            {"bill_number": "HR3001", "title": "House Resolution 3001"},
            {"bill_number": "HB200", "title": "House Bill 200"},
        ]
        self.assertEqual(result, expected)

    def test_search_by_bill_number_type_filter(self):
        result = search_by_bill_number("B", self.bills)
        expected = [
            {"bill_number": "HB1001", "title": "House Bill 1001"},
            {"bill_number": "SB2001", "title": "Senate Bill 2001"},
            {"bill_number": "HB200", "title": "House Bill 200"},
            {"bill_number": "SB200", "title": "Senate Bill 200"},
        ]
        self.assertEqual(result, expected)

    # 2. Test for filter_by_chamber
    def test_filter_by_chamber_house(self):
        result = filter_by_chamber("House", self.bills)
        expected = [
            {"bill_number": "HB1001", "title": "House Bill 1001"},
            {"bill_number": "HR3001", "title": "House Resolution 3001"},
            {"bill_number": "HB200", "title": "House Bill 200"},
        ]
        self.assertEqual(result, expected)

    def test_filter_by_chamber_senate(self):
        result = filter_by_chamber("Senate", self.bills)
        expected = [
            {"bill_number": "SB2001", "title": "Senate Bill 2001"},
            {
                "bill_number": "SJR4001",
                "title": "Senate Joint Resolution 4001",
            },
            {"bill_number": "SB200", "title": "Senate Bill 200"},
        ]
        self.assertEqual(result, expected)

    # 3. Test for filter_by_type
    def test_filter_by_type_bill(self):
        result = filter_by_type("Bill", self.bills)
        expected = [
            {"bill_number": "HB1001", "title": "House Bill 1001"},
            {"bill_number": "SB2001", "title": "Senate Bill 2001"},
            {"bill_number": "HB200", "title": "House Bill 200"},
            {"bill_number": "SB200", "title": "Senate Bill 200"},
        ]
        self.assertEqual(result, expected)

    def test_filter_by_type_resolution(self):
        result = filter_by_type("Resolution", self.bills)
        expected = [
            {"bill_number": "HR3001", "title": "House Resolution 3001"},
        ]
        self.assertEqual(result, expected)

    def test_filter_by_type_joint_resolution(self):
        result = filter_by_type("Joint Resolution", self.bills)
        expected = [
            {
                "bill_number": "SJR4001",
                "title": "Senate Joint Resolution 4001",
            },
        ]
        self.assertEqual(result, expected)
