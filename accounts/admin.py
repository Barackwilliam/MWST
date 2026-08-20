from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AuditLog, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "get_full_name", "role", "phone", "region", "is_active")
    list_filter = ("role", "is_active", "region")
    search_fields = ("username", "first_name", "last_name", "email", "phone")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("MUWESTA", {"fields": ("role", "phone", "photo", "branch", "region", "district", "two_factor")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("MUWESTA", {"fields": ("role", "phone")}),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "table_affected", "record_id", "ip_address")
    list_filter = ("action", "table_affected")
    search_fields = ("action", "detail", "record_id")
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False
