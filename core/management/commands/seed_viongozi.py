"""
Tengeneza viongozi wa mfano kwa ajili ya majaribio.

Inachagua maeneo halisi kutoka kwenye database yako — kata, wilaya, mkoa
na kanda zenye wanachama — kisha inaunda kiongozi kwa kila ngazi.

    python manage.py seed_viongozi
    python manage.py seed_viongozi --nenosiri kiongozi2026
    python manage.py seed_viongozi --futa        # ondoa wote

ONYO: hizi ni akaunti za MAJARIBIO zenye nenosiri linalojulikana. Zifute
kabla ya kuachia wanachama:  python manage.py seed_viongozi --futa
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Count

from geo.models import (District, LeaderLevel, LeaderPost, Leadership,
                        Region, Ward, Zone)
from members.models import Member

User = get_user_model()

#: Alama ya majaribio inayowekwa kwenye `Leadership.note`.
#:
#: Awali tulitumia kiambishi kwenye jina la mtumiaji (`jaribio.`), lakini
#: majina yalikuwa marefu kuandika. Sasa alama ipo kwenye wadhifa, si
#: kwenye jina — kwa hiyo `--futa` inatambua akaunti za majaribio bila
#: kugusa kiongozi halisi hata kama jina linafanana.
ALAMA = "seed_viongozi"


class Command(BaseCommand):
    help = "Tengeneza viongozi wa mfano kwa majaribio"

    def add_arguments(self, parser):
        parser.add_argument("--nenosiri", default="kiongozi2026")
        parser.add_argument("--futa", action="store_true",
                            help="Ondoa akaunti zote za majaribio")
        parser.add_argument("--panga", action="store_true",
                            help="Wapangie kata wanachama wasio na kata "
                                 "(kwa data ya mfano pekee)")

    def handle(self, *args, **opts):
        ok, warn = self.style.SUCCESS, self.style.WARNING

        if opts["futa"]:
            # Tunafuta MTUMIAJI pale nyadhifa zake ZOTE ni za majaribio.
            # Kiongozi halisi mwenye jina linalofanana habaki hatarini.
            wa_jaribio = []
            for u in User.objects.filter(leaderships__note=ALAMA).distinct():
                notes = set(u.leaderships.values_list("note", flat=True))
                if notes == {ALAMA}:
                    wa_jaribio.append(u.pk)

            # Toleo la awali lilitumia kiambishi `jaribio.` badala ya
            # alama. Tunazichukua nazo ili zisibaki zikiwa na nenosiri
            # linalojulikana.
            wa_zamani = list(User.objects
                             .filter(username__startswith="jaribio.")
                             .values_list("pk", flat=True))
            wa_jaribio = list(set(wa_jaribio) | set(wa_zamani))
            n = len(wa_jaribio)
            User.objects.filter(pk__in=wa_jaribio).delete()
            self.stdout.write(ok(f"Akaunti {n} za majaribio zimefutwa."))
            return

        pw = opts["nenosiri"]

        # Data ya mfano haiwapangii wanachama kata. Bila kata, kila
        # kiongozi anaona sifuri na majaribio hayaelezi chochote.
        if opts["panga"]:
            self._panga()

        # Chagua maeneo YENYE wanachama — kiongozi wa eneo tupu hana
        # cha kuonyesha, na majaribio yasingeeleza chochote.
        ward = (Ward.objects.annotate(n=Count("members"))
                .filter(n__gt=0).order_by("-n").first()
                or Ward.objects.first())
        if ward is None:
            self.stdout.write(warn("Hakuna kata kwenye database. Endesha `seed` kwanza."))
            return

        district = ward.district
        region = district.region
        zone = region.zone or Zone.objects.first()

        plan = [
            ("mwenyekiti_kata", LeaderLevel.WARD, LeaderPost.CHAIR, {"ward": ward}),
            ("katibu_kata", LeaderLevel.WARD, LeaderPost.SECRETARY, {"ward": ward}),
            ("mwenyekiti_wilaya", LeaderLevel.DISTRICT, LeaderPost.CHAIR, {"district": district}),
            ("katibu_wilaya", LeaderLevel.DISTRICT, LeaderPost.SECRETARY, {"district": district}),
            ("mwenyekiti_mkoa", LeaderLevel.REGION, LeaderPost.CHAIR, {"region": region}),
            ("katibu_mkoa", LeaderLevel.REGION, LeaderPost.SECRETARY, {"region": region}),
            ("mwenyekiti_taifa", LeaderLevel.NATIONAL, LeaderPost.CHAIR, {}),
            ("katibu_taifa", LeaderLevel.NATIONAL, LeaderPost.SECRETARY, {}),
        ]
        if zone:
            plan[6:6] = [
                ("mwenyekiti_kanda", LeaderLevel.ZONE, LeaderPost.CHAIR, {"zone": zone}),
                ("katibu_kanda", LeaderLevel.ZONE, LeaderPost.SECRETARY, {"zone": zone}),
            ]

        # Kata ya PILI, ya wilaya nyingine kabisa — ndiyo ya kuthibitisha
        # kwamba kiongozi wa Kata A hamwoni mwanachama wa Kata B.
        nyingine = (Ward.objects.annotate(n=Count("members"))
                    .filter(n__gt=0).exclude(district=district).order_by("-n").first())
        if nyingine:
            plan.append(("mwenyekiti_kata2", LeaderLevel.WARD, LeaderPost.CHAIR,
                         {"ward": nyingine}))

        if not Member.objects.filter(ward=ward).exists():
            self.stdout.write(warn(
                f"\nONYO: kata {ward} haina mwanachama hata mmoja, kwa hiyo "
                f"kiongozi wake ataona sifuri.\n"
                f"Kwa data ya mfano, ongeza --panga ili wanachama "
                f"wapangiwe kata kwanza."))

        rows = []
        for suffix, level, post, area in plan:
            username = suffix
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": post.label,
                          "last_name": suffix.split("_", 1)[-1].title(),
                          "role": "member"},
            )
            user.set_password(pw)
            user.is_active = True
            user.is_staff = False        # si afisa; ni kiongozi wa kanda/kata
            user.is_superuser = False
            user.save()

            Leadership.objects.filter(user=user).delete()
            Leadership.objects.create(user=user, level=level, post=post,
                                      note=ALAMA, **area)

            from geo.scope import scope_members
            rows.append((username, level.label, post.label,
                         Leadership.objects.filter(user=user).first().area_name,
                         scope_members(user).count()))

        jumla = Member.objects.count()
        self.stdout.write(ok(f"\nViongozi {len(rows)} wa majaribio wameundwa.\n"))
        self.stdout.write(f"Nenosiri kwa wote: {pw}")
        self.stdout.write(f"Wanachama wote kwenye mfumo: {jumla}\n")
        self.stdout.write(
            f"  {'Jina la mtumiaji':30} {'Ngazi':10} {'Wadhifa':12} "
            f"{'Eneo':26} {'Anaona'}")
        self.stdout.write("  " + "-" * 92)
        for u, lv, po, area, n in rows:
            self.stdout.write(f"  {u:30} {lv:10} {po:12} {area[:25]:26} {n:>4}/{jumla}")

        self.stdout.write(warn(
            "\nHizi ni akaunti za MAJARIBIO zenye nenosiri linalojulikana.\n"
            "Zifute kabla ya kuachia wanachama:  "
            "python manage.py seed_viongozi --futa"))

    def _panga(self):
        """
        Wapangie kata wanachama wasio nayo.

        Inagusa TU wale wasio na kata. Aliye nayo haguswi — data halisi
        haipaswi kubadilishwa na amri ya majaribio.
        """
        wards = list(Ward.objects.select_related("district__region")[:6])
        if not wards:
            return
        bila = list(Member.objects.filter(ward__isnull=True))
        for i, m in enumerate(bila):
            w = wards[i % len(wards)]
            m.ward = w
            m.district = w.district
            m.region = w.district.region
            m.save(update_fields=["ward", "district", "region"])
        if bila:
            self.stdout.write(self.style.WARNING(
                f"Wanachama {len(bila)} wamepangiwa kata "
                f"{len(wards)} (data ya mfano)."))
