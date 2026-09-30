"""
Sajili viongozi wa Taifa kutoka faili la CSV.

Faili lina safu tatu — jina, simu, cheo — mfano:

    jina,simu,cheo
    Ramadhani Juma,0783 453 224,Mwenyekiti
    Mustafa Kassim Kipingu,0782257911,Makamu

Kila kiongozi anapata:
  * jina la kuingia = cheo chake (mwenyekiti, makamu, katibu_msaidizi...;
    Wajumbe ni mjumbe1, mjumbe2, ...),
  * nenosiri la muda linaloonyeshwa HAPA TU — mpe mhusika mwenyewe,
  * namba yake ya simu kwenye akaunti, ili code ya kuingia (OTP) iende
    kwenye simu yake kila anapoingia kwenye kifaa kipya.

    python manage.py sajili_viongozi viongozi.csv
    python manage.py sajili_viongozi viongozi.csv --tuma-sms
    python manage.py sajili_viongozi viongozi.csv --nenosiri-mpya

Faili la CSV lina namba za simu za watu halisi — lisiwekwe kwenye git.

Ni salama kuendesha mara nyingi: aliyekwisha sajiliwa anasasishwa jina,
simu na cheo, lakini nenosiri lake halibadilishwi isipokuwa
`--nenosiri-mpya`. `--tuma-sms` inatuma jina la kuingia na kiungo tu —
NENOSIRI HALITUMWI kwa SMS (angalia `sms.send_membership_ready`).
"""
import csv
import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import Role
from geo.models import LeaderLevel, LeaderPost, Leadership

User = get_user_model()

#: Alama kwenye `Leadership.note` — inatenganisha nyadhifa za amri hii na
#: zile zilizowekwa kwa mkono au na `seed_viongozi`.
ALAMA = "sajili_viongozi"

#: Cheo kama kilivyoandikwa -> (wadhifa, jina la kuingia).
VYEO = {
    "mwenyekiti": (LeaderPost.CHAIR, "mwenyekiti"),
    "makamu": (LeaderPost.VICE_CHAIR, "makamu"),
    "makamu mwenyekiti": (LeaderPost.VICE_CHAIR, "makamu"),
    "katibu": (LeaderPost.SECRETARY, "katibu"),
    "katibu msaidizi": (LeaderPost.ASST_SECRETARY, "katibu_msaidizi"),
    "mweka hazina": (LeaderPost.TREASURER, "mweka_hazina"),
    "mweka hazina msaidizi": (LeaderPost.ASST_TREASURER, "mweka_hazina_msaidizi"),
    "mjumbe": (LeaderPost.COMMITTEE, "mjumbe"),
}

#: Herufi zenye utata (0/O, 1/l/I) zimeondolewa ili nenosiri lisomwe kwa
#: simu bila makosa — sawa na `Member.create_login`.
ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"


def local_phone(raw):
    """+255 769 545 535 / 0769545535 / 769545535 -> 0769545535."""
    digits = "".join(ch for ch in str(raw) if ch.isdigit())
    if digits.startswith("255"):
        digits = digits[3:]
    if len(digits) == 9:
        digits = "0" + digits
    return digits


def read_rows(path):
    try:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
    except OSError as e:
        raise CommandError(f"Faili halisomeki: {e}")
    if not rows or not {"jina", "simu", "cheo"} <= set(rows[0]):
        raise CommandError("CSV lazima iwe na vichwa: jina,simu,cheo")

    out, wajumbe, seen = [], 0, set()
    for n, r in enumerate(rows, start=2):
        name = " ".join((r["jina"] or "").split())
        phone = local_phone(r["simu"] or "")
        cheo = " ".join((r["cheo"] or "").lower().split())
        if cheo not in VYEO:
            raise CommandError(f"Mstari {n}: cheo '{r['cheo']}' hakijulikani. "
                               f"Tumia: {', '.join(sorted(VYEO))}")
        if not name or len(phone) != 10 or not phone.startswith("0"):
            raise CommandError(f"Mstari {n}: jina au namba ya simu si sahihi "
                               f"({r['jina']!r}, {r['simu']!r}).")
        post, username = VYEO[cheo]
        if post == LeaderPost.COMMITTEE:
            wajumbe += 1
            username = f"mjumbe{wajumbe}"
        elif username in seen:
            raise CommandError(f"Mstari {n}: cheo '{r['cheo']}' kimerudiwa.")
        seen.add(username)
        out.append({"name": name, "phone": phone, "post": post, "username": username})
    return out


