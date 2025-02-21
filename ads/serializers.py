"""Serializers for Ads."""

from rest_framework import serializers
from .models import Ad


class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ["id", "title", "image", "link", "weight"]

    def validate(self, data):
        """Ensure image is required when creating an ad, but not when updating."""
        if self.instance is None and not data.get("image"):
            raise serializers.ValidationError(
                {"image": "An image is required for new ads."}
            )
        return data
