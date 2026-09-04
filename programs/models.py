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


# ===========================================================================
#  UONGOZI: MATATIZO NA MAWASILIANO
#
#  MTIRIRIKO WA TATIZO
#      Mwanachama -> Kata -> Wilaya -> Mkoa -> Kanda -> Taifa
#
#  Tatizo linaanzia kwa kiongozi wa kata ya mwanachama. Kiongozi
#  akishindwa kulitatua, analipandisha ngazi moja juu. Kila hatua
#  inahifadhiwa kwenye `CaseEvent` — nani, lini, na kwa nini.
#
#  Bila kumbukumbu hakuna uwajibikaji: mwanachama akiuliza "ombi langu
#  liko wapi", jibu lisiwe la kubahatisha.
# ===========================================================================
from geo.models import LeaderLevel, next_level


class CaseCategory(models.TextChoices):
    WELFARE = "welfare", _("Ustawi na Msaada")
    FINANCE = "finance", _("Ada na Malipo")
    MEMBERSHIP = "membership", _("Uanachama na Kadi")
    COMPLAINT = "complaint", _("Malalamiko")
    SUGGESTION = "suggestion", _("Ushauri na Mapendekezo")
    OTHER = "other", _("Nyingine")


class CaseStatus(models.TextChoices):
    OPEN = "open", _("Limefunguliwa")
    IN_PROGRESS = "in_progress", _("Linashughulikiwa")
    ESCALATED = "escalated", _("Limepandishwa")
    RESOLVED = "resolved", _("Limetatuliwa")
    CLOSED = "closed", _("Limefungwa")


class CaseUrgency(models.TextChoices):
    LOW = "low", _("Si ya Haraka")
    NORMAL = "normal", _("Kawaida")
    HIGH = "high", _("Ya Haraka")


