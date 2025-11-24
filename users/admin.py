from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import UserAccount


@admin.register(UserAccount)
class UserAccountAdmin(BaseUserAdmin):
    """Admin configuration for UserAccount model."""

    list_display = [
        "email",
        "name",
        "username",
        "is_active",
        "is_email_verified",
        "is_staff",
        "is_superuser",
        "created_at",
        "profile_picture_preview",
    ]
    list_filter = [
        "is_active",
        "is_email_verified",
        "is_staff",
        "is_superuser",
        "created_at",
        "email_verified_at",
    ]
    search_fields = [
        "email",
        "username",
        "first_name",
        "last_name",
    ]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"
    readonly_fields = [
        "id",
        "created_at",
        "last_login",
        "profile_picture_preview",
    ]

    fieldsets = (
        (
            "Authentication",
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "username",
                    "profile_picture",
                    "profile_picture_preview",
                )
            },
        ),
        (
            "Status & Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
        (
            "Email Verification",
            {
                "fields": (
                    "is_email_verified",
                    "email_verified_at",
                    "email_verification_token",
                )
            },
        ),
        (
            "OTP",
            {
                "fields": (
                    "otp",
                    "otp_expiry",
                    "otp_sent_at",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "created_at",
                )
            },
        ),
        (
            "Groups & Permissions",
            {
                "fields": (
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
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
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    filter_horizontal = ["groups", "user_permissions"]

    def profile_picture_preview(self, obj):
        """Display profile picture thumbnail in admin."""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 50%;" />',
                obj.profile_picture.url,
            )
        return format_html('<span style="color: #999;">No image</span>')

    profile_picture_preview.short_description = "Profile Picture"

    def name(self, obj):
        """Display user's full name."""
        return obj.name

    name.short_description = "Name"
