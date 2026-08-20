"""
Arifa za muda wa uanachama.

Uanachama hudumu miaka mitatu. Bila kukumbushwa, mtu hagundui kwamba muda
wake umeisha hadi anapohitaji huduma — na wakati huo tayari amechelewa.
Amri hii inamjulisha mapema, na tena muda ukiisha.

Endesha kila siku:
    python manage.py arifa_uanachama
Kuona tu bila kutuma:
    python manage.py arifa_uanachama --dry-run

Ni salama kuendeshwa mara nyingi kwa siku moja. Kila arifa ina `key` ya
kipekee inayojumuisha tarehe ya kuisha, kwa hiyo haiwezi kutumwa mara
mbili — wala haitazuiwa mtu akihuisha na kupata tarehe mpya.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from content.models import Notification
from members.models import Member, MemberStatus

#: Siku kabla ya kuisha ambazo mtu hukumbushwa. Tatu zinatosha:
#: moja ya mapema, moja ya kukusudia, na moja ya dharura.
MILESTONES = [90, 30, 7]


def _notice(member, days_left, expires_on):
    """Kichwa, maelezo na alama za arifa kwa hatua husika."""
    tarehe = expires_on.strftime("%d %b %Y")
    if days_left < 0:
        return {
            "title": "Uanachama wako umeisha muda",
            "body": (f"Uanachama wako uliisha tarehe {tarehe}. Huisha sasa "
                     f"upate kipindi kingine cha miaka {Member.TERM_YEARS} "
                     f"na kadi mpya."),
            "icon": "alert", "tint": "red",
        }
    if days_left <= 7:
        return {
            "title": f"Uanachama wako unaisha baada ya siku {days_left}",
            "body": (f"Kadi yako inaisha tarehe {tarehe}. Huisha kabla ya "
                     f"tarehe hiyo ili usikatishwe huduma."),
            "icon": "alert", "tint": "orange",
        }
    return {
        "title": f"Uanachama wako unaisha tarehe {tarehe}",
        "body": (f"Umebakiwa na siku {days_left}. Ukihuisha kabla muda "
                 f"haujaisha, siku zilizobaki haziponyeki — kipindi kipya "
                 f"kinaanzia tarehe ya kuisha uliyonayo."),
        "icon": "calendar", "tint": "gold",
    }


class Command(BaseCommand):
    help = "Wajulishe wanachama kuhusu muda wa uanachama wao"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true",
                            help="Onyesha tu, usitume chochote")

    def handle(self, *args, **opts):
        today = timezone.localdate()
        dry = opts["dry_run"]
        sent = skipped = 0

        # Waliositishwa hawapewi arifa za kuhuisha — hali yao ni uamuzi
        # wa afisa, si suala la malipo.
        members = (Member.objects
                   .filter(expires_on__isnull=False)
                   .exclude(status=MemberStatus.SUSPENDED)
                   .select_related("category"))

        for m in members:
            days = (m.expires_on - today).days

            if days < 0:
                stage = "imeisha"
            elif days in MILESTONES:
                stage = str(days)
            else:
                continue

            # `key` inajumuisha tarehe ya kuisha, kwa hiyo mtu akihuisha
            # na kupata tarehe mpya, arifa za kipindi kipya zitapita.
            key = f"muda:{m.pk}:{m.expires_on.isoformat()}:{stage}"
            data = _notice(m, days, m.expires_on)

            if dry:
                if not Notification.objects.filter(key=key).exists():
                    self.stdout.write(f"  {m.membership_no}  {data['title']}")
                    sent += 1
                else:
                    skipped += 1
                continue

            made = Notification.once(
                key, member=m, user_id=m.user_id,
                url="/lipa/?huisha=1", **data)
            if made:
                sent += 1
            else:
                skipped += 1

        note = " (dry-run, hakuna kilichotumwa)" if dry else ""
        self.stdout.write(self.style.SUCCESS(
            f"Arifa mpya: {sent}. Zilizokuwepo tayari: {skipped}.{note}"))
