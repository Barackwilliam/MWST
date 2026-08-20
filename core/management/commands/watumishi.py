"""
Unda akaunti za watumishi (msimamizi, maafisa, waratibu).

Kuunda wote kwa nenosiri lililotengenezwa lenye nguvu:
    python manage.py watumishi

Kuweka nenosiri moja unalolijua (kwa mfumo wa majaribio tu):
    python manage.py watumishi --password NenosiriLangu123

Kuunda mratibu wa kanda fulani:
    python manage.py watumishi --mratibu kaskazini

TAHADHARI: nenosiri linaonyeshwa MARA MOJA tu, hapa kwenye terminal.
Halihifadhiwi popote. Linakili mara moja, mpe mhusika kwa njia salama,
kisha umwambie alibadilishe akiingia mara ya kwanza.
"""
import secrets

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Role
from geo.models import Zone

User = get_user_model()

#: Herufi zenye utata (0/O, 1/l/I) zimeondolewa ili nenosiri liweze
#: kusomwa kwa simu au kunakiliwa kwa mkono bila makosa.
ALPHABET = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789"

STAFF = [
    ("admin",     Role.SUPER_ADMIN,   "Msimamizi",  "Mkuu",       True),
    ("usimamizi", Role.MANAGEMENT,    "Afisa",      "Usimamizi",  False),
    ("usajili",   Role.REGISTRATION,  "Afisa",      "Usajili",    False),
    ("malipo",    Role.FINANCE,       "Afisa",      "Malipo",     False),
    ("michango",  Role.CONTRIBUTIONS, "Afisa",      "Michango",   False),
    ("ustawi",    Role.WELFARE,       "Afisa",      "Ustawi",     False),
    ("wadau",     Role.OUTREACH,      "Afisa",      "Wadau",      False),
]


def make_password(length=14):
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


class Command(BaseCommand):
    help = "Unda akaunti za watumishi wa MUWESTA"

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            help="Nenosiri moja kwa wote. Bila hii, kila mmoja anapata "
                 "nenosiri lake lenye nguvu (inashauriwa).")
        parser.add_argument(
            "--mratibu", metavar="CODE", action="append", default=[],
            help="Unda mratibu wa kanda hii (kwa code yake). Inaweza "
                 "kurudiwa kwa kanda nyingi.")
        parser.add_argument(
            "--reset", action="store_true",
            help="Badilisha nenosiri za akaunti zilizopo pia. Bila hii, "
                 "zilizopo zinaachwa kama zilivyo.")

    def handle(self, *args, **opts):
        rows = []

        for username, role, first, last, is_super in STAFF:
            rows.append(self._upsert(username, role, first, last,
                                     is_super=is_super, opts=opts))

        for code in opts["mratibu"]:
            zone = Zone.objects.filter(code__iexact=code).first()
            if zone is None:
                self.stderr.write(self.style.ERROR(
                    f"Kanda '{code}' haipo. Kanda zilizopo: "
                    f"{', '.join(Zone.objects.values_list('code', flat=True)) or 'hakuna'}"))
                continue
            row = self._upsert(f"mratibu_{zone.code}", Role.COORDINATOR,
                               "Mratibu", zone.name, opts=opts)
            # Uratibu unaunganishwa hapa; bila hii mratibu huingia lakini
            # haoni mkoa hata mmoja.
            zone.coordinator = row["user"]
            zone.save(update_fields=["coordinator"])
            row["note"] = f"kanda: {zone.name}"
            rows.append(row)

        self._report(rows)

    # ------------------------------------------------------------------
    @transaction.atomic
    def _upsert(self, username, role, first, last, is_super=False, opts=None):
        opts = opts or {}
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"first_name": first, "last_name": last, "role": role})

        password = None
        if created or opts.get("reset"):
            password = opts.get("password") or make_password()
            user.set_password(password)

        user.role = role
        user.is_active = True
        user.is_staff = True
        user.is_superuser = is_super
        user.save()

        return {"user": user, "username": username, "role": role,
                "password": password, "created": created, "note": ""}

    def _report(self, rows):
        made = [r for r in rows if r["created"]]
        reset = [r for r in rows if r["password"] and not r["created"]]
        kept = [r for r in rows if not r["password"]]

        self.stdout.write("")
        self.stdout.write(f"{'MTUMIAJI':<20}{'JUKUMU':<18}{'NENOSIRI':<18}MAELEZO")
        self.stdout.write("-" * 74)
        for r in rows:
            pw = r["password"] or "(halijabadilishwa)"
            state = "mpya" if r["created"] else ("limebadilishwa" if r["password"] else "lipo")
            note = f"{state}{' — ' + r['note'] if r['note'] else ''}"
            self.stdout.write(f"{r['username']:<20}{r['role']:<18}{pw:<18}{note}")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Wapya: {len(made)} | Nenosiri zilizobadilishwa: {len(reset)} | "
            f"Zilizoachwa: {len(kept)}"))

        if made or reset:
            self.stdout.write(self.style.WARNING(
                "\nNenosiri hizi hazitaonyeshwa tena. Zinakili sasa, zipeleke "
                "kwa wahusika kwa njia salama, na uwaambie wazibadilishe "
                "wakiingia mara ya kwanza."))
        if kept:
            self.stdout.write(
                "Kubadilisha nenosiri za zilizopo, ongeza:  --reset")
        if not Zone.objects.exists():
            self.stdout.write(self.style.WARNING(
                "\nHakuna kanda kwenye database, kwa hiyo hakuna mratibu "
                "aliyeundwa. Unda kanda kwanza, kisha endesha:\n"
                "    python manage.py watumishi --mratibu <code>"))