class Case(TimeStamped):
    """
    Tatizo lililotolewa na mwanachama.

    `level` ni ngazi inayolishughulikia SASA — inabadilika kila
    linapopandishwa. `ward`, `district`, `region`, `zone` zinanakiliwa
    kutoka kwa mwanachama wakati wa kufungua, si kusomwa kila mara.

    Sababu ya kunakili: mwanachama akihama kata, matatizo yake ya zamani
    yanapaswa kubaki kwenye kumbukumbu ya kata aliyokuwepo — si kuhamia
    kwa kiongozi asiyeyajua.
    """
    reference = models.CharField(_("Namba ya Kumbukumbu"), max_length=40,
                                 unique=True, blank=True)
    member = models.ForeignKey("members.Member", on_delete=models.CASCADE,
                               related_name="cases", verbose_name=_("Mwanachama"))
    subject = models.CharField(_("Kichwa"), max_length=160)
    body = models.TextField(_("Maelezo"))
    category = models.CharField(_("Aina"), max_length=12,
                                choices=CaseCategory.choices,
                                default=CaseCategory.OTHER)
    urgency = models.CharField(_("Uzito"), max_length=8,
                               choices=CaseUrgency.choices,
                               default=CaseUrgency.NORMAL)
    status = models.CharField(_("Hali"), max_length=12, choices=CaseStatus.choices,
                              default=CaseStatus.OPEN, db_index=True)

    #: Ngazi inayolishughulikia sasa.
    level = models.CharField(_("Ngazi"), max_length=12, choices=LeaderLevel.choices,
                             default=LeaderLevel.WARD, db_index=True)

    ward = models.ForeignKey("geo.Ward", null=True, blank=True,
                             on_delete=models.SET_NULL, related_name="cases")
    district = models.ForeignKey("geo.District", null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name="cases")
    region = models.ForeignKey("geo.Region", null=True, blank=True,
                               on_delete=models.SET_NULL, related_name="cases")
    zone = models.ForeignKey("geo.Zone", null=True, blank=True,
                             on_delete=models.SET_NULL, related_name="cases")

    #: Tarehe ya kufika kwenye ngazi ya sasa. Amri ya kupandisha
    #: yenyewe inaitumia — si `created_at`, ambayo isingebadilika.
    level_since = models.DateTimeField(default=timezone.now, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution = models.TextField(_("Suluhisho"), blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Tatizo")
        verbose_name_plural = _("Matatizo")
        indexes = [models.Index(fields=["status", "level"])]

    def __str__(self):
        return f"{self.reference} — {self.subject[:40]}"

    def save(self, *args, **kwargs):
        if not self.reference:
            from core.models import Sequence
            year = timezone.localdate().year
            seq = Sequence.next(f"case:{year}")
            self.reference = f"TAT/{year}/{seq:04d}"
        # Nakili maeneo kutoka kwa mwanachama mara ya kwanza pekee.
        if not self.pk and self.member_id:
            self.ward = self.ward or self.member.ward
            self.district = self.district or self.member.district
            self.region = self.region or self.member.region
            self.zone = self.zone or (self.member.region.zone
                                      if self.member.region else None)
        super().save(*args, **kwargs)

    # -- Hali ----------------------------------------------------------------
    @property
    def is_open(self):
        return self.status in (CaseStatus.OPEN, CaseStatus.IN_PROGRESS,
                               CaseStatus.ESCALATED)

    @property
    def days_at_level(self):
        return (timezone.now() - self.level_since).days

    @property
    def badge(self):
        return {"open": "warn", "in_progress": "info", "escalated": "gold",
                "resolved": "ok", "closed": "muted"}.get(self.status, "muted")

    @property
    def area_name(self):
        area = {LeaderLevel.WARD: self.ward, LeaderLevel.DISTRICT: self.district,
                LeaderLevel.REGION: self.region, LeaderLevel.ZONE: self.zone}.get(self.level)
        return str(area) if area else str(_("Taifa"))

    # -- Hatua ---------------------------------------------------------------
    def log(self, kind, user=None, note="", to_level=""):
        return CaseEvent.objects.create(case=self, kind=kind, actor=user,
                                        note=note[:500], to_level=to_level)

    def escalate(self, user=None, note="", automatic=False):
        """
        Peleka tatizo ngazi moja juu.

        HATUA MOJA TU. Kuruka ngazi kungefanya kiongozi wa wilaya asijue
        tatizo lililo kwenye mkoa wake — na wakati wa kuuliza, kila mmoja
        angesema hakulijua.

        Likishafika Taifa, halipandi tena; ndiyo ngazi ya mwisho.
        """
        nxt = next_level(self.level)
        if nxt is None:
            return None
        self.level = nxt
        self.level_since = timezone.now()
        self.status = CaseStatus.ESCALATED
        self.save(update_fields=["level", "level_since", "status", "updated_at"])
        self.log("auto_escalated" if automatic else "escalated",
                 user=user, note=note, to_level=nxt)
        return nxt

    def resolve(self, user=None, resolution=""):
        self.status = CaseStatus.RESOLVED
        self.resolved_at = timezone.now()
        self.resolution = resolution
        self.save(update_fields=["status", "resolved_at", "resolution", "updated_at"])
        self.log("resolved", user=user, note=resolution)


class CaseEvent(TimeStamped):
    """
    Hatua moja kwenye maisha ya tatizo.

    Hazifutwi wala kuhaririwa. Ni kumbukumbu — ikiharirika, haina thamani
    wakati wa ubishi.
    """
    KIND = [
        ("opened", _("Limefunguliwa")),
        ("comment", _("Maoni")),
        ("escalated", _("Limepandishwa na kiongozi")),
        ("auto_escalated", _("Limepanda lenyewe kwa muda")),
        ("resolved", _("Limetatuliwa")),
        ("closed", _("Limefungwa")),
        ("reopened", _("Limefunguliwa upya")),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="events")
    kind = models.CharField(max_length=16, choices=KIND)
    actor = models.ForeignKey("accounts.User", null=True, blank=True,
                              on_delete=models.SET_NULL, related_name="case_events")
    note = models.TextField(blank=True)
    to_level = models.CharField(max_length=12, blank=True)
    #: Maoni ya ndani hayaonekani kwa mwanachama.
    internal = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("Hatua ya Tatizo")
        verbose_name_plural = _("Hatua za Matatizo")

    def __str__(self):
        return f"{self.case.reference} — {self.get_kind_display()}"


class Broadcast(TimeStamped):
    """
    Tangazo la kiongozi kwa wanachama wa eneo lake.

    Wanaolengwa hawanakiliwi kwenye jedwali; wanahesabiwa wakati wa
    kusoma kwa kutumia ufinyu ule ule wa `geo.scope`. Faida: mwanachama
    mpya wa kata anaona matangazo yaliyopita, na aliyehama haoni ya
    kata aliyoiacha.
    """
    sender = models.ForeignKey("accounts.User", on_delete=models.CASCADE,
                               related_name="broadcasts", verbose_name=_("Mtumaji"))
    level = models.CharField(_("Ngazi"), max_length=12, choices=LeaderLevel.choices)
    ward = models.ForeignKey("geo.Ward", null=True, blank=True,
                             on_delete=models.CASCADE, related_name="broadcasts")
    district = models.ForeignKey("geo.District", null=True, blank=True,
                                 on_delete=models.CASCADE, related_name="broadcasts")
    region = models.ForeignKey("geo.Region", null=True, blank=True,
                               on_delete=models.CASCADE, related_name="broadcasts")
    zone = models.ForeignKey("geo.Zone", null=True, blank=True,
                             on_delete=models.CASCADE, related_name="broadcasts")

    subject = models.CharField(_("Kichwa"), max_length=160)
    body = models.TextField(_("Ujumbe"))
    #: Idadi ya waliolengwa wakati wa kutuma. Inahifadhiwa kwa sababu
    #: idadi hubadilika — wanachama wanaingia na kutoka.
    reached = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Tangazo la Kiongozi")
        verbose_name_plural = _("Matangazo ya Viongozi")

    def __str__(self):
        return self.subject[:50]

    @property
    def area_name(self):
        area = {LeaderLevel.WARD: self.ward, LeaderLevel.DISTRICT: self.district,
                LeaderLevel.REGION: self.region, LeaderLevel.ZONE: self.zone}.get(self.level)
        return str(area) if area else str(_("Taifa"))


class Thread(TimeStamped):
    """
    Mazungumzo kati ya mwanachama na uongozi wa ngazi fulani.

    Ni kati ya mwanachama na NGAZI, si mtu binafsi. Kiongozi akibadilika,
    mazungumzo yanabaki na yanaendelea — hayapotei na mtu aliyeondoka.
    """
    member = models.ForeignKey("members.Member", on_delete=models.CASCADE,
                               related_name="threads")
    level = models.CharField(max_length=12, choices=LeaderLevel.choices,
                             default=LeaderLevel.WARD)
    subject = models.CharField(_("Kichwa"), max_length=160, blank=True)
    last_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-last_at"]
        verbose_name = _("Mazungumzo")
        verbose_name_plural = _("Mazungumzo")

    def __str__(self):
        return f"{self.member.full_name} — {self.subject or '(bila kichwa)'}"

    def touch(self):
        self.last_at = timezone.now()
        self.save(update_fields=["last_at", "updated_at"])


class Message(TimeStamped):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey("accounts.User", null=True, blank=True,
                               on_delete=models.SET_NULL, related_name="sent_messages")
    #: True = kutoka kwa kiongozi. Tunaihifadhi badala ya kukisia kutoka
    #: kwa `sender`, kwa sababu kiongozi anaweza kubadilika baadaye.
    from_leader = models.BooleanField(default=False)
    body = models.TextField(_("Ujumbe"))
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("Ujumbe")
        verbose_name_plural = _("Ujumbe")

    def __str__(self):
        return self.body[:50]


class Chat(TimeStamped):
    """
    Mazungumzo kati ya VIONGOZI wawili.

    Ni tofauti na `Thread`, ambayo ni kati ya mwanachama na ngazi.
    Hapa ni kati ya watu wawili wenye nyadhifa — mwenyekiti wa kata na
    mwenyekiti wa wilaya yake, au wenyeviti wawili wa kata moja.

    `pair_key` ni funguo ya kipekee inayozuia mazungumzo mawili kati ya
    watu wale wale. Bila hiyo, kila mmoja angeanzisha yake na majibu
    yangetawanyika sehemu mbili.
    """
    a = models.ForeignKey("accounts.User", on_delete=models.CASCADE,
                          related_name="chats_a")
    b = models.ForeignKey("accounts.User", on_delete=models.CASCADE,
                          related_name="chats_b")
    pair_key = models.CharField(max_length=40, unique=True, db_index=True)
    last_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-last_at"]
        verbose_name = _("Mazungumzo ya Viongozi")
        verbose_name_plural = _("Mazungumzo ya Viongozi")

    def __str__(self):
        return f"{self.a} \u2194 {self.b}"

    @staticmethod
    def key_for(u1, u2):
        """Funguo isiyobadilika bila kujali nani alianzisha."""
        x, y = sorted([int(u1), int(u2)])
        return f"{x}-{y}"

    @classmethod
    def between(cls, u1, u2):
        """Rudisha mazungumzo yaliyopo, au yaunde."""
        key = cls.key_for(u1.pk, u2.pk)
        chat = cls.objects.filter(pair_key=key).first()
        if chat is None:
            first, second = (u1, u2) if u1.pk < u2.pk else (u2, u1)
            chat = cls.objects.create(a=first, b=second, pair_key=key)
        return chat

    def other(self, user):
        return self.b if self.a_id == user.pk else self.a

    def touch(self):
        self.last_at = timezone.now()
        self.save(update_fields=["last_at", "updated_at"])


class ChatMessage(TimeStamped):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey("accounts.User", on_delete=models.CASCADE,
                               related_name="chat_messages")
    body = models.TextField(_("Ujumbe"))
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("Ujumbe wa Kiongozi")
        verbose_name_plural = _("Ujumbe wa Viongozi")

    def __str__(self):
        return self.body[:50]
