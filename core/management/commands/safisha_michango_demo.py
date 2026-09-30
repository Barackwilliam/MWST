"""
Ondoa michango ya majaribio iliyotengenezwa na `seed`, kisha funga miradi
iliyotimiza lengo.

Kwa nini: `seed` ilikuwa ikiweka michango ya hadi TZS 50,000,000 kwenye
miradi bila kuangalia lengo, na kuithibitisha moja kwa moja. Tovuti ikaonyesha
"TZS 50,050,000 kati ya TZS 9,000,000" — fedha ambazo hazikuwahi kuingia.

Mchango wa seed unatambuliwa kwa alama zake zote kwa pamoja: hauna aina
(`purpose`), hauna kiasi alichoweka mtoaji (`entered_amount`), hauna namba ya
mtoa huduma, kumbukumbu, maelezo, jina/simu/barua pepe ya mchangiaji, afisa
aliyeurekodi wala ombi la uanachama — na kiasi chake ni kimoja kati ya vile
ambavyo `seed` huchagua. Mchango halisi kutoka fomu yoyote una angalau kimoja
kati ya hivyo.

Kwa chaguo-msingi INAONYESHA tu kitakachofutwa. Ongeza `--futa` kufuta kweli:

    python manage.py safisha_michango_demo            # angalia kwanza
    python manage.py safisha_michango_demo --futa     # futa

Leja haifutwi: kila ingizo la mchango unaofutwa linapata ingizo la kinyume,
na pointi zake zinarudishwa (angalia `reverse_posting`).
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from finance.models import Contribution, PaymentStatus, Project, reverse_posting

#: Viasi ambavyo `seed.contributions()` huchagua.
SEED_AMOUNTS = [Decimal(a) for a in (50000, 100000, 150000, 200000, 250000,
                                     500000, 750000, 1000000, 1500000,
                                     5000000, 25000000, 50000000)]


def demo_contributions(include_general=False):
    qs = Contribution.objects.filter(
        status=PaymentStatus.CONFIRMED,
        amount__in=SEED_AMOUNTS,
        purpose="", entered_amount__isnull=True,
        gateway="", gateway_ref="", reference="", note="", idempotency_key="",
        donor_name="", donor_phone="", donor_email="",
        recorded_by__isnull=True, application__isnull=True,
    )
    if not include_general:
        qs = qs.filter(project__isnull=False)
    return qs.select_related("project", "ledger_entry")


class Command(BaseCommand):
    help = "Ondoa michango ya majaribio (seed) na funga miradi iliyotimiza lengo."

    def add_arguments(self, parser):
        parser.add_argument("--futa", action="store_true",
                            help="Futa kweli. Bila hii inaonyesha tu.")
        parser.add_argument("--yote", action="store_true",
                            help="Jumuisha pia michango ya seed isiyo na mradi "
                                 "(mifuko ya jumla).")

    def handle(self, *args, **opts):
        rows = list(demo_contributions(include_general=opts["yote"]))
        total = sum((c.amount for c in rows), Decimal("0"))

        for c in rows:
            where = c.project.title if c.project else "—"
            self.stdout.write(f"  {c.receipt_no:<22} TZS {c.amount:>15,.0f}  {where}")
        self.stdout.write(f"Michango ya demo: {len(rows)} — jumla TZS {total:,.0f}")

        if not opts["futa"]:
            self.stdout.write(self.style.WARNING(
                "Hakuna kilichofutwa. Endesha tena na --futa kuthibitisha."))
            return

        with transaction.atomic():
            for c in rows:
                reverse_posting(c, reason="Mchango wa majaribio umeondolewa")
                c.delete()
            closed = Project.close_all_full()

        self.stdout.write(self.style.SUCCESS(f"Imefutwa: michango {len(rows)}."))
        for p in closed:
            self.stdout.write(f"  Mradi umefungwa (lengo limetimia): {p.title}")
