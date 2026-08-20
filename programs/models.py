"""Pointi, tuzo, ustawi na matukio."""
from decimal import Decimal

from django.db import models, transaction
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.mixins import Bilingual, TimeStamped

from . import points as pts


# ===========================================================================
#  POINTI NA TUZO
# ===========================================================================
class PointRule(Bilingual):
    code = models.SlugField(max_length=40, unique=True)
    activity = models.CharField(_("Shughuli"), max_length=140)
    activity_en = models.CharField(max_length=140, blank=True)
    points = models.PositiveIntegerField(_("Pointi"), default=10)
    #: Chanzo cha pointi. `money` hutolewa na mfumo baada ya Pesapal
    #: kuthibitisha; `participation` hutolewa kwa mkono na afisa.
    kind = models.CharField(_("Aina"), max_length=16, choices=pts.PointKind.CHOICES,
                            default=pts.PointKind.PARTICIPATION)
    note = models.CharField(max_length=120, blank=True)
    note_en = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("Kanuni ya Pointi")
        verbose_name_plural = _("Kanuni za Pointi")

    def __str__(self):
        return self.activity

    @property
    def needs_second_approval(self):
        return self.points > pts.SECOND_APPROVAL_ABOVE


class PointBoost(TimeStamped):
    """
    Bonasi ya muda kwa mfuko fulani.

    Badala ya kubandika "yatima mara 2" milele kwenye code, afisa
    huweka bonasi inayoisha: "mwezi huu, msaada wa mafuriko mara mbili".
    Hii inaelekeza michango pale panapohitajika SASA bila kuandika
    tathmini ya kudumu ya thamani ya mradi mmoja dhidi ya mwingine.
    """
    fund = models.ForeignKey("finance.Fund", on_delete=models.CASCADE,
                             related_name="point_boosts", verbose_name=_("Mfuko"))
    multiplier = models.DecimalField(_("Mara"), max_digits=4, decimal_places=2, default=2)
    starts_on = models.DateField(_("Kuanzia"), default=timezone.localdate)
    ends_on = models.DateField(_("Hadi"))
    reason = models.CharField(_("Sababu"), max_length=160)
    created_by = models.ForeignKey("accounts.User", null=True, blank=True,
                                   on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-starts_on"]
        verbose_name = _("Bonasi ya Pointi")
        verbose_name_plural = _("Bonasi za Pointi")

    def __str__(self):
        return f"{self.fund} ×{self.multiplier}"

    @classmethod
    def multiplier_for(cls, fund, on=None):
        """Mara zinazotumika kwa mfuko huu leo. Bila bonasi, ni 1."""
        if fund is None:
            return Decimal("1")
        on = on or timezone.localdate()
        row = (cls.objects.filter(fund=fund, is_active=True,
                                  starts_on__lte=on, ends_on__gte=on)
               .order_by("-multiplier").first())
        return row.multiplier if row else Decimal("1")


class PointTransaction(TimeStamped):
    """
    Leja ya pointi — haifutwi, salio linahesabiwa.

    Kosa lirekebishwe kwa `reverse()`, si kwa kufuta. Leja
    inayoweza kufutwa si leja; ni pendekezo. Ukaguzi wa baadaye
    unahitaji kuona kilichotokea, si kilichobaki.
    """
    member = models.ForeignKey("members.Member", on_delete=models.CASCADE,
                               related_name="point_transactions")
    rule = models.ForeignKey(PointRule, null=True, blank=True, on_delete=models.SET_NULL)
    kind = models.CharField(max_length=16, choices=pts.PointKind.CHOICES,
                            default=pts.PointKind.PARTICIPATION)
    points = models.IntegerField(help_text="Chanya = kupata, hasi = kutumia")
    reason = models.CharField(max_length=160, blank=True)
    source = models.CharField(max_length=80, blank=True)
    awarded_on = models.DateField(default=timezone.localdate)

    #: Nani ameziidhinisha. Tupu kwa pointi za malipo — hakuna
    #: binadamu anayehusika, Pesapal ndiye shahidi.
    awarded_by = models.ForeignKey("accounts.User", null=True, blank=True,
                                   on_delete=models.SET_NULL,
                                   related_name="points_awarded")
    #: Idhini ya pili kwa pointi kubwa (angalia SECOND_APPROVAL_ABOVE).
    approved_by = models.ForeignKey("accounts.User", null=True, blank=True,
                                    on_delete=models.SET_NULL,
                                    related_name="points_approved")
    reverses = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name="reversals")

    class Meta:
        ordering = ["-awarded_on", "-id"]
        verbose_name = _("Muamala wa Pointi")
        verbose_name_plural = _("Miamala ya Pointi")

    def __str__(self):
        return f"{self.member.full_name} {self.points:+d}"

    # -- Kutoa ---------------------------------------------------------------
    @classmethod
    def award(cls, member, rule, multiplier=1, source="", by=None, approved_by=None):
        return cls.objects.create(
            member=member, rule=rule, kind=rule.kind,
            points=rule.points * multiplier,
            reason=rule.activity, source=source,
            awarded_by=by, approved_by=approved_by,
        )

    @classmethod
    def award_money(cls, member, amount, fund=None, reason="", source=""):
        """
        Pointi za mchango. Huitwa na mfumo, si na binadamu.

        Kikomo cha `MONEY_CAP` kinaangaliwa hapa: mtu aliyefika kikomo
        cha kipindi hapati zaidi, na anayekaribia kufika anapata
        zilizobaki tu. Anarudishiwa idadi halisi iliyotolewa.
        """
        mult = PointBoost.multiplier_for(fund)
        want = pts.points_for_amount(amount, mult)
        if want <= 0:
            return None

        used = cls.money_points(member)
        room = max(pts.MONEY_CAP - used, 0)
        give = min(want, room)
        if give <= 0:
            return None

        return cls.objects.create(
            member=member, kind=pts.PointKind.MONEY, points=give,
            reason=reason or str(_("Mchango")), source=source)

    @transaction.atomic
    def reverse(self, by=None, reason=""):
        """Rekebisha kosa bila kuficha historia."""
        if self.reversals.exists():
            return self.reversals.first()
        return PointTransaction.objects.create(
            member=self.member, kind=pts.PointKind.REVERSAL,
            points=-self.points, reverses=self,
            reason=reason or str(_("Marekebisho: %s") % self.reason),
            source=self.source, awarded_by=by)

    # -- Kuhesabu ------------------------------------------------------------
    @classmethod
    def _period_start(cls, on=None):
        on = on or timezone.localdate()
        try:
            return on.replace(year=on.year - pts.PERIOD_YEARS)
        except ValueError:          # 29 Feb
            return on.replace(year=on.year - pts.PERIOD_YEARS, day=28)

    @classmethod
    def lifetime(cls, member):
        """Pointi zote tangu kujiunga. Hazipungui — za vyeti na heshima."""
        return cls.objects.filter(member=member).aggregate(s=Sum("points"))["s"] or 0

    @classmethod
    def period(cls, member):
        """Pointi za miaka mitatu iliyopita. Ndizo zinazoamua kiwango."""
        return (cls.objects.filter(member=member, awarded_on__gte=cls._period_start())
                .aggregate(s=Sum("points"))["s"] or 0)

    @classmethod
    def money_points(cls, member):
        """Pointi za fedha ndani ya kipindi — kwa ajili ya kikomo."""
        return (cls.objects
                .filter(member=member, kind=pts.PointKind.MONEY,
                        awarded_on__gte=cls._period_start())
                .aggregate(s=Sum("points"))["s"] or 0)

    @classmethod
    def by_kind(cls, member):
        """Mgawanyo wa pointi za kipindi kwa chanzo."""
        rows = (cls.objects.filter(member=member, awarded_on__gte=cls._period_start())
                .values("kind").annotate(total=Sum("points")))
        return {r["kind"]: r["total"] or 0 for r in rows}

    @classmethod
    def balance(cls, member):
        #: Jina la zamani. Salio la kiwango ni la kipindi, si la maisha.
        return cls.period(member)

    @classmethod
    def officer_today(cls, user):
        """Pointi ambazo afisa ametoa leo — kwa kikomo cha kila siku."""
        if user is None:
            return 0
        return (cls.objects
                .filter(awarded_by=user, awarded_on=timezone.localdate(),
                        points__gt=0)
                .aggregate(s=Sum("points"))["s"] or 0)


