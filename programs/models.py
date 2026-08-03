"""Pointi, tuzo, ustawi na matukio."""
from decimal import Decimal

from django.db import models, transaction
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.mixins import Bilingual, TimeStamped


# ===========================================================================
#  POINTI NA TUZO
# ===========================================================================
class PointRule(Bilingual):
    code = models.SlugField(max_length=40, unique=True)
    activity = models.CharField(_("Shughuli"), max_length=140)
    activity_en = models.CharField(max_length=140, blank=True)
    points = models.PositiveIntegerField(_("Pointi"), default=10)
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


class PointTransaction(TimeStamped):
    """Leja ya pointi — haifutwi, salio linahesabiwa."""
    member = models.ForeignKey("members.Member", on_delete=models.CASCADE,
                               related_name="point_transactions")
    rule = models.ForeignKey(PointRule, null=True, blank=True, on_delete=models.SET_NULL)
    points = models.IntegerField(help_text="Chanya = kupata, hasi = kutumia")
    reason = models.CharField(max_length=160, blank=True)
    source = models.CharField(max_length=80, blank=True)
    awarded_on = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ["-awarded_on", "-id"]
        verbose_name = _("Muamala wa Pointi")
        verbose_name_plural = _("Miamala ya Pointi")

    def __str__(self):
        return f"{self.member.full_name} {self.points:+d}"

    @classmethod
    def award(cls, member, rule, multiplier=1, source=""):
        return cls.objects.create(
            member=member, rule=rule, points=rule.points * multiplier,
            reason=rule.activity, source=source,
        )

    @classmethod
    def balance(cls, member):
        return cls.objects.filter(member=member).aggregate(s=Sum("points"))["s"] or 0


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
