"""
Pandisha matatizo yaliyokaa muda mrefu bila kushughulikiwa.

Kiongozi asiyeshughulikia tatizo asiliweke kando milele. Baada ya siku
zilizowekwa, linapanda lenyewe ngazi moja juu — na hatua hiyo
inahifadhiwa kama nyingine zote, ikionyesha kwamba ilipanda kwa muda,
si kwa uamuzi wa mtu.

Endesha kila siku:
    python manage.py pandisha_matatizo
    python manage.py pandisha_matatizo --siku 5
    python manage.py pandisha_matatizo --onyesha     # ona tu, usipandishe
"""
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from geo.models import LeaderLevel
from programs.models import Case, CaseStatus


class Command(BaseCommand):
    help = "Pandisha matatizo yaliyokaa bila kushughulikiwa"

    def add_arguments(self, parser):
        parser.add_argument("--siku", type=int,
                            default=getattr(settings, "CASE_ESCALATE_DAYS", 7))
        parser.add_argument("--onyesha", action="store_true")

    def handle(self, *args, **opts):
        ok, warn = self.style.SUCCESS, self.style.WARNING
        siku = opts["siku"]
        mpaka = timezone.now() - timezone.timedelta(days=siku)

        # Yaliyo wazi tu, na yasiyo ngazi ya Taifa — hakuna pa kupandisha
        # kutoka Taifa, na kupandisha lililotatuliwa hakuna maana.
        qs = (Case.objects
              .filter(status__in=[CaseStatus.OPEN, CaseStatus.IN_PROGRESS,
                                  CaseStatus.ESCALATED],
                      level_since__lt=mpaka)
              .exclude(level=LeaderLevel.NATIONAL)
              .select_related("member"))

        if opts["onyesha"]:
            self.stdout.write(f"Yatakayopanda (baada ya siku {siku}): {qs.count()}")
            for c in qs[:20]:
                self.stdout.write(
                    f"  {c.reference}  {c.get_level_display():8} "
                    f"siku {c.days_at_level:>3}  {c.subject[:40]}")
            return

        n = 0
        for case in qs:
            zamani = case.get_level_display()
            nxt = case.escalate(
                automatic=True,
                note=f"Limepanda lenyewe baada ya siku {case.days_at_level} "
                     f"bila kushughulikiwa {zamani.lower()}.")
            if nxt:
                n += 1
                self.stdout.write(
                    f"  {case.reference}: {zamani} -> {case.get_level_display()}")

        self.stdout.write((ok if n else warn)(
            f"Matatizo {n} yamepandishwa (kikomo: siku {siku})."))
