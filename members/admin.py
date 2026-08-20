from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Application, Beneficiary, Card, Category, FamilyMember, Member


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "monthly_fee", "points_per_payment", "is_featured", "order")
    list_editable = ("monthly_fee", "order", "is_featured")


class FamilyInline(admin.TabularInline):
    model = FamilyMember
    extra = 0


class BeneficiaryInline(admin.TabularInline):
    model = Beneficiary
    extra = 0


class CardInline(admin.TabularInline):
    model = Card
    extra = 0
    readonly_fields = ("serial",)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("membership_no", "full_name", "category", "status",
                    "phone", "region", "joined_on")
    list_filter = ("status", "category", "region")
    search_fields = ("membership_no", "account_no", "full_name", "phone", "email", "national_id")
    readonly_fields = ("membership_no", "account_no", "created_at", "updated_at")
    inlines = [CardInline, FamilyInline, BeneficiaryInline]
    date_hierarchy = "joined_on"
    actions = ["suspend", "activate", "issue_card"]

    @admin.action(description=_("Sitisha wanachama waliochaguliwa"))
    def suspend(self, request, queryset):
        queryset.update(status="suspended")

    @admin.action(description=_("Rejesha wanachama waliochaguliwa"))
    def activate(self, request, queryset):
        queryset.update(status="active")

    @admin.action(description=_("Toa kadi mpya"))
    def issue_card(self, request, queryset):
        for m in queryset:
            Card.issue(m)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("reference", "full_name", "category", "status", "region", "created_at")
    list_filter = ("status", "category", "region")
    search_fields = ("reference", "full_name", "phone", "email")
    readonly_fields = ("reference", "created_at", "updated_at")
    actions = ["approve_selected", "activate_selected", "reject_selected"]

    @admin.action(description=_("Hakiki maombi (yasubiri malipo)"))
    def approve_selected(self, request, queryset):
        n = 0
        for app in queryset.filter(status__in=["pending", "review"]):
            app.approve(request.user)
            n += 1
        self.message_user(request, _(
            "Maombi %(n)d yamehakikiwa. Sasa yanasubiri malipo ya ada — "
            "wapewe kiungo cha /lipa/?ombi=<namba ya ombi>."
        ) % {"n": n})

    @admin.action(description=_("Kamilisha uanachama (ada imelipwa nje ya mfumo)"))
    def activate_selected(self, request, queryset):
        """
        Njia ya dharura: mtu amelipa taslimu au kwa benki na afisa
        amethibitisha. Kwa malipo ya mtandaoni hii haihitajiki — Pesapal
        inaanzisha `activate` yenyewe.
        """
        n = 0
        for app in queryset.filter(status="awaiting_payment", member__isnull=True):
            app.activate()
            n += 1
        self.message_user(request, _(
            "Wanachama %(n)d wamekamilishwa. Nenosiri la muda linapatikana "
            "kwenye ukurasa wa ombi."
        ) % {"n": n})

    @admin.action(description=_("Kataa maombi"))
    def reject_selected(self, request, queryset):
        queryset.update(status="rejected")


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("serial", "member", "issued_on", "expires_on", "is_active", "printed")
    list_filter = ("is_active", "printed")
    search_fields = ("serial", "member__full_name", "member__membership_no")


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "member", "relationship", "date_of_birth", "phone")
    list_filter = ("relationship",)
    search_fields = ("full_name", "member__full_name", "member__membership_no")
    autocomplete_fields = ["member"]


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ("full_name", "member", "relationship", "percentage_share", "phone")
    search_fields = ("full_name", "member__full_name", "member__membership_no")
    autocomplete_fields = ["member"]
