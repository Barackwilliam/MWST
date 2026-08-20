"""Watumiaji, majukumu na kumbukumbu za matendo."""
from django.contrib.auth.models import AbstractUser
from django.db import models
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
            ip_address=(request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
                        or request.META.get("REMOTE_ADDR")),
            device=request.META.get("HTTP_USER_AGENT", "")[:200],
        )
