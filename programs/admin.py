from django.contrib import admin

from django.utils.translation import gettext_lazy as _

from . import points as pts
from .models import (AssistanceRequest, AssistanceType, Event, EventRegistration,
                     EventType, PointBoost, PointRule, PointTransaction, Reward)


@admin.register(PointRule)
class PointRuleAdmin(admin.ModelAdmin):
    list_display = ("activity", "code", "kind", "points", "is_active", "order")
    list_editable = ("points", "order", "is_active")
    list_filter = ("kind", "is_active")


@admin.register(PointBoost)
class PointBoostAdmin(admin.ModelAdmin):
    list_display = ("fund", "multiplier", "starts_on", "ends_on", "reason", "is_active")
    list_filter = ("is_active", "fund")

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    """
    Leja ya pointi. HAIFUTWI — kosa linarekebishwa kwa `reverse()`,
    ambayo huacha muamala wa asili na kuongeza wa marekebisho juu yake.
    Ukaguzi wa baadaye unahitaji kuona kilichotokea, si kilichobaki.
    """
    list_display = ("awarded_on", "member", "kind", "points", "reason",
                    "awarded_by", "source")
    list_filter = ("kind", "awarded_on")
    search_fields = ("member__full_name", "reason", "source")
    readonly_fields = ("reverses",)
    actions = ["reverse_selected"]

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description=_("Rekebisha (ondoa pointi zilizotolewa kimakosa)"))
    def reverse_selected(self, request, queryset):
        n = 0
        for txn in queryset.exclude(kind=pts.PointKind.REVERSAL):
            if not txn.reversals.exists():
                txn.reverse(by=request.user)
                n += 1
        self.message_user(request, _(
            "Miamala %(n)d imerekebishwa. Ya asili imebaki kwenye leja."
        ) % {"n": n})

    def save_model(self, request, obj, form, change):
        # Afisa hawezi kujipa pointi mwenyewe. Kamwe.
        own = getattr(request.user, "member", None)
        if own and obj.member_id == own.pk:
            self.message_user(request, _(
                "Huwezi kujipa pointi mwenyewe."), level="error")
            return
        if not obj.awarded_by_id:
            obj.awarded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ("title", "points_required", "is_active")


@admin.register(AssistanceType)
class AssistanceTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "icon")


@admin.register(AssistanceRequest)
class AssistanceRequestAdmin(admin.ModelAdmin):
    list_display = ("reference", "member", "assistance_type", "amount_requested",
                    "amount_approved", "status")
    list_filter = ("status", "assistance_type")
    search_fields = ("reference", "member__full_name")


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "scene")


class RegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 0


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_type", "start_at", "region", "status",
                    "is_public", "participant_count")
    list_filter = ("status", "event_type", "region", "is_public")
    search_fields = ("title", "venue")
    date_hierarchy = "start_at"
    inlines = [RegistrationInline]


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ("event", "member", "full_name", "phone", "attended")
    list_filter = ("attended", "event")
    search_fields = ("full_name", "phone", "member__full_name")
