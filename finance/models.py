"""Fedha: ada, michango, mifuko, kampeni, wahisani na leja."""
from decimal import Decimal

from django.db import models, transaction
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.mixins import Bilingual, Sequence, TimeStamped


# ===========================================================================
#  MIFUKO
# ===========================================================================
class Fund(Bilingual):
    """
    Mfuko wa fedha. Zaka na Waqf ni restricted — haziwezi kutumika
    kwa matumizi ya kawaida ya jumuiya.
    """
    name = models.CharField(_("Jina la Mfuko"), max_length=80, unique=True)
    name_en = models.CharField(max_length=80, blank=True)
    code = models.SlugField(max_length=40, unique=True)
    is_restricted = models.BooleanField(_("Fedha zenye masharti"), default=False)
    colour = models.CharField(max_length=20, default="#12864a")
    icon = models.CharField(max_length=30, default="coins")
    annual_target = models.DecimalField(_("Lengo la mwaka"), max_digits=16, decimal_places=2, default=0)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("Mfuko")
        verbose_name_plural = _("Mifuko")

    def __str__(self):
        return self.name


class PaymentMethod(models.TextChoices):
    MPESA = "mpesa", "M-Pesa"
    AIRTEL = "airtel", "Airtel Money"
    TIGO = "tigo", "Tigo Pesa"
    HALO = "halo", "HaloPesa"
    MIXX = "mixx", "Mixx by Yas"
    BANK = "bank", _("Benki")
    CASH = "cash", _("Taslimu")
    CARD = "card", _("Kadi ya Benki")


class PaymentStatus(models.TextChoices):
    CONFIRMED = "confirmed", _("Yaliyothibitisha")
    PENDING = "pending", _("Yanasubiri Uthibitisho")
    FAILED = "failed", _("Yaliyokosekana")
    CANCELLED = "cancelled", _("Yameghairiwa")


BADGE = {
    PaymentStatus.CONFIRMED: "ok",
    PaymentStatus.PENDING: "warn",
    PaymentStatus.FAILED: "danger",
    PaymentStatus.CANCELLED: "danger",
}


# ===========================================================================
#  AKAUNTI NA LEJA
# ===========================================================================
class Account(TimeStamped):
    """Akaunti ya mwanachama. Salio linahesabiwa kutoka kwenye leja."""
    member = models.OneToOneField("members.Member", on_delete=models.CASCADE, related_name="account")
    savings = models.DecimalField(_("Akiba"), max_digits=14, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("Akaunti ya Mwanachama")
        verbose_name_plural = _("Akaunti za Wanachama")

    def __str__(self):
        return f"{self.member.account_no} — {self.member.full_name}"

    def balance(self):
        agg = self.entries.aggregate(s=Sum("amount"))
        return agg["s"] or Decimal("0")

    def total_by_fund(self, code):
        agg = self.entries.filter(fund__code=code, amount__gt=0).aggregate(s=Sum("amount"))
        return agg["s"] or Decimal("0")


class LedgerEntry(TimeStamped):
    """
    Kila mwendo wa fedha. Haifutwi kamwe — kurekebisha kosa
    unaingiza entry ya kinyume (reversal).
    """
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="entries")
    fund = models.ForeignKey(Fund, on_delete=models.PROTECT, related_name="entries")
    amount = models.DecimalField(max_digits=14, decimal_places=2,
                                 help_text="Chanya = ingizo, hasi = toleo")
    description = models.CharField(max_length=200, blank=True)
    entry_date = models.DateField(default=timezone.localdate)
    reverses = models.ForeignKey("self", null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name="reversed_by")

    class Meta:
        ordering = ["-entry_date", "-id"]
        verbose_name = _("Ingizo la Leja")
        verbose_name_plural = _("Leja")

    def __str__(self):
        return f"{self.account.member.account_no} {self.amount:+,.2f}"


