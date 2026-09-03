"""Mikoa, wilaya, kata na matawi."""
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Zone(models.Model):
    """
    Kanda ya kiutawala ya MUWESTA. Kila kanda ina mratibu mmoja
    anayesimamia mikoa yote iliyo ndani yake.
    """
    name = models.CharField(_("Kanda"), max_length=80, unique=True)
    name_en = models.CharField(max_length=80, blank=True)
    code = models.SlugField(max_length=20, unique=True)
    coordinator = models.ForeignKey("accounts.User", null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name="zones",
                                    verbose_name=_("Mratibu"))
    office = models.CharField(_("Ofisi ya Kanda"), max_length=120, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("Kanda")
        verbose_name_plural = _("Kanda")

    def __str__(self):
        return self.name

    def tx(self, field):
        from django.utils.translation import get_language
        lang = (get_language() or "sw").lower()
        if lang.startswith("en"):
            return getattr(self, f"{field}_en", "") or getattr(self, field)
        return getattr(self, field)


class Region(models.Model):
    name = models.CharField(_("Mkoa"), max_length=80, unique=True)
    zone = models.ForeignKey(Zone, null=True, blank=True, on_delete=models.SET_NULL,
                             related_name="regions", verbose_name=_("Kanda"))
    code = models.CharField(max_length=10, blank=True)
    map_x = models.FloatField(default=50, help_text="Nafasi kwenye ramani (0-100)")
    map_y = models.FloatField(default=50)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Mkoa")
        verbose_name_plural = _("Mikoa")

    def __str__(self):
        return self.name


class District(models.Model):
    """Halmashauri: DC (Wilaya), MC (Manispaa), CC (Jiji), TC (Mji)."""
    KIND = [("DC", _("Wilaya")), ("MC", _("Manispaa")), ("CC", _("Jiji")), ("TC", _("Mji"))]

    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="districts")
    name = models.CharField(_("Wilaya"), max_length=80)
    kind = models.CharField(_("Aina"), max_length=2, choices=KIND, default="DC")

    class Meta:
        ordering = ["name", "kind"]
        # Mkoa mmoja unaweza kuwa na Kibaha TC na Kibaha DC — majina yanafanana
        # lakini ni halmashauri mbili tofauti, kwa hiyo `kind` ni sehemu ya ufunguo.
        unique_together = [("region", "name", "kind")]
        verbose_name = _("Halmashauri")
        verbose_name_plural = _("Halmashauri")

    def __str__(self):
        return f"{self.name} {self.kind} ({self.region.name})"

    @property
    def full_name(self):
        return f"{self.name} {self.kind}"


class Ward(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="wards")
    name = models.CharField(_("Kata"), max_length=80)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Kata")
        verbose_name_plural = _("Kata")

    def __str__(self):
        return self.name


class Branch(models.Model):
    name = models.CharField(_("Tawi"), max_length=120)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="branches")
    district = models.ForeignKey(District, null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name="branches")
    address = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=24, blank=True)
    email = models.EmailField(blank=True)
    contact_person = models.CharField(max_length=120, blank=True)
    is_head_office = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_head_office", "name"]
        verbose_name = _("Tawi")
        verbose_name_plural = _("Matawi")

    def __str__(self):
        return self.name


class LeaderLevel(models.TextChoices):
    """
    Ngazi za uongozi, kutoka chini kwenda juu.

    Mpangilio ni MUHIMU: `LEVEL_ORDER` inautumia kupandisha matatizo na
    kuamua nani anaona nani. Ngazi ikiongezwa katikati, mpangilio huu
    ndio wa kubadilisha — si sehemu nyingine.
    """
    WARD = "ward", _("Kata")
    DISTRICT = "district", _("Wilaya")
    REGION = "region", _("Mkoa")
    ZONE = "zone", _("Kanda")
    NATIONAL = "national", _("Taifa")


#: Kutoka chini kwenda juu. Ngazi inayofuata ndiyo tatizo linapopandishwa.
LEVEL_ORDER = [LeaderLevel.WARD, LeaderLevel.DISTRICT, LeaderLevel.REGION,
               LeaderLevel.ZONE, LeaderLevel.NATIONAL]


