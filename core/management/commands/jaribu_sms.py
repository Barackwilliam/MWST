"""
Jaribu muunganisho wa NextSMS.

Njia ya kutuma ndiyo iliyoandikwa wazi kwenye nyaraka zao; ndiyo maana
hii ndiyo ya kutegemewa kuliko kuangalia salio. Ikifanya kazi, token na
sender ni sahihi.

    python manage.py jaribu_sms                 # test mode (bure)
    python manage.py jaribu_sms 0769600102      # kwenda namba fulani
    python manage.py jaribu_sms 0769600102 --kweli   # SMS halisi

Kwa `NEXTSMS_TEST_MODE=True`, NextSMS inarudisha jibu la kweli bila
kutuma SMS wala kupunguza salio. Ndiyo ya kuanza nayo.
"""
from django.conf import settings
from django.core.management.base import BaseCommand

from core import sms


class Command(BaseCommand):
    help = "Jaribu muunganisho wa NextSMS na uonyeshe jibu lake"

    def add_arguments(self, parser):
        parser.add_argument("phone", nargs="?", default="255700000000",
                            help="Namba ya kujaribu (chaguo-msingi ni ya mfano)")
        parser.add_argument("--kweli", action="store_true",
                            help="Tuma SMS halisi (inapunguza salio)")

    def handle(self, *args, **opts):
        w, ok, err = self.style.WARNING, self.style.SUCCESS, self.style.ERROR

        self.stdout.write("Mipangilio:")
        self.stdout.write(f"  Token      : {'ipo' if settings.NEXTSMS_TOKEN else 'HAIPO'}")
        self.stdout.write(f"  Username   : {settings.NEXTSMS_USERNAME or '(haipo)'}")
        self.stdout.write(f"  Sender     : {settings.NEXTSMS_SENDER or 'HAIPO'}")
        self.stdout.write(f"  Test mode  : {settings.NEXTSMS_TEST_MODE}")

        if not sms.is_configured():
            self.stdout.write(err(
                "\nHaijawekwa kikamilifu. Inahitaji NEXTSMS_SENDER pamoja na "
                "NEXTSMS_TOKEN au (NEXTSMS_USERNAME na NEXTSMS_PASSWORD)."))
            return

        if opts["kweli"]:
            settings.NEXTSMS_TEST_MODE = False
            self.stdout.write(w("\nMODE: SMS HALISI — salio litapungua"))
        else:
            settings.NEXTSMS_TEST_MODE = True
            self.stdout.write("\nMODE: majaribio — hakuna SMS wala gharama")

        to = sms.msisdn(opts["phone"])
        self.stdout.write(f"Namba: {opts['phone']} -> {to}")
        self.stdout.write(f"Njia : {sms._endpoint()}\n")

        sent = sms.send(to, "MUWESTA: Huu ni ujumbe wa majaribio.",
                        reference="jaribio")
        if sent:
            self.stdout.write(ok("IMEFAULU. Token na sender ni sahihi."))
            if not opts["kweli"]:
                self.stdout.write(
                    "Sasa jaribu SMS halisi:  "
                    "python manage.py jaribu_sms <namba> --kweli")
        else:
            self.stdout.write(err(
                "IMESHINDWA. Kosa halisi limeandikwa hapo juu — soma mstari "
                "wa 'NextSMS ... -> HTTP' au '-> REJECTED/FAILED'."))
