"""
Safisha namba za simu zilizohifadhiwa kwa miundo tofauti.

Data za zamani zina "0721 508 699" wakati mfumo sasa unatumia
"0721508699". Bila usafi huu, kutafuta na kulinganisha kunashindwa.

    python manage.py safisha_simu
    python manage.py safisha_simu --dry-run
"""
from django.core.management.base import BaseCommand

from core.mixins import normalize_phone
from members.models import Application, Beneficiary, FamilyMember, Member


class Command(BaseCommand):
    help = "Weka namba zote za simu kwenye muundo mmoja"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **opts):
        total = 0
        for model in (Member, Application, FamilyMember, Beneficiary):
            changed = []
            for obj in model.objects.exclude(phone=""):
                clean = normalize_phone(obj.phone)
                if clean != obj.phone:
                    obj.phone = clean
                    changed.append(obj)
            if changed and not opts["dry_run"]:
                model.objects.bulk_update(changed, ["phone"], batch_size=500)
            total += len(changed)
            self.stdout.write(f"  {model.__name__:<16} {len(changed)}")

        verb = "zingebadilishwa" if opts["dry_run"] else "zimebadilishwa"
        self.stdout.write(self.style.SUCCESS(f"Namba {total} {verb}."))