# ===========================================================================
#  MALIPO YA ADA
# ===========================================================================
class Payment(TimeStamped):
    member = models.ForeignKey("members.Member", on_delete=models.PROTECT, related_name="payments")
    receipt_no = models.CharField(_("Namba ya Risiti"), max_length=32, unique=True, blank=True)
    amount = models.DecimalField(_("Kiasi"), max_digits=14, decimal_places=2)
    year = models.PositiveSmallIntegerField(_("Mwaka"), default=timezone.now().year)
    period_month = models.PositiveSmallIntegerField(_("Mwezi"), null=True, blank=True)
    method = models.CharField(_("Njia ya Malipo"), max_length=12,
                              choices=PaymentMethod.choices, default=PaymentMethod.MPESA)
    bank_name = models.CharField(max_length=60, blank=True)
    reference = models.CharField(_("Kumbukumbu"), max_length=80, blank=True)
    idempotency_key = models.CharField(max_length=120, blank=True, db_index=True,
                                       help_text="Huzuia malipo kuingia mara mbili kutoka gateway")
    status = models.CharField(max_length=12, choices=PaymentStatus.choices,
                              default=PaymentStatus.CONFIRMED)
    paid_at = models.DateTimeField(_("Tarehe ya Malipo"), default=timezone.now)
    recorded_by = models.ForeignKey("accounts.User", null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name="payments_recorded")
    ledger_entry = models.OneToOneField(LedgerEntry, null=True, blank=True,
                                        on_delete=models.SET_NULL, related_name="payment")

    class Meta:
        ordering = ["-paid_at", "-id"]
        verbose_name = _("Malipo ya Ada")
        verbose_name_plural = _("Malipo ya Ada")
        indexes = [models.Index(fields=["status"]), models.Index(fields=["paid_at"])]
        constraints = [
            models.UniqueConstraint(fields=["idempotency_key"],
                                    condition=models.Q(idempotency_key__gt=""),
                                    name="uniq_payment_idempotency"),
        ]

    def __str__(self):
        return f"{self.receipt_no} — {self.member.full_name}"

    @property
    def badge(self):
        return BADGE.get(self.status, "muted")

    @property
    def method_label(self):
        label = self.get_method_display()
        return f"{label} - {self.bank_name}" if self.bank_name else label

    def save(self, *args, **kwargs):
        if not self.receipt_no:
            with transaction.atomic():
                seq = Sequence.next("receipt")
                self.receipt_no = f"MWST-R-{seq:06d}"
                super().save(*args, **kwargs)
            return
        super().save(*args, **kwargs)

    @transaction.atomic
    def post_to_ledger(self, fund_code="ada"):
        """Ingiza malipo kwenye leja na toa pointi. Haifanyi mara mbili."""
        if self.ledger_entry_id or self.status != PaymentStatus.CONFIRMED:
            return self.ledger_entry
        account, _created = Account.objects.get_or_create(member=self.member)
        fund = Fund.objects.get(code=fund_code)
        entry = LedgerEntry.objects.create(
            account=account, fund=fund, amount=self.amount,
            description=f"Ada ya uanachama — {self.receipt_no}",
            entry_date=self.paid_at.date(),
        )
        self.ledger_entry = entry
        self.save(update_fields=["ledger_entry", "updated_at"])

        from programs.models import PointRule, PointTransaction
        rule = PointRule.objects.filter(code="payment_on_time", is_active=True).first()
        if rule:
            PointTransaction.award(self.member, rule, source=self.receipt_no)
        return entry


