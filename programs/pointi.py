"""
Weka kanuni za pointi za MUWESTA.

    python manage.py pointi

Inaunda kanuni za ushiriki (kuhudhuria, kujitolea, kuongoza...) kutoka
`programs/points.py`. Kanuni zilizopo hazibadilishwi isipokuwa kwa
`--reset` — ofisi ikirekebisha kiwango kupitia admin, hatutaki amri
hii ikirudishe nyuma.

Pointi za MICHANGO hazina kanuni hapa. Zinahesabiwa moja kwa moja
kutoka kiasi cha fedha (TSh 1,000 = pointi 1) mara Pesapal
anapothibitisha malipo — hakuna afisa anayehusika.
"""
from django.core.management.base import BaseCommand

from programs import points as pts
from programs.models import PointRule


class Command(BaseCommand):
    help = "Weka kanuni za pointi za ushiriki"

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true",
                            help="Rudisha viwango vya awali kwa kanuni zilizopo.")

    def handle(self, *args, **opts):
        made = updated = kept = 0

        for order, (code, sw, en, value) in enumerate(pts.PARTICIPATION_ACTIVITIES, 1):
            rule, created = PointRule.objects.get_or_create(
                code=code,
                defaults={"activity": sw, "activity_en": en, "points": value,
                          "kind": pts.PointKind.PARTICIPATION, "order": order})
            if created:
                made += 1
            elif opts["reset"]:
                rule.activity, rule.activity_en = sw, en
                rule.points, rule.order = value, order
                rule.kind = pts.PointKind.PARTICIPATION
                rule.save()
                updated += 1
            else:
                kept += 1

        # Kanuni ya zamani ya michango haitumiki tena — pointi za fedha
        # sasa zinahesabiwa moja kwa moja, si kwa kanuni.
        #
        # Nyingine hapa zinarudia kanuni mpya kwa maneno tofauti
        # (`referral` na `mwaliko` zote ni kuleta mwanachama; `training`,
        # `volunteer` na `agm` zinarudia `semina`, `kujitolea`, `kikao`).
        # Zikibaki hai, afisa angeweza kutoa pointi mara mbili kwa
        # jambo moja bila kukusudia. Zinazimwa, hazifutwi — miamala
        # iliyokwisha tolewa nazo inabaki kwenye leja.
        LEGACY = ["donation", "referral", "training", "volunteer", "agm",
                  "payment_on_time", "full_year"]
        retired = PointRule.objects.filter(code__in=LEGACY, is_active=True).count()
        PointRule.objects.filter(code__in=LEGACY).update(is_active=False)

        self.stdout.write("")
        self.stdout.write(f"{'KANUNI':<34}{'POINTI':<10}HALI")
        self.stdout.write("-" * 56)
        for rule in PointRule.objects.filter(kind=pts.PointKind.PARTICIPATION,
                                             is_active=True):
            flag = "idhini ya pili" if rule.needs_second_approval else ""
            self.stdout.write(f"{rule.activity:<34}{rule.points:<10}{flag}")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Mpya: {made} | Zilizosasishwa: {updated} | Zilizoachwa: {kept} | "
            f"Zilizozimwa (zilikuwa zinarudia): {retired}"))
        self.stdout.write("")
        self.stdout.write("Viwango vya MUWESTA:")
        for row in pts.TIERS:
            self.stdout.write(f"   {row['name']:<22}kuanzia pointi {row['min']:,}")
        self.stdout.write("")
        self.stdout.write(
            f"Michango: TSh {pts.SHILLINGS_PER_POINT:,.0f} = pointi 1 "
            f"(kikomo {pts.MONEY_CAP:,} kwa miaka {pts.PERIOD_YEARS})")
        self.stdout.write(
            f"Ada ya uanachama: pointi {pts.MEMBERSHIP_FEE_POINTS}")
        if kept:
            self.stdout.write("\nKubadilisha viwango vya kanuni zilizopo:  --reset")