class Reward(Bilingual):
    title = models.CharField(_("Tuzo"), max_length=140)
    title_en = models.CharField(max_length=140, blank=True)
    description = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    points_required = models.PositiveIntegerField(_("Pointi zinazohitajika"), default=1000)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["points_required"]
        verbose_name = _("Tuzo")
        verbose_name_plural = _("Tuzo")

    def __str__(self):
        return self.title


# ===========================================================================
#  USTAWI
# ===========================================================================
class AssistanceType(Bilingual):
    name = models.CharField(max_length=80, unique=True)
    name_en = models.CharField(max_length=80, blank=True)
    icon = models.CharField(max_length=30, default="hand-heart")

    class Meta:
        verbose_name = _("Aina ya Msaada")
        verbose_name_plural = _("Aina za Msaada")

    def __str__(self):
        return self.name


class AssistanceRequest(TimeStamped):
    STATUS = [("pending", _("Inasubiri")), ("review", _("Kwenye Usahihishaji")),
              ("approved", _("Imeidhinishwa")), ("rejected", _("Imekataliwa")),
              ("paid", _("Imelipwa"))]

    reference = models.CharField(max_length=32, unique=True, blank=True)
    member = models.ForeignKey("members.Member", on_delete=models.PROTECT,
                               related_name="assistance_requests")
    assistance_type = models.ForeignKey(AssistanceType, on_delete=models.PROTECT)
    description = models.TextField(_("Maelezo"))
    amount_requested = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount_approved = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=12, choices=STATUS, default="pending")
    approved_by = models.ForeignKey("accounts.User", null=True, blank=True,
                                    on_delete=models.SET_NULL)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Ombi la Msaada")
        verbose_name_plural = _("Maombi ya Msaada")

    def __str__(self):
        return f"{self.reference} — {self.member.full_name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            from core.mixins import Sequence
            with transaction.atomic():
                seq = Sequence.next("welfare")
                self.reference = f"WR/{timezone.localdate().year}/{seq:04d}"
                super().save(*args, **kwargs)
            return
        super().save(*args, **kwargs)


