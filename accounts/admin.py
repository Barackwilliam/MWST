from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AuditLog, User, VerificationCode


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


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    """
    Code za SMS. Ni za kusoma tu — code yenyewe imehifadhiwa kama hash,
    kwa hiyo hakuna cha kuhariri. Ipo hapa kwa ajili ya kufuatilia:
    kuona ni nani aliomba code, mara ngapi, na kutoka IP ipi.
    """
    list_display = ("phone", "purpose", "attempts", "used_at",
                    "expires_at", "created_at")
    list_filter = ("purpose", "created_at")
    search_fields = ("phone", "reference", "user__username")
    readonly_fields = ("user", "phone", "purpose", "code_hash", "reference",
                       "attempts", "expires_at", "used_at", "ip_address",
                       "created_at", "updated_at")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False
