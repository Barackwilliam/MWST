"""
Badilisha hali ya wanachama ambao muda wao umeisha.

Endesha kila siku (cron au GitHub Actions):
    python manage.py expire_members
Kuona tu bila kubadilisha:
    python manage.py expire_members --dry-run
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from members.models import Member, MemberStatus


class Command(BaseCommand):
    help = "Weka hali ya 'expired' kwa wanachama ambao muda wao umeisha"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true",
                            help="Onyesha tu, usibadilishe chochote")

    def handle(self, *args, **opts):
        today = timezone.localdate()
        qs = (Member.objects
              .filter(expires_on__lt=today)
              .exclude(status=MemberStatus.EXPIRED))
        count = qs.count()

        if opts["dry_run"]:
            for m in qs[:20]:
                self.stdout.write(f"  {m.membership_no}  {m.full_name}  ({m.expires_on})")
            self.stdout.write(self.style.WARNING(
                f"Wangebadilishwa: {count} (dry-run, hakuna kilichobadilika)"))
            return

        qs.update(status=MemberStatus.EXPIRED)
        self.stdout.write(self.style.SUCCESS(
            f"Wanachama {count} wamewekwa 'expired'."))
