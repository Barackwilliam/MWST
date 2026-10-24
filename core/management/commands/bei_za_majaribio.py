"""
Bei za majaribio: punguza bei za vifurushi kwa muda, kisha zirudishe.

Kwa siku za majaribio, kila kifurushi kinagawanywa kwa 1000 (sifuri tatu
zinaondolewa): Bronze TSh 10,000 inakuwa TSh 10. Bei halisi zinahifadhiwa
kwenye kila kifurushi (`Category.price_backup`) KABLA ya kubadilishwa, kwa
hiyo `--zima` inazirudisha kama zilivyokuwa — si kwa kuzidisha, ambako
kungekosea kama mtu alibadilisha bei katikati.

    python manage.py bei_za_majaribio               # angalia hali ya sasa
    python manage.py bei_za_majaribio --washa       # gawanya kwa 1000
    python manage.py bei_za_majaribio --zima        # rudisha bei halisi

Ni salama kuendesha mara nyingi: `--washa` mara ya pili haigawanyi tena,
na `--zima` bila bei zilizohifadhiwa haibadilishi chochote.

Wakati bei za majaribio zimewashwa, tovuti inaonyesha bango juu ya kila
ukurasa wa umma. Malipo yanayofanyika wakati huo ni ya KWELI: uanachama
unaolipiwa kwa bei ya majaribio ni uanachama kamili wa miaka 3.
"""
from decimal import ROUND_HALF_UP, Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from members.models import Category

FIELDS = ("registration_fee", "monthly_fee", "annual_fee")


def _money(value):
    return f"TSh {Decimal(value):,.0f}"


class Command(BaseCommand):
    help = "Washa au zima bei za majaribio za vifurushi (gawanya kwa 1000)."

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--washa", action="store_true",
                           help="Hifadhi bei halisi, kisha zigawanye")
        group.add_argument("--zima", action="store_true",
                           help="Rudisha bei halisi zilizohifadhiwa")
        parser.add_argument("--gawanya", type=int, default=1000,
                            help="Kigawanyo (chaguo-msingi: 1000 = sifuri tatu)")

    def handle(self, *args, **opts):
        if opts["washa"]:
            self._washa(opts["gawanya"])
        elif opts["zima"]:
            self._zima()
        self._hali()

    @transaction.atomic
    def _washa(self, divisor):
        if divisor < 2:
            self.stderr.write("--gawanya lazima iwe 2 au zaidi.")
            return
        n = 0
        for cat in Category.objects.select_for_update():
            if cat.price_backup:
                continue                       # tayari iko kwenye majaribio
            cat.price_backup = {f: str(getattr(cat, f)) for f in FIELDS}
            for f in FIELDS:
                real = Decimal(getattr(cat, f) or 0)
                cheap = (real / divisor).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
                # Bei halisi isiyo sifuri isiwe sifuri — ingekuwa bure.
                setattr(cat, f, max(cheap, Decimal(1)) if real else Decimal(0))
            cat.save(update_fields=[*FIELDS, "price_backup"])
            n += 1
        self.stdout.write(self.style.WARNING(
            f"Bei za majaribio zimewashwa kwa vifurushi {n} (÷{divisor})."))

    @transaction.atomic
    def _zima(self):
        n = 0
        for cat in Category.objects.select_for_update().exclude(price_backup=None):
            for f in FIELDS:
                if f in cat.price_backup:
                    setattr(cat, f, Decimal(cat.price_backup[f]))
            cat.price_backup = None
            cat.save(update_fields=[*FIELDS, "price_backup"])
            n += 1
        self.stdout.write(self.style.SUCCESS(f"Bei halisi zimerudishwa kwa vifurushi {n}."))

    def _hali(self):
        cats = list(Category.objects.order_by("order", "pk"))
        test = [c for c in cats if c.price_backup]
        state = "MAJARIBIO" if test else "HALISI"
        self.stdout.write(f"\nHali: bei {state}\n")
        self.stdout.write(f"  {'Kifurushi':12} {'Usajili':>14} {'Mwezi':>14}   Bei halisi (usajili / mwezi)")
        for c in cats:
            real = (f"{_money(c.price_backup['registration_fee'])} / "
                    f"{_money(c.price_backup['monthly_fee'])}") if c.price_backup else "—"
            self.stdout.write(f"  {c.name:12} {_money(c.registration_fee):>14} "
                              f"{_money(c.monthly_fee):>14}   {real}")
