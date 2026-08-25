"""Watumiaji, majukumu na kumbukumbu za matendo."""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.mixins import TimeStamped


class Role(models.TextChoices):
    SUPER_ADMIN = "super_admin", _("Msimamizi Mkuu")
    ADMIN = "admin", _("Msimamizi")
    MANAGEMENT = "management", _("Afisa wa Usimamizi")
    REGISTRATION = "registration", _("Afisa Usajili")
    FINANCE = "finance", _("Afisa Malipo ya Ada")
    CONTRIBUTIONS = "contributions", _("Afisa Michango")
    WELFARE = "welfare", _("Afisa Ustawi")
    OUTREACH = "outreach", _("Afisa Wadau na Wahisani")
    COORDINATOR = "coordinator", _("Mratibu wa Mkoa")
    MEMBER = "member", _("Mwanachama")
    DONOR = "donor", _("Mhisani")


#: Ukurasa wa kwanza baada ya kuingia, kwa kila jukumu
ROLE_HOME = {
    Role.SUPER_ADMIN: "core:national",
    Role.ADMIN: "core:national",
    Role.MANAGEMENT: "core:national",
    Role.REGISTRATION: "core:usajili",
    Role.FINANCE: "core:malipo",
    Role.CONTRIBUTIONS: "core:michango",
    Role.WELFARE: "core:national",
    Role.OUTREACH: "core:wadau",
    Role.COORDINATOR: "core:coordinator",
    Role.MEMBER: "core:member_dashboard",
    Role.DONOR: "core:donor_dashboard",
}

#: Majukumu ya nje ya ofisi — hawana ufikiaji wa dashibodi za watumishi.
PUBLIC_ROLES = [Role.MEMBER, Role.DONOR]

STAFF_ROLES = [r for r in Role if r not in PUBLIC_ROLES]


class User(AbstractUser):
    role = models.CharField(_("Jukumu"), max_length=24, choices=Role.choices, default=Role.MEMBER)
    phone = models.CharField(_("Simu"), max_length=24, blank=True)
    photo = models.ImageField(upload_to="users/", blank=True, null=True)
    branch = models.ForeignKey("geo.Branch", null=True, blank=True,
                               on_delete=models.SET_NULL, related_name="users")
    region = models.ForeignKey("geo.Region", null=True, blank=True,
                               on_delete=models.SET_NULL, related_name="users")
    district = models.ForeignKey("geo.District", null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name="users")
    two_factor = models.BooleanField(_("Uthibitisho wa hatua mbili"), default=False)

    class Meta:
        verbose_name = _("Mtumiaji")
        verbose_name_plural = _("Watumiaji")

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def initials(self):
        name = self.get_full_name() or self.username
        parts = [p for p in name.split() if p]
        if not parts:
            return "??"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    @property
    def is_staff_role(self):
        return self.role in [r.value for r in STAFF_ROLES]

    def home_url_name(self):
        return ROLE_HOME.get(self.role, "core:member_dashboard")


def _client_ip(request):
    """
    Anwani ya IP ya mteja.

    `X-Forwarded-For` inatumwa na KIVINJARI; proxy huongeza IP halisi
    MWISHONI. Kuchukua ya kwanza kunamruhusu mtu kubandika IP ya uongo,
    na kumbukumbu ya usalama ingekuwa ya kudanganya — ndiyo hasa
    kumbukumbu isiyotakiwa kuwa hivyo.
    """
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        parts = [p.strip() for p in forwarded.split(",") if p.strip()]
        if parts:
            return parts[-1]
    return request.META.get("REMOTE_ADDR")


class AuditLog(TimeStamped):
    """Kumbukumbu ya kila kitendo muhimu kwenye mfumo."""
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                             related_name="audit_logs")
    action = models.CharField(max_length=120)
    table_affected = models.CharField(max_length=80, blank=True)
    record_id = models.CharField(max_length=40, blank=True)
    detail = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Kumbukumbu ya Matendo")
        verbose_name_plural = _("Kumbukumbu za Matendo")

    def __str__(self):
        return f"{self.user} — {self.action}"

    @classmethod
    def record(cls, request, action, obj=None, detail=""):
        user = getattr(request, "user", None)
        return cls.objects.create(
            user=user if getattr(user, "is_authenticated", False) else None,
            action=action,
            table_affected=obj._meta.db_table if obj is not None else "",
            record_id=str(getattr(obj, "pk", "")) if obj is not None else "",
            detail=detail,
            ip_address=_client_ip(request),
            device=request.META.get("HTTP_USER_AGENT", "")[:200],
        )


