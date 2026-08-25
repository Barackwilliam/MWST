"""
Django admin ya MUWESTA.

MATATIZO MAWILI YALIYOREKEBISHWA HAPA:

1. Django huruhusu YEYOTE mwenye `is_staff` kuingia kwenye `/admin`.
   Maafisa wote wa MUWESTA wana `is_staff` (ndiyo inayowapa paneli ya
   `/dashibodi/`), kwa hiyo wote 13 wangeweza kufungua Django admin na
   kubadilisha bei, hali za malipo, au majukumu ya watu — bila kizuizi
   chochote. Sasa ni `is_superuser` pekee.

2. Django admin haina kizuizi cha majaribio wala code ya SMS. Kuingia
   kunaandikwa kwenye `AuditLog` ili kuwe na kumbukumbu ya nani
   aliingia na lini.

Njia ya kuifikia inatoka `DJANGO_ADMIN_URL`. Ikiachwa tupu, admin
haipatikani kabisa.
"""
import logging

from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

log = logging.getLogger(__name__)


class MuwestaAdminSite(AdminSite):
    site_header = _("MUWESTA — Usimamizi wa Mfumo")
    site_title = _("MUWESTA Admin")
    index_title = _("Usimamizi wa kina wa mfumo")

    def has_permission(self, request):
        """
        Msimamizi mkuu pekee.

        Django ya kawaida inaangalia `is_staff`. Hapa tunadai
        `is_superuser` — sehemu hii inaruhusu kubadilisha data yoyote
        moja kwa moja bila ukaguzi wa mfumo, kwa hiyo si mahali pa
        kila afisa.
        """
        user = request.user
        return bool(user.is_active and user.is_superuser)

    def login(self, request, extra_context=None):
        """Andika jaribio lolote la kuingia kwenye kumbukumbu."""
        response = super().login(request, extra_context)
        if request.method == "POST":
            user = getattr(request, "user", None)
            who = request.POST.get("username", "")[:40]
            if user is not None and user.is_authenticated:
                self._audit(request, "django_admin_login", user.username)
            else:
                self._audit(request, "django_admin_login_failed", who)
        return response

    @staticmethod
    def _audit(request, action, detail):
        try:
            from accounts.models import AuditLog
            AuditLog.record(request, action, detail=detail)
        except Exception:
            # Kumbukumbu isiyoandikika isizuie mtu kuingia.
            log.exception("AuditLog ya %s haikuandikwa", action)


#: `config.apps.AdminConfig` inaifanya hii kuwa `admin.site` chaguo-msingi
#: (`default_site`). Kwa hiyo kila `@admin.register(...)` kwenye apps zetu
#: inasajili hapa yenyewe — hakuna faili ya kuhariri, na usajili wowote
#: mpya utakuja hapa bila mtu kukumbuka.
site = MuwestaAdminSite(name="admin")