def next_level(level):
    """Ngazi inayofuata juu, au `None` ikiwa tayari ni ya Taifa."""
    try:
        i = LEVEL_ORDER.index(level)
    except ValueError:
        return None
    return LEVEL_ORDER[i + 1] if i + 1 < len(LEVEL_ORDER) else None


class LeaderPost(models.TextChoices):
    CHAIR = "chair", _("Mwenyekiti")
    SECRETARY = "secretary", _("Katibu")
    TREASURER = "treasurer", _("Mweka Hazina")


class Leadership(models.Model):
    """
    Kiongozi wa ngazi fulani ya kiutawala.

    Eneo linahifadhiwa kwenye sehemu MOJA tu kati ya `ward`, `district`,
    `region`, `zone` — ile inayolingana na `level`. Ngazi ya Taifa haina
    eneo; inaona kila kitu.

    TAREHE NI MUHIMU. Bila `ended_on`, kiongozi wa zamani angeendelea
    kuona wanachama wote wa eneo lake milele. Na bila `started_on`,
    hutajua nani alikuwa kiongozi wakati uamuzi fulani ulipofanyika —
    jambo linalohitajika pale kunapokuwa na ubishi.
    """
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE,
                             related_name="leaderships", verbose_name=_("Mtumiaji"))
    level = models.CharField(_("Ngazi"), max_length=12, choices=LeaderLevel.choices)
    post = models.CharField(_("Wadhifa"), max_length=12, choices=LeaderPost.choices,
                            default=LeaderPost.CHAIR)

    ward = models.ForeignKey(Ward, null=True, blank=True, on_delete=models.CASCADE,
                             related_name="leaders", verbose_name=_("Kata"))
    district = models.ForeignKey(District, null=True, blank=True, on_delete=models.CASCADE,
                                 related_name="leaders", verbose_name=_("Wilaya"))
    region = models.ForeignKey(Region, null=True, blank=True, on_delete=models.CASCADE,
                               related_name="leaders", verbose_name=_("Mkoa"))
    zone = models.ForeignKey(Zone, null=True, blank=True, on_delete=models.CASCADE,
                             related_name="leaders", verbose_name=_("Kanda"))

    started_on = models.DateField(_("Ameanza"), default=timezone.localdate)
    ended_on = models.DateField(_("Amemaliza"), null=True, blank=True)
    note = models.CharField(_("Maelezo"), max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["level", "post"]
        verbose_name = _("Kiongozi")
        verbose_name_plural = _("Viongozi")
        indexes = [models.Index(fields=["level", "ended_on"])]

    def __str__(self):
        return f"{self.get_post_display()} — {self.area_name}"

    # -- Eneo ----------------------------------------------------------------
    @property
    def area(self):
        """Rekodi ya eneo lake, au `None` kwa ngazi ya Taifa."""
        return {
            LeaderLevel.WARD: self.ward,
            LeaderLevel.DISTRICT: self.district,
            LeaderLevel.REGION: self.region,
            LeaderLevel.ZONE: self.zone,
        }.get(self.level)

    @property
    def area_name(self):
        if self.level == LeaderLevel.NATIONAL:
            return str(_("Taifa"))
        area = self.area
        return str(area) if area else "—"

    @property
    def is_active(self):
        today = timezone.localdate()
        if self.started_on and self.started_on > today:
            return False
        return self.ended_on is None or self.ended_on >= today

    def clean(self):
        """
        Eneo lazima lilingane na ngazi.

        Kiongozi wa kata bila kata angekuwa hana anayemsimamia — na
        `scope` ingemrudishia wanachama sifuri bila kueleza kwa nini.
        """
        from django.core.exceptions import ValidationError

        needed = {
            LeaderLevel.WARD: "ward", LeaderLevel.DISTRICT: "district",
            LeaderLevel.REGION: "region", LeaderLevel.ZONE: "zone",
        }.get(self.level)

        if needed and not getattr(self, f"{needed}_id"):
            raise ValidationError({needed: _("Ngazi hii inahitaji eneo.")})
        if self.level == LeaderLevel.NATIONAL and any(
                [self.ward_id, self.district_id, self.region_id, self.zone_id]):
            raise ValidationError(_("Ngazi ya Taifa haina eneo maalum."))
        if self.ended_on and self.started_on and self.ended_on < self.started_on:
            raise ValidationError({"ended_on": _("Tarehe ya kumaliza ni kabla ya kuanza.")})
