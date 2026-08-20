"""
Sajili IPN URL kwenye Pesapal na uonyeshe `ipn_id`.

Endesha MARA MOJA kwa kila mazingira (sandbox na live ni tofauti):

    python manage.py pesapal_ipn

Kisha weka namba unayopewa kwenye environment kama PESAPAL_IPN_ID.
"""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from finance.gateways import pesapal


class Command(BaseCommand):
    help = "Sajili IPN URL kwenye Pesapal na uonyeshe ipn_id"

    def add_arguments(self, parser):
        parser.add_argument("--url", help="IPN URL kamili (chaguo-msingi: SITE_URL + /pesapal/ipn/)")
        parser.add_argument("--list", action="store_true", help="Onyesha IPN zilizosajiliwa")

    def handle(self, *args, **opts):
        if not pesapal.is_configured():
            raise CommandError(
                "PESAPAL_CONSUMER_KEY / PESAPAL_CONSUMER_SECRET hazijawekwa "
                "kwenye environment.")

        self.stdout.write(f"Mazingira: {settings.PESAPAL_ENV}")

        if opts["list"]:
            for row in pesapal.list_ipns() or []:
                self.stdout.write(f"  {row.get('ipn_id')}  {row.get('url')}")
            return

        url = opts["url"] or f"{settings.SITE_URL}/pesapal/ipn/"
        if url.startswith("http://127.0.0.1") or url.startswith("http://localhost"):
            raise CommandError(
                "Pesapal haiwezi kufikia localhost. Weka SITE_URL ya tovuti "
                "iliyo mtandaoni, au tumia --url na anwani ya ngrok.")

        ipn_id = pesapal.register_ipn(url)
        self.stdout.write(self.style.SUCCESS(f"IPN imesajiliwa: {url}"))
        self.stdout.write(self.style.SUCCESS(f"PESAPAL_IPN_ID={ipn_id}"))
        self.stdout.write("Weka thamani hiyo kwenye environment ya Render.")
