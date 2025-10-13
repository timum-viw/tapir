from django.contrib import admin

from tapir.accounts.models import TapirUser
from tapir.accounts.api_key_models import APIKey


@admin.register(TapirUser)
class TapirUserAdmin(admin.ModelAdmin):
    list_display = ["username", "is_staff", "is_active", "email"]
    list_filter = ("is_staff", "is_active")
    search_fields = ["username", "first_name", "last_name", "email"]


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "key_preview", "is_active", "created_at", "last_used_at"]
    list_filter = ("is_active", "created_at")
    search_fields = ["name", "user__username", "user__email", "key"]
    readonly_fields = ["key", "created_at", "last_used_at"]
    autocomplete_fields = ["user"]
    
    @admin.display(description="Key Preview")
    def key_preview(self, obj):
        """Display only the first 8 characters of the key for security."""
        return f"{obj.key[:8]}..." if obj.key else ""
    
    fieldsets = (
        (None, {
            'fields': ('name', 'user', 'is_active')
        }),
        ('Key Information', {
            'fields': ('key', 'created_at', 'last_used_at'),
            'classes': ('collapse',),
        }),
    )
