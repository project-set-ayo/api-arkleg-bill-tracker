"""Views for Bill app."""

import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.generics import ListAPIView
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsAdminUser
from .filters import filter_by_chamber, filter_by_type, search_by_bill_number
from .models import Tag, Bill, UserBillInteraction, UserKeyword
from .serializers import (
    UserBillInteractionSerializer,
    UserKeywordSerializer,
    BillSerializer,
    AdminBillSerializer,
)
from .utils import (
    fetch_bill,
    fetch_bills,
    full_text_search,
    process_bill,
    get_or_create_bill,
)


class BillListAPIView(APIView):
    def get(self, request):
        url = f"https://api.legiscan.com/?key={settings.LEGISCAN_API_KEY}&op=getMasterList&state={settings.LEGISCAN_STATE}"
        response = requests.get(url)

        if response.status_code != 200:
            return Response(
                {"detail": "Error fetching data."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        data = response.json()

        masterlist = data.get("masterlist", {})
        session = masterlist.pop("session")

        merged_bills = list(
            map(lambda b_data: process_bill(b_data), masterlist.values())
        )

        return Response(
            {"session": session, "bills": merged_bills},
            status=status.HTTP_200_OK,
        )


class BillViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["GET"], url_path="tags")
    def get_all_tags(self, request):
        """
        Returns a list of all tags in the system.
        Example: /api/bills/tags/
        """
        tags = Tag.objects.values_list("name", flat=True).distinct()
        return Response({"tags": list(tags)})

    @action(detail=False, methods=["GET"], url_path="filter-by-tags")
    def filter_by_tags(self, request):
        """
        Filters bills based on multiple tags.
        Example: /api/bill/filter-by-tags/?tags=healthcare,budget
        """
        tag_names = request.query_params.get("tags", "")

        if not tag_names:
            return Response({"error": "No tags provided"}, status=400)

        tag_list = [tag.strip() for tag in tag_names.split(",") if tag.strip()]
        if not tag_list:
            return Response({"error": "Invalid tag format"}, status=400)

        # Fetch bills that have ALL the provided tags
        bills = Bill.objects.filter(tags__name__in=tag_list).distinct()

        if not bills.exists():
            return Response(
                {"message": "No bills found matching the given tags"},
                status=404,
            )

        serializer = BillSerializer(bills, many=True)
        return Response(serializer.data)


class BillDetailView(APIView):
    """Handles retrieving bill details and adding/updating user interactions."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, legiscan_bill_id):
        """Retrieve bill details including LegiScan data, admin notes, and user interaction."""
        bill_data = fetch_bill(legiscan_bill_id)  # Fetch bill details from API
        bill = Bill.objects.filter(legiscan_bill_id=legiscan_bill_id).first()

        # Admin details (if bill exists in DB)
        admin_info = {
            "admin_note": bill.admin_note if bill else None,
            "admin_stance": bill.admin_stance if bill else None,
            "admin_expanded_analysis_url": (
                bill.admin_expanded_analysis_url if bill else None
            ),
        }

        # User interaction (if authenticated)
        user_interaction = None
        if request.user.is_authenticated:
            interaction = UserBillInteraction.objects.filter(
                user=request.user, bill=bill
            ).first()
            if interaction:
                user_interaction = UserBillInteractionSerializer(interaction).data

        return Response(
            {
                "bill_data": bill_data,  # Data from LegiScan API
                "admin_info": admin_info,
                "user_interaction": user_interaction,
            }
        )

    def post(self, request, legiscan_bill_id):
        """Allows authenticated users to create or update their interaction with a bill."""
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        bill_data = fetch_bill(legiscan_bill_id)  # Fetch bill details from API
        if not bill_data:
            return Response(
                {"error": "Invalid bill ID."}, status=status.HTTP_404_NOT_FOUND
            )

        # Ensure bill exists or create it without overriding existing values
        bill, created = Bill.objects.get_or_create(
            legiscan_bill_id=legiscan_bill_id,
            defaults={
                "bill_number": bill_data.get("bill_number"),
                "bill_title": bill_data.get("title")[:255],
            },
        )

        # Ensure user interaction is either updated or created
        user_interaction, created = UserBillInteraction.objects.update_or_create(
            user=request.user,
            bill=bill,
            defaults={
                "stance": request.data.get("stance"),
                "note": request.data.get("note"),
            },
        )

        return Response(
            UserBillInteractionSerializer(user_interaction).data,
            status=(status.HTTP_200_OK if not created else status.HTTP_201_CREATED),
        )

    def patch(self, request, legiscan_bill_id):
        """Allows authenticated users to partially update their interaction with a bill."""
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        bill = Bill.objects.filter(legiscan_bill_id=legiscan_bill_id).first()
        if not bill:
            return Response(
                {"error": "No interaction found for this bill."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_interaction = UserBillInteraction.objects.filter(
            user=request.user, bill=bill
        ).first()

        if not user_interaction:
            return Response(
                {"error": "No interaction found to update."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserBillInteractionSerializer(
            user_interaction, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, legiscan_bill_id):
        """Allows authenticated users to delete their interaction with a bill."""
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        bill = Bill.objects.filter(legiscan_bill_id=legiscan_bill_id).first()
        if not bill:
            return Response(
                {"error": "Bill not found."}, status=status.HTTP_404_NOT_FOUND
            )

        user_interaction = UserBillInteraction.objects.filter(
            user=request.user, bill=bill
        ).first()
        if not user_interaction:
            return Response(
                {"error": "No interaction found to delete."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_interaction.delete()
        return Response(
            {"message": "Your interaction has been removed."},
            status=status.HTTP_204_NO_CONTENT,
        )


# search-v2


@api_view(["GET"])
def sessions(request):
    """
    Fetches a list of all legislative sessions in Arkansas.
    """
    url = f"https://api.legiscan.com/?key={settings.LEGISCAN_API_KEY}&op=getSessionList&state={settings.LEGISCAN_STATE}"
    response = requests.get(url)

    if response.status_code == 200:
        return Response(response.json().get("sessions", []))
    return Response({"error": "Failed to fetch session list"}, status=500)


@api_view(["GET"])
def sponsors(request):
    """
    Fetches sponsors active in a given session based on the session_id.

    {"session": {...}, "people": [{...}]}
    """
    session_id = request.query_params.get("session_id")

    if not session_id:
        return Response({"error": "session_id is required"}, status=400)

    url = f"https://api.legiscan.com/?key={settings.LEGISCAN_API_KEY}&op=getSessionPeople&id={session_id}"
    response = requests.get(url)

    if response.status_code == 200:
        return Response(response.json().get("sessionpeople", []))
    return Response({"error": "Failed to fetch session sponsors"}, status=500)


@api_view(["GET"])
def bills(request):
    """
    Fetches a list of bills for a given session.

    {"session": {...}, "bills": [{...}]}
    """
    session_id = request.query_params.get("session_id")

    if not session_id:
        return Response({"error": "session_id is required"}, status=400)

    url = f"https://api.legiscan.com/?key={settings.LEGISCAN_API_KEY}&op=getMasterList&id={session_id}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json().get("masterlist", {})
        session_data = data.pop("session")
        bills_dict_data = data

        return Response(
            {
                "session": session_data,
                "bills": map(lambda bd: bd[1], bills_dict_data.items()),
            }
        )
    return Response({"error": "Failed to fetch bills"}, status=500)


@api_view(["GET"])
def sponsored_bills(request):
    """
    Fetches all bills sponsored by a specific person using the getSponsoredList API.

    Expected Query Parameter:
    - people_id: The ID of the sponsor (required)

    Example response from LegiScan:
    { "sponsor": {...}, "sessions": [{...}], "bills": [{...}]}
    """
    people_id = request.query_params.get("people_id")

    if not people_id:
        return Response({"error": "people_id is required"}, status=400)

    url = f"https://api.legiscan.com/?key={settings.LEGISCAN_API_KEY}&op=getSponsoredList&id={people_id}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json().get("sponsoredbills", {})
        return Response(
            {
                "sponsor": data.get("sponsor"),
                "sessions": data.get("sessions"),
                "bills": data.get("bills"),
            }
        )
    return Response({"error": "Failed to fetch sponsored bills"}, status=500)


@api_view(["GET"])
def text_search_bills(request):
    """
    Search bills in a given session using the LegiScan getSearch API.

    Required Query Parameters:
    - session_id: The ID of the legislative session
    - query: The search term

    Optional Query Parameters:
    - page: The page number for pagination (default: 1)

    Example Request:
    GET /api/bills/search/?session_id=1234&query=education&page=2

    Response Format:
    {
        "searchresult": {
            "summary": {...},
            "results": [{...}, {...}]
        }
    }
    """
    session_id = request.query_params.get("session_id")
    query = request.query_params.get("query")
    page = request.query_params.get("page", 1)  # Default to page 1

    if not session_id or not query:
        return Response(
            {"error": "session_id and query are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Construct LegiScan API URL
    url = f"https://api.legiscan.com/?key={settings.LEGISCAN_API_KEY}&op=getSearch&id={session_id}&query={query}&page={page}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json().get("searchresult", {})
        summary = data.pop("summary")

        return Response(
            {
                "summary": summary,
                "bills": map(lambda bd: bd[1], data.items()),
            }
        )

    return Response(
        {"error": "Failed to fetch search results"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


# interactions & keywords


class UserBillInteractionViewSet(viewsets.ViewSet):
    """
    ViewSet for managing user interactions with bills.
    Handles listing all interactions, retrieving, updating, and deleting a specific interaction.
    """

    permission_classes = [IsAuthenticated]

    def retrieve(self, request, legiscan_bill_id=None):
        """Handles GET: Retrieve a specific user-bill interaction."""
        bill = get_object_or_404(Bill, legiscan_bill_id=legiscan_bill_id)
        interaction = UserBillInteraction.objects.filter(
            user=request.user, bill=bill
        ).first()

        if not interaction:
            return Response(
                {"error": "No interaction found for this bill."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(UserBillInteractionSerializer(interaction).data)

    def list(self, request):
        """Handles GET: List all interactions for the authenticated user."""
        interactions = UserBillInteraction.objects.filter(user=request.user).order_by(
            "-modified"
        )
        serializer = UserBillInteractionSerializer(interactions, many=True)
        return Response(serializer.data)

    def destroy(self, request, legiscan_bill_id=None):
        """Handles DELETE: Deletes a user's interaction with a bill."""
        bill = get_object_or_404(Bill, legiscan_bill_id=legiscan_bill_id)
        interaction = UserBillInteraction.objects.filter(
            user=request.user, bill=bill
        ).first()

        if not interaction:
            return Response(
                {"error": "No interaction found to delete."},
                status=status.HTTP_404_NOT_FOUND,
            )

        interaction.delete()
        return Response(
            {"message": "Interaction deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(detail=True, methods=["POST", "PATCH"], url_path="update-or-create")
    def update_or_create_interaction(self, request, legiscan_bill_id=None):
        """
        Handles POST & PATCH: Creates or updates a user's interaction with a bill.
        If an interaction exists, update it. If not, create a new one.
        """
        bill = get_or_create_bill(legiscan_bill_id)

        interaction, created = UserBillInteraction.objects.update_or_create(
            user=request.user,
            bill=bill,
            defaults={
                "stance": request.data.get("stance"),
                "note": request.data.get("note"),
                "ignore": request.data.get("ignore"),
            },
        )

        return Response(
            UserBillInteractionSerializer(interaction).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class UserKeywordViewSet(viewsets.ModelViewSet):
    serializer_class = UserKeywordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Ensure users can only access their own keywords."""
        return UserKeyword.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Ensure user cannot add duplicate keywords."""
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Delete a keyword from the user’s list."""
        keyword_instance = self.get_object()
        if keyword_instance.user != request.user:
            return Response(
                {"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN
            )
        keyword_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["DELETE"])
    def bulk_delete(self, request):
        """Bulk delete multiple user keywords."""
        keyword_ids = request.data.get("keyword_ids", [])
        if not isinstance(keyword_ids, list) or not keyword_ids:
            return Response(
                {"error": "Provide a list of keyword IDs."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Filter only keywords belonging to the current user
        keywords_to_delete = UserKeyword.objects.filter(
            user=request.user, id__in=keyword_ids
        )
        deleted_count, _ = keywords_to_delete.delete()

        return Response({"deleted": deleted_count}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["GET"], url_path="matching-bills")
    def matching_bills(self, request):
        """Returns a list of bills that match the user's saved keywords."""

        user_keywords = self.get_queryset()
        matched_bills = {}

        for entry in user_keywords:
            keyword = entry.keyword.lower()
            bills = full_text_search(keyword)[1:]  # Skip summary result
            if bills:
                matched_bills[keyword] = bills

        return Response(matched_bills)


# admin-only


class AdminBillViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    def retrieve(self, request, legiscan_bill_id=None):
        """Handles GET: Returns a bill's admin details."""
        try:
            bill = Bill.objects.get(legiscan_bill_id=legiscan_bill_id)
            serializer = AdminBillSerializer(bill)
            return Response(serializer.data)
        except Bill.DoesNotExist:
            return Response({"error": "Bill not found"}, status=404)

    @action(detail=True, methods=["POST"], url_path="update-or-create")
    def update_or_create_bill(self, request, legiscan_bill_id=None):
        """
        Combines POST (create) and PATCH (update) into a single operation.
        If the bill exists, update it. If it doesn't, create it.
        """
        try:
            bill = Bill.objects.get(legiscan_bill_id=legiscan_bill_id)
            serializer = AdminBillSerializer(bill, data=request.data, partial=True)
        except Bill.DoesNotExist:
            request.data["legiscan_bill_id"] = legiscan_bill_id
            serializer = AdminBillSerializer(data=request.data)

        if serializer.is_valid():
            bill = serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def destroy(self, request, legiscan_bill_id=None):
        """Handles DELETE: Clears admin-related fields but does not delete the bill."""
        try:
            bill = Bill.objects.get(legiscan_bill_id=legiscan_bill_id)
            serializer = AdminBillSerializer()
            serializer.delete_admin_info(bill)
            return Response({"message": "Admin information removed."}, status=204)
        except Bill.DoesNotExist:
            return Response({"error": "Bill not found"}, status=404)
