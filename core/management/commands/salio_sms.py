"""
Angalia salio la SMS.

SMS zikiisha, code za kuingia zinaacha kufanya kazi. Mfumo unaendelea
(mtu anaruhusiwa kuingia bila code — angalia `_start_login_code`), lakini
usalama unashuka kimya kimya. Ni tatizo linalotakiwa kugundulika mapema.

Endesha kila siku pamoja na amri nyingine:
    python manage.py salio_sms
    python manage.py salio_sms --onyo 200
"""
from django.core.management.base import BaseCommand

from core import sms


class Command(BaseCommand):
    help = "Angalia salio la SMS la NextSMS"

    def add_arguments(self, parser):
        parser.add_argument("--onyo", type=int, default=150,
                            help="Salio la chini linalotoa onyo (chaguo-msingi 150)")

    def handle(self, *args, **opts):
        if not sms.is_configured():
            self.stdout.write(self.style.WARNING(
                "NextSMS haijawekwa. Angalia NEXTSMS_TOKEN na NEXTSMS_SENDER."))
            return

        left = sms.balance()
        if left is None:
            self.stdout.write(self.style.ERROR(
                "Salio halikupatikana. Angalia log kwa maelezo."))
            return

        floor = opts["onyo"]
        line = f"Salio: {left:,} SMS"
        if left <= 0:
            self.stdout.write(self.style.ERROR(
                line + " — ZIMEISHA. Code za kuingia hazitumwi."))
        elif left <= floor:
            self.stdout.write(self.style.WARNING(
                line + f" — chini ya {floor:,}. Ongeza salio."))
        else:
            self.stdout.write(self.style.SUCCESS(line))