# ===========================================================================
#  MICHANGO
# ===========================================================================
class Project(Bilingual, TimeStamped):
    STATUS = [("completed", _("Imekamilika")), ("ongoing", _("Inaendelea")),
              ("paused", _("Imesimama")), ("planned", _("Haijaanza"))]

    title = models.CharField(_("Mradi"), max_length=160)
    title_en = models.CharField(max_length=160, blank=True)
    summary = models.TextField(_("Maelezo"), blank=True)
    summary_en = models.TextField(blank=True)
    region = models.ForeignKey("geo.Region", null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=12, choices=STATUS, default="ongoing")
    target_amount = models.DecimalField(_("Lengo"), max_digits=16, decimal_places=2, default=0)
    scene = models.CharField(max_length=20, default="ujenzi",
                             help_text="Mchoro: msikiti, elimu, afya, maji, ujenzi...")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Mradi")
        verbose_name_plural = _("Miradi")

    def __str__(self):
        return self.title

    def raised(self):
        return self.contributions.filter(status=PaymentStatus.CONFIRMED)\
                   .aggregate(s=Sum("amount"))["s"] or Decimal("0")

    def progress(self):
        """Asilimia halisi — inaweza kuvuka 100 kama mradi umepokea zaidi ya lengo."""
        if not self.target_amount:
            return 0
        return round(float(self.raised()) / float(self.target_amount) * 100)

    def progress_bar(self):
        """Upana wa bar, umebanwa 100% ili usivuke kisanduku."""
        return min(self.progress(), 100)


class Donor(TimeStamped):
    TYPES = [("individual", _("Mtu binafsi")), ("company", _("Kampuni")),
             ("organisation", _("Shirika")), ("member", _("Mwanachama"))]

    name = models.CharField(_("Jina"), max_length=160)
    donor_type = models.CharField(max_length=16, choices=TYPES, default="individual")
    member = models.ForeignKey("members.Member", null=True, blank=True,
                               on_delete=models.SET_NULL, related_name="donor_profiles")
    region = models.ForeignKey("geo.Region", null=True, blank=True, on_delete=models.SET_NULL)
    country = models.CharField(max_length=60, blank=True, default="Tanzania")
    phone = models.CharField(max_length=24, blank=True)
    email = models.EmailField(blank=True)
    is_partner = models.BooleanField(_("Ni mdau"), default=False)
    is_active = models.BooleanField(default=True)
    #: Mhisani anaweza kufungua akaunti ili kufuatilia michango yake mwenyewe.
    #: Michango mingi haina akaunti — ndiyo maana ni hiari.
    user = models.OneToOneField("accounts.User", null=True, blank=True,
                                on_delete=models.SET_NULL, related_name="donor_profile",
                                verbose_name=_("Akaunti"))

    class Meta:
        ordering = ["name"]
        verbose_name = _("Mhisani / Mdau")
        verbose_name_plural = _("Wahisani na Wadau")

    def __str__(self):
        return self.name

    def total_given(self):
        return self.contributions.filter(status=PaymentStatus.CONFIRMED)\
                   .aggregate(s=Sum("amount"))["s"] or Decimal("0")


class Campaign(Bilingual, TimeStamped):
    title = models.CharField(_("Kampeni"), max_length=160)
    title_en = models.CharField(max_length=160, blank=True)
    summary = models.TextField(blank=True)
    summary_en = models.TextField(blank=True)
    fund = models.ForeignKey(Fund, null=True, blank=True, on_delete=models.SET_NULL,
                             related_name="campaigns")
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name="campaigns")
    target_amount = models.DecimalField(_("Lengo"), max_digits=16, decimal_places=2)
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField()
    scene = models.CharField(max_length=20, default="sadaka")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Kampeni")
        verbose_name_plural = _("Kampeni")

    def __str__(self):
        return self.title

    def raised(self):
        return self.contributions.filter(status=PaymentStatus.CONFIRMED)\
                   .aggregate(s=Sum("amount"))["s"] or Decimal("0")

    def progress(self):
        if not self.target_amount:
            return 0
        return round(float(self.raised()) / float(self.target_amount) * 100)

    def progress_bar(self):
        return min(self.progress(), 100)

    def days_left(self):
        return max((self.end_date - timezone.localdate()).days, 0)


