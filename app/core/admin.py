"""
Django admin customization.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models  # noqa


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ["id"]
    list_display = ["email", "first_name", "last_name", "username"]
    fieldsets = (
        (None, {"fields": ("email", "first_name", "last_name",  "username", "password")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined",)}),
    )
    readonly_fields = ["email", "last_login", "date_joined"]

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "first_name",
                "last_name",
                "email",
                "password1",
                "password2",
                "username",
                "is_active",
                "is_staff",
                "is_superuser",
            ),
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Post)
admin.site.register(models.HashTag)
admin.site.register(models.Tag)
