"""
Tuma SMS zilizoko kwenye foleni.

SMS inayoshindwa (salio limeisha, mtandao umekatika, NextSMS ina
hitilafu) huhifadhiwa badala ya kupotea. Amri hii inajaribu tena.

Endesha kila saa, au pamoja na amri nyingine za kila siku:
    python manage.py tuma_sms_foleni
    python manage.py tuma_sms_foleni --idadi 100
    python manage.py tuma_sms_foleni --onyesha      # ona tu, usitume

Salio likiisha, amri inasimama mara moja badala ya kupoteza majaribio
ya kila ujumbe mmoja mmoja — sababu ni ile ile kwa wote.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from content.models import SmsOutbox
from core import sms


class Command(BaseCommand):
    help = "Tuma tena SMS zilizoshindwa"

    def add_arguments(self, parser):
        parser.add_argument("--idadi", type=int, default=200,
                            help="Kiwango cha juu cha kutuma kwa mara moja")
        parser.add_argument("--onyesha", action="store_true",
                            help="Onyesha foleni bila kutuma")

    def handle(self, *args, **opts):
        ok, err, warn = self.style.SUCCESS, self.style.ERROR, self.style.WARNING

        queued = SmsOutbox.objects.filter(status="queued")[:opts["idadi"]]
        total = SmsOutbox.objects.filter(status="queued").count()

        if not total:
            self.stdout.write(ok("Foleni ni tupu."))
            return

        if opts["onyesha"]:
            self.stdout.write(f"Foleni ina ujumbe {total}:")
            for m in queued[:20]:
                self.stdout.write(
                    f"  {m.phone}  majaribio {m.attempts}  "
                    f"[{m.reference or '-'}]  {m.last_error}")
            return

        if not sms.is_configured():
            self.stdout.write(err(
                f"NextSMS haijawekwa. Ujumbe {total} unasubiri."))
            return

        sent = failed = 0
        for m in queued:
            # `queue=False` — bila hiyo, ujumbe uliokataliwa ungejiongeza
            # kwenye foleni tena na foleni isingeisha kamwe.
            if sms.send(m.phone, m.text, m.reference, queue=False):
                m.status = "sent"
                m.sent_at = timezone.now()
                m.attempts += 1
                m.save(update_fields=["status", "sent_at", "attempts", "updated_at"])
                sent += 1
                continue

            m.attempts += 1
            if m.attempts >= SmsOutbox.MAX_ATTEMPTS:
                m.status = "failed"
                m.last_error = "imekata tamaa baada ya majaribio " \
                               f"{SmsOutbox.MAX_ATTEMPTS}"
            m.save(update_fields=["status", "attempts", "last_error", "updated_at"])
            failed += 1

            # Ujumbe wa kwanza ukishindwa, mara nyingi sababu ni ile ile
            # kwa wote — salio au mtandao. Kuendelea ni kupoteza muda.
            if failed >= 3 and sent == 0:
                self.stdout.write(warn(
                    "Ujumbe wa kwanza mitatu umeshindwa — nimesimama. "
                    "Angalia salio na log."))
                break

        left = SmsOutbox.objects.filter(status="queued").count()
        line = f"Zimetumwa: {sent}. Zimeshindwa: {failed}. Zilizobaki: {left}."
        self.stdout.write(ok(line) if sent else warn(line))