class Contribution(TimeStamped):
    """Mchango wa hiari, Zaka, Sadaqa, Waqf au ufadhili wa mradi."""
    receipt_no = models.CharField(max_length=32, unique=True, blank=True)
    fund = models.ForeignKey(Fund, on_delete=models.PROTECT, related_name="contributions")
    member = models.ForeignKey("members.Member", null=True, blank=True,
                               on_delete=models.SET_NULL, related_name="contributions")
    donor = models.ForeignKey(Donor, null=True, blank=True,
                              on_delete=models.SET_NULL, related_name="contributions")
    donor_name = models.CharField(_("Jina la Mchangiaji"), max_length=160, blank=True)
    project = models.ForeignKey(Project, null=True, blank=True,
                                on_delete=models.SET_NULL, related_name="contributions")
    campaign = models.ForeignKey(Campaign, null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name="contributions")
    amount = models.DecimalField(_("Kiasi"), max_digits=16, decimal_places=2)
    method = models.CharField(max_length=12, choices=PaymentMethod.choices,
                              default=PaymentMethod.MPESA)
    bank_name = models.CharField(max_length=60, blank=True)
    reference = models.CharField(max_length=80, blank=True)
    idempotency_key = models.CharField(max_length=120, blank=True, db_index=True)
    status = models.CharField(max_length=12, choices=PaymentStatus.choices,
                              default=PaymentStatus.CONFIRMED)
    note = models.CharField(_("Maelezo"), max_length=200, blank=True)
    received_at = models.DateTimeField(default=timezone.now)
    recorded_by = models.ForeignKey("accounts.User", null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name="contributions_recorded")
    ledger_entry = models.OneToOneField(LedgerEntry, null=True, blank=True,
                                        on_delete=models.SET_NULL, related_name="contribution")

    class Meta:
        ordering = ["-received_at", "-id"]
        verbose_name = _("Mchango")
        verbose_name_plural = _("Michango")
        indexes = [models.Index(fields=["fund"]), models.Index(fields=["received_at"])]

    def __str__(self):
        return f"{self.receipt_no} — {self.display_name}"

    @property
    def display_name(self):
        return self.donor_name or (self.donor.name if self.donor else "") or \
               (self.member.full_name if self.member else "—")

    @property
    def badge(self):
        return BADGE.get(self.status, "muted")

    def save(self, *args, **kwargs):
        if not self.receipt_no:
            with transaction.atomic():
                seq = Sequence.next("contribution_receipt")
                self.receipt_no = f"MWST-M-{seq:06d}"
                super().save(*args, **kwargs)
            return
        super().save(*args, **kwargs)

    @transaction.atomic
    def post_to_ledger(self):
        if self.ledger_entry_id or not self.member_id or self.status != PaymentStatus.CONFIRMED:
            return None
        account, _c = Account.objects.get_or_create(member=self.member)
        entry = LedgerEntry.objects.create(
            account=account, fund=self.fund, amount=self.amount,
            description=f"{self.fund.name} — {self.receipt_no}",
            entry_date=self.received_at.date(),
        )
        self.ledger_entry = entry
        self.save(update_fields=["ledger_entry", "updated_at"])

        from programs.models import PointRule, PointTransaction
        rule = PointRule.objects.filter(code="donation", is_active=True).first()
        if rule:
            units = int(self.amount // Decimal("10000"))
            if units:
                PointTransaction.award(self.member, rule, multiplier=units,
                                       source=self.receipt_no)
        return entry


class Expense(TimeStamped):
    fund = models.ForeignKey(Fund, on_delete=models.PROTECT, related_name="expenses")
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(_("Maelezo"), max_length=200)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    spent_on = models.DateField(default=timezone.localdate)
    approved_by = models.ForeignKey("accounts.User", null=True, blank=True,
                                    on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-spent_on"]
        verbose_name = _("Matumizi")
        verbose_name_plural = _("Matumizi")

    def __str__(self):
        return f"{self.title} — {self.amount:,.2f}"