class CodePurpose(models.TextChoices):
    """Sababu ya code. Code ya sababu moja haitumiki kwa nyingine."""
    PHONE = "phone", _("Kuthibitisha Namba ya Simu")
    LOGIN = "login", _("Kuingia kwenye Mfumo")


class VerificationCode(TimeStamped):
    """
    Code ya tarakimu sita inayotumwa kwa SMS.

    Code HAIHIFADHIWI wazi. Tunahifadhi alama yake (hash) tu, kama
    nenosiri. Mtu akipata nakala ya database, hawezi kusoma code za
    watu wanaosubiri kuingia.

    Kila code ina majaribio matano. Bila kikomo, tarakimu sita
    zingeweza kukisiwa kwa majaribio milioni moja — code fupi ni
    salama tu ikiwa na kikomo cha majaribio.
    """
    MAX_ATTEMPTS = 5
    TTL_MINUTES = 10
    #: Code ngapi kwa namba moja kwa saa. NextSMS yenyewe ina kikomo cha
    #: ujumbe 20 tofauti kwa saa (status 63); hii ni yetu, ya kuzuia mtu
    #: kutumia mfumo wetu kutuma SMS nyingi kwa namba ya mtu mwingine.
    MAX_PER_HOUR = 5

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE,
                             related_name="codes")
    #: Namba iliyopokea code, kwa muundo wa 255XXXXXXXXX. Kwa uthibitisho
    #: wa usajili mtumiaji bado hayupo — namba ndiyo kitambulisho pekee.
    phone = models.CharField(max_length=20, db_index=True)
    purpose = models.CharField(max_length=12, choices=CodePurpose.choices)
    code_hash = models.CharField(max_length=128)
    #: Kitambulisho cha rekodi husika (mfano namba ya ombi la uanachama).
    reference = models.CharField(max_length=80, blank=True, db_index=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["phone", "purpose"])]
        verbose_name = _("Code ya Uthibitisho")
        verbose_name_plural = _("Code za Uthibitisho")

    def __str__(self):
        return f"{self.phone} — {self.get_purpose_display()}"

    @classmethod
    def too_many(cls, phone):
        """Je, namba hii imeombewa code nyingi mno saa hii?"""
        since = timezone.now() - timezone.timedelta(hours=1)
        return cls.objects.filter(phone=phone, created_at__gte=since).count() >= cls.MAX_PER_HOUR

    @classmethod
    def issue(cls, phone, purpose, user=None, reference="", ip=None):
        """
        Tengeneza code mpya na urudishe (rekodi, code wazi).

        Code wazi inarudishwa MARA MOJA tu — ndiyo inayotumwa kwenye SMS.
        Baada ya hapo haipatikani tena popote.

        Code za zamani za namba hii na sababu hii zinabatilishwa. Bila
        hivyo, code tano zilizotumwa zote zingefanya kazi kwa pamoja.
        """
        from django.contrib.auth.hashers import make_password
        import secrets

        cls.objects.filter(phone=phone, purpose=purpose,
                           used_at__isnull=True).update(used_at=timezone.now())

        code = f"{secrets.randbelow(1000000):06d}"
        row = cls.objects.create(
            user=user, phone=phone, purpose=purpose, reference=reference,
            code_hash=make_password(code),
            expires_at=timezone.now() + timezone.timedelta(minutes=cls.TTL_MINUTES),
            ip_address=ip or None,
        )
        return row, code

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @classmethod
    def verify(cls, phone, purpose, code):
        """
        Thibitisha code. Hurudisha (rekodi, kosa).

        `kosa` ni `None` ikifaulu, vinginevyo ni ufunguo wa ujumbe:
        "none", "expired", "attempts", "wrong".
        """
        from django.contrib.auth.hashers import check_password

        row = (cls.objects.filter(phone=phone, purpose=purpose,
                                  used_at__isnull=True)
               .order_by("-created_at").first())
        if row is None:
            return None, "none"
        if row.is_expired:
            return row, "expired"
        if row.attempts >= cls.MAX_ATTEMPTS:
            return row, "attempts"

        # Hesabu ya majaribio inaongezwa KABLA ya kulinganisha. Ombi
        # likikatika katikati, jaribio bado limehesabiwa.
        row.attempts += 1
        row.save(update_fields=["attempts", "updated_at"])

        if not check_password(str(code).strip(), row.code_hash):
            return row, "wrong"

        row.used_at = timezone.now()
        row.save(update_fields=["used_at", "updated_at"])
        return row, None
