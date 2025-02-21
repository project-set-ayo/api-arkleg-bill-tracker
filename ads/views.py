"""Views for Ads."""

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Ad
from .serializers import AdSerializer
import random


class IsAdminGroup(permissions.BasePermission):
    """Allow only users in the 'admin' group to modify ads, others can only read."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  # Allow GET requests for all users

        # Check if the user is in the 'admin' group
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name="admin").exists()
        )


class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [IsAdminGroup]

    def list(self, request, *args, **kwargs):
        """Return ads with weight-based randomization."""
        ads = Ad.objects.filter(is_active=True)
        weighted_ads = [ad for ad in ads for _ in range(ad.weight)]
        random.shuffle(weighted_ads)
        return Response(AdSerializer(weighted_ads, many=True).data)

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[IsAdminGroup],
        url_path="admin-view",
    )
    def admin_view(self, request):
        """
        Admins get a unique list of all ads without weight duplication.
        """
        ads = Ad.objects.all().order_by("-created")
        return Response(AdSerializer(ads, many=True).data)
