from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BillListAPIView,
    BillSearchAPIView,
    BillDetailView,
    BillViewSet,
    UserBillInteractionListView,
    UserKeywordViewSet,
    AdminBillViewSet,
)


router = DefaultRouter()
router.register(r"", UserKeywordViewSet, basename="user-keywords")

urlpatterns = [
    # order-matters!
    # keywords
    path("user/keywords/", include(router.urls)),
    # search
    path("search/", BillSearchAPIView.as_view(), name="bill-search"),
    # tags, no-legiscan
    path("search-by-tags/", BillViewSet.as_view({"get": "filter_by_tags"})),
    path("tags/", BillViewSet.as_view({"get": "get_all_tags"})),
    # interaction
    path(
        "interactions/",
        UserBillInteractionListView.as_view(),
        name="user-bill-interactions",
    ),
    # list
    path("", BillListAPIView.as_view(), name="bill-list"),
    # detail
    path(
        "<str:legiscan_bill_id>/",
        BillDetailView.as_view(),
        name="bill-detail",
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
