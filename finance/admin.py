from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (Account, Campaign, Contribution, Donor, Expense, Fund,
                     LedgerEntry, Payment, Project)


@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_restricted", "annual_target", "order")
    list_editable = ("annual_target", "order")


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("member", "balance_display", "savings")
    search_fields = ("member__full_name", "member__account_no")

    @admin.display(description=_("Salio"))
    def balance_display(self, obj):
        return f"{obj.balance():,.2f}"


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("entry_date", "account", "fund", "amount", "description")
    list_filter = ("fund", "entry_date")
    search_fields = ("account__member__full_name", "description")
    readonly_fields = ("created_at", "updated_at")

    def has_delete_permission(self, request, obj=None):
        return False  # Leja haifutwi — tumia reversal


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("receipt_no", "member", "amount", "method", "status", "paid_at")
    list_filter = ("status", "method", "year")
    search_fields = ("receipt_no", "member__full_name", "member__membership_no", "reference")
    readonly_fields = ("receipt_no", "ledger_entry", "created_at", "updated_at")
    date_hierarchy = "paid_at"
    actions = ["confirm_and_post"]

    @admin.action(description=_("Thibitisha na ingiza kwenye leja"))
    def confirm_and_post(self, request, queryset):
        n = 0
        for p in queryset:
            p.status = "confirmed"
            p.save(update_fields=["status", "updated_at"])
            p.post_to_ledger()
            n += 1
        self.message_user(request, _("Malipo %(n)d yamethibitishwa.") % {"n": n})


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ("receipt_no", "display_name", "fund", "amount", "status", "received_at")
    list_filter = ("fund", "status", "method")
    search_fields = ("receipt_no", "donor_name", "member__full_name", "donor__name")
    readonly_fields = ("receipt_no", "ledger_entry", "created_at", "updated_at")
    date_hierarchy = "received_at"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "region", "target_amount", "progress")
    list_filter = ("status", "region")
    search_fields = ("title",)


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("title", "target_amount", "progress", "days_left", "end_date", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title",)


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ("name", "donor_type", "region", "is_partner", "is_active")
    list_filter = ("donor_type", "is_partner", "is_active", "region")
    search_fields = ("name", "email", "phone")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("title", "fund", "amount", "spent_on")
    list_filter = ("fund",)
    date_hierarchy = "spent_on"
