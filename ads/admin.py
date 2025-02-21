"""Ads Admin."""

from django.contrib import admin
from django.utils.html import format_html
from .models import Ad


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "preview_image",
        "link",
        "weight",
        "is_active",
        "created",
        "modified",
    )
    list_filter = ("is_active", "created", "modified")
    search_fields = ("title", "link")
    list_editable = ("weight", "is_active")
    ordering = ("-created",)

    def preview_image(self, obj):
        """Display a small preview of the ad image in the admin panel."""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;"/>',
                obj.image.url,
            )
        return "No Image"

    preview_image.short_description = "Image Preview"
