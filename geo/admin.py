from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Branch, District, Leadership, Region, Ward, Zone


class DistrictInline(admin.TabularInline):
    model = District
    extra = 0


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "coordinator", "office", "region_count", "order")
    list_editable = ("order",)
    autocomplete_fields = ["coordinator"]

    @admin.display(description="Mikoa")
    def region_count(self, obj):
        return obj.regions.count()


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "zone", "code", "order")
    list_filter = ("zone",)
    search_fields = ("name",)
    inlines = [DistrictInline]


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "region")
    list_filter = ("region__zone", "region", "kind")
    search_fields = ("name",)


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ("name", "district")
    search_fields = ("name",)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "phone", "is_head_office")
    list_filter = ("region", "is_head_office")
    search_fields = ("name", "address")


@admin.register(Leadership)
class LeadershipAdmin(admin.ModelAdmin):
    """
    Viongozi wa ngazi zote.

    `area_name` inaonyesha eneo bila kujali ni kata, wilaya, mkoa au
    kanda — sehemu nne tofauti kwenye modeli, moja tu inayotumika.
    """
    list_display = ("user", "post", "level", "area_name", "started_on",
                    "ended_on", "is_active")
    list_filter = ("level", "post", "ended_on")
    search_fields = ("user__username", "user__first_name", "user__last_name",
                     "ward__name", "district__name", "region__name", "zone__name")
    autocomplete_fields = ("user",)
    date_hierarchy = "started_on"

    @admin.display(description=_("Eneo"))
    def area_name(self, obj):
        return obj.area_name

    @admin.display(description=_("Anatumika"), boolean=True)
    def is_active(self, obj):
        return obj.is_active
