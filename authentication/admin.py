from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User

# write your admin classes here
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["-date_joined"]
    list_display = [
        "email", "full_name", "phone_number",
        "is_email_verified", "profile_completion",
        "is_active", "is_staff", "date_joined",
    ]
    list_filter = ["is_staff", "is_active", "is_email_verified", "phone_verified", "country"]
    search_fields = ["email", "first_name", "last_name", "phone_number"]
    readonly_fields = ["date_joined", "last_activity", "profile_completion", "last_login"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {
            "fields": ("first_name", "last_name", "avatar", "bio", "date_of_birth")
        }),
        (_("Contact"), {
            "fields": ("phone_number", "phone_verified")
        }),
        (_("Address"), {
            "fields": (
                "address_line1", "address_line2",
                "city", "state", "postal_code", "country",
            )
        }),
        (_("Dashboard & Preferences"), {
            "fields": (
                "notification_preference",
                "is_email_verified",
                "profile_completion",
                "last_activity",
            )
        }),
        (_("Permissions"), {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        (_("Timestamps"), {"fields": ("date_joined", "last_login")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2"),
        }),
    )