from django.contrib import admin
from .models import Branch, District, Region, Ward, Zone


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