# ===========================================================================
#  MATUKIO
# ===========================================================================
class EventType(Bilingual):
    name = models.CharField(max_length=80, unique=True)
    name_en = models.CharField(max_length=80, blank=True)
    slug = models.SlugField(max_length=40, unique=True)
    colour = models.CharField(max_length=20, default="#12864a")
    scene = models.CharField(max_length=20, default="tukio")

    class Meta:
        verbose_name = _("Aina ya Tukio")
        verbose_name_plural = _("Aina za Matukio")

    def __str__(self):
        return self.name


class Event(Bilingual, TimeStamped):
    STATUS = [("planned", _("Imepangwa")), ("done", _("Imefanyika")),
              ("postponed", _("Imeahirishwa")), ("cancelled", _("Imeghairiwa"))]

    title = models.CharField(_("Tukio"), max_length=180)
    title_en = models.CharField(max_length=180, blank=True)
    summary = models.TextField(_("Maelezo"), blank=True)
    summary_en = models.TextField(blank=True)
    event_type = models.ForeignKey(EventType, on_delete=models.PROTECT, related_name="events")
    venue = models.CharField(_("Ukumbi"), max_length=160, blank=True)
    venue_en = models.CharField(max_length=160, blank=True)
    region = models.ForeignKey("geo.Region", null=True, blank=True, on_delete=models.SET_NULL,
                               related_name="events")
    start_at = models.DateTimeField(_("Kuanza"))
    end_at = models.DateTimeField(_("Kumalizika"), null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default="planned")
    is_public = models.BooleanField(_("Ionekane kwenye tovuti"), default=True)
    capacity = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["start_at"]
        verbose_name = _("Tukio")
        verbose_name_plural = _("Matukio")

    def __str__(self):
        return self.title

    @property
    def scene(self):
        return self.event_type.scene

    @property
    def days_until(self):
        return (self.start_at.date() - timezone.localdate()).days

    @property
    def badge(self):
        return {"planned": "ok", "done": "ok", "postponed": "warn",
                "cancelled": "danger"}.get(self.status, "muted")

    def participant_count(self):
        return self.registrations.count()


class EventRegistration(TimeStamped):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    member = models.ForeignKey("members.Member", null=True, blank=True,
                               on_delete=models.SET_NULL, related_name="event_registrations")
    full_name = models.CharField(max_length=140, blank=True)
    phone = models.CharField(max_length=24, blank=True)
    email = models.EmailField(blank=True)
    attended = models.BooleanField(_("Alihudhuria"), default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Usajili wa Tukio")
        verbose_name_plural = _("Usajili wa Matukio")

    def __str__(self):
        return f"{self.full_name or self.member} @ {self.event}"
