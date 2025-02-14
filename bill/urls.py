from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BillListAPIView,
    BillSearchAPIView,
    BillDetailView,
    BillViewSet,
    UserKeywordViewSet,
    UserBillInteractionViewSet,
    AdminBillViewSet,
    sessions,
    sponsors,
    bills,
    sponsored_bills,
    text_search_bills,
)


user_keyword_router = DefaultRouter()
user_keyword_router.register(r"keyword", UserKeywordViewSet, basename="user-keywords")


urlpatterns = [
    # order-matters!
    # keywords
    path("user/", include(user_keyword_router.urls)),
    # search
    path("search/", BillSearchAPIView.as_view(), name="bill-search"),
    # tags, no-legiscan
    path("search-by-tags/", BillViewSet.as_view({"get": "filter_by_tags"})),
    path("tags/", BillViewSet.as_view({"get": "get_all_tags"})),
    # list
    path("", BillListAPIView.as_view(), name="bill-list"),
    # detail
    path(
        "<str:legiscan_bill_id>/",
        BillDetailView.as_view(),
        name="bill-detail",
    ),
    # search-v2
    path("search/session/", sessions, name="search-session"),
    path("search/sponsor/", sponsors, name="search-sponsor"),
    path("search/bill/", bills, name="search-bill"),
    path("search/sponsored-bills/", sponsored_bills, name="search-sponsored-bills"),
    path("search/text/", text_search_bills, name="search-text-bills"),
    # user-interaction
    path(
        "user/interaction/",
        UserBillInteractionViewSet.as_view({"get": "list"}),
        name="user-bill-interactions-list",
    ),
    path(
        "user/interaction/<str:legiscan_bill_id>/",
        UserBillInteractionViewSet.as_view(
            {
                "get": "retrieve",
                "post": "update_or_create_interaction",
                "patch": "update_or_create_interaction",
                "delete": "destroy",
            }
        ),
        name="user-bill-interactions-detail",
    ),
    # admin-only
    path(
        "admin/<str:legiscan_bill_id>/",
        AdminBillViewSet.as_view(
            {
                "get": "retrieve",
                "post": "update_or_create_bill",
                "patch": "update_or_create_bill",
                "delete": "destroy",
            }
        ),
    ),
]