class Command(BaseCommand):
    help = "Sajili viongozi wa Taifa (cheo = jina la kuingia) kutoka CSV."

    def add_arguments(self, parser):
        parser.add_argument("faili", help="CSV yenye safu: jina,simu,cheo")
        parser.add_argument("--nenosiri-mpya", action="store_true",
                            help="Weka nenosiri jipya hata kwa waliokwisha sajiliwa")
        parser.add_argument("--tuma-sms", action="store_true",
                            help="Mtumie kila mmoja jina lake la kuingia kwa SMS "
                                 "(bila nenosiri)")

    def handle(self, *args, **opts):
        rows = read_rows(opts["faili"])

        # Jina la kuingia likiwa tayari ni la mtu mwingine (asiyesajiliwa na
        # amri hii), hatumgusi — tungembadilishia mtu nenosiri kimya kimya.
        for r in rows:
            u = User.objects.filter(username=r["username"]).first()
            if u and not u.leaderships.filter(note=ALAMA).exists():
                raise CommandError(
                    f"Jina '{r['username']}' tayari linatumiwa na akaunti nyingine. "
                    f"Ibadilishe au ifute kwanza.")

        done = []
        with transaction.atomic():
            for r in rows:
                first, _, last = r["name"].partition(" ")
                user, created = User.objects.get_or_create(
                    username=r["username"], defaults={"role": Role.MEMBER})
                user.first_name, user.last_name = first, last
                user.phone = r["phone"]
                user.is_active = True
                user.is_staff = user.is_superuser = False
                password = None
                if created or opts["nenosiri_mpya"]:
                    password = "".join(secrets.choice(ALPHABET) for _ in range(10))
                    user.set_password(password)
                user.save()

                Leadership.objects.filter(user=user, note=ALAMA).delete()
                Leadership.objects.create(user=user, level=LeaderLevel.NATIONAL,
                                          post=r["post"], note=ALAMA)
                done.append((r, password, created))

        self.stdout.write(self.style.SUCCESS(f"\nViongozi {len(done)} wamesajiliwa.\n"))
        self.stdout.write(f"  {'Jina la kuingia':24} {'Nenosiri':12} {'Simu':12} "
                          f"{'Cheo':22} Jina")
        self.stdout.write("  " + "-" * 100)
        for r, pw, created in done:
            label = LeaderPost(r["post"]).label
            self.stdout.write(f"  {r['username']:24} {pw or '(halijabadilika)':12} "
                              f"{r['phone']:12} {str(label):22} {r['name']}")

        login = settings.SITE_URL.rstrip("/") + "/ingia/viongozi/"
        self.stdout.write(f"\nKuingia: {login}")
        self.stdout.write(self.style.WARNING(
            "Nenosiri linaonyeshwa MARA HII TU. Mpe kila mmoja lake mwenyewe "
            "(si kwenye kikundi). Akiingia, code ya uthibitisho itakuja kwa "
            "SMS kwenye namba yake."))

        if opts["tuma_sms"]:
            from core import sms
            sent = 0
            for r, _pw, _c in done:
                text = (f"MUWESTA: Umesajiliwa kama {LeaderPost(r['post']).label}. "
                        f"Jina la kuingia: {r['username']}. Utapewa nenosiri na "
                        f"msimamizi. Ingia: {login}")
                sent += bool(sms.send(r["phone"], text, reference="kiongozi-amesajiliwa"))
            self.stdout.write(f"SMS zilizotumwa: {sent}/{len(done)}")
