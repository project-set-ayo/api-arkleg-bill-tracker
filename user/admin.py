from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import UserChangeForm, UserCreationForm
from .models import User


class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User

    # Show phone_number in admin list view
    list_display = ("email", "phone_number", "is_staff", "is_active")

    # Add phone_number to filtering options
    list_filter = ("email", "phone_number", "is_staff", "is_active")

    fieldsets = (
        (None, {"fields": ("email", "phone_number", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "phone_number",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )

    # Allow searching by email and phone number
    search_fields = ("email", "phone_number")

    ordering = ("email",)


admin.site.register(User, CustomUserAdmin)
