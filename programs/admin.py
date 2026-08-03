from django.contrib import admin

from .models import (AssistanceRequest, AssistanceType, Event, EventRegistration,
                     EventType, PointRule, PointTransaction, Reward)


@admin.register(PointRule)
class PointRuleAdmin(admin.ModelAdmin):
    list_display = ("activity", "code", "points", "is_active", "order")
    list_editable = ("points", "order", "is_active")


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ("awarded_on", "member", "points", "reason", "source")
    list_filter = ("awarded_on",)
    search_fields = ("member__full_name", "reason", "source")


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
