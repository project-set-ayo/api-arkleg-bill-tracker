from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BillListAPIView,
    BillDetailView,
    BillViewSet,
    UserKeywordViewSet,
    UserBillInteractionViewSet,
    AdminBillViewSet,
    # search
    sessions,
    sponsors,
    bills,
    sponsored_bills,
    text_search_bills,
    # analysis
    list_bill_analyses,
    upload_bill_analysis,
    delete_bill_analysis,
)


user_keyword_router = DefaultRouter()

user_keyword_router.register(r"keyword", UserKeywordViewSet, basename="user-keywords")


urlpatterns = [
    # order-matters!
    # keywords
    path("user/", include(user_keyword_router.urls)),
    # analysis
    path("analysis/<str:bill_id>/", list_bill_analyses, name="bill-analysis-list"),
    path(
        "analysis/<str:bill_id>/upload/",
        upload_bill_analysis,
        name="bill-analysis-upload",
    ),
    path(
        "analysis/<int:analysis_id>/delete/",
        delete_bill_analysis,
        name="bill-analysis-delete",
    ),
    # tags, no-legiscan
    path("search-by-tags/", BillViewSet.as_view({"get": "filter_by_tags"})),
    path("tags/", BillViewSet.as_view({"get": "get_all_tags"})),
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
