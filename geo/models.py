"""Mikoa, wilaya, kata na matawi."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Zone(models.Model):
    """
    Kanda ya kiutawala ya MWST. Kila kanda ina mratibu mmoja
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
