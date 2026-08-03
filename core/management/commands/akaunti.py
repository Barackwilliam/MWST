"""
Kagua na rekebisha matatizo ya kuingia kwenye mfumo.

Kuona hali ya watumiaji wote:
    python manage.py akaunti

Kurekebisha nenosiri la mtumiaji mmoja:
    python manage.py akaunti --reset mwanachama

Kurekebisha nenosiri za watumiaji wote wa mfano:
    python manage.py akaunti --reset-all
"""
from django.contrib.auth import authenticate, get_user_model
from django.core.management.base import BaseCommand

from accounts.models import Role
from members.models import Member

User = get_user_model()

DEMO = {
    "admin": Role.SUPER_ADMIN,
    "usimamizi": Role.MANAGEMENT,
    "usajili": Role.REGISTRATION,
    "malipo": Role.FINANCE,
    "michango": Role.CONTRIBUTIONS,
    "ustawi": Role.WELFARE,
    "wadau": Role.OUTREACH,
    "mratibu": Role.COORDINATOR,
    "mwanachama": Role.MEMBER,
}
DEFAULT_PASSWORD = "mwst2026"


class Command(BaseCommand):
    help = "Kagua na rekebisha akaunti za kuingia"

    def add_arguments(self, parser):
        parser.add_argument("--reset", metavar="USERNAME",
                            help="Rekebisha nenosiri la mtumiaji mmoja")
        parser.add_argument("--reset-all", action="store_true",
                            help="Rekebisha nenosiri za watumiaji wote wa mfano")
        parser.add_argument("--password", default=DEFAULT_PASSWORD,
                            help=f"Nenosiri jipya (chaguo-msingi: {DEFAULT_PASSWORD})")

    def handle(self, *args, **opts):
        pw = opts["password"]

        if opts["reset"]:
            self._reset_one(opts["reset"], pw)
            return
        if opts["reset_all"]:
            for username in DEMO:
                self._reset_one(username, pw, quiet=True)
            self.stdout.write(self.style.SUCCESS(
                f"Watumiaji wote wa mfano wamewekewa nenosiri: {pw}"))
            return

        self._report(pw)

    # ------------------------------------------------------------------
    def _reset_one(self, username, pw, quiet=False):
        user, created = User.objects.get_or_create(
            username=username, defaults={"role": DEMO.get(username, Role.MEMBER)})
        user.set_password(pw)
        user.is_active = True
        if username == "admin":
            user.is_staff = user.is_superuser = True
        elif username in DEMO and DEMO[username] != Role.MEMBER:
            user.is_staff = True
        user.save()

        if username == "mwanachama" and not hasattr(user, "member"):
            member = Member.objects.filter(user__isnull=True).first()
            if member:
                member.user = user
                member.save(update_fields=["user"])
                if not quiet:
                    self.stdout.write(f"  Ameunganishwa na {member.membership_no}")

        if not quiet:
            verb = "ameundwa" if created else "amerekebishwa"
            self.stdout.write(self.style.SUCCESS(
                f"{username} {verb}. Nenosiri: {pw}"))

    def _report(self, pw):
        total = User.objects.count()
        self.stdout.write(f"Watumiaji kwenye database: {total}")
        if total == 0:
            self.stdout.write(self.style.ERROR(
                "\nHAKUNA MTUMIAJI HATA MMOJA.\n"
                "Endesha:  python manage.py seed"))
            return

        self.stdout.write("")
        self.stdout.write(f"{'MTUMIAJI':<14}{'HAI':<6}{'JUKUMU':<16}{'NENOSIRI':<12}MWANACHAMA")
        self.stdout.write("-" * 62)
        broken = []
        for username in DEMO:
            u = User.objects.filter(username=username).first()
            if u is None:
                self.stdout.write(f"{username:<14}{'—':<6}{'HAYUPO':<16}")
                broken.append(username)
                continue
            ok = u.check_password(pw)
            auth = authenticate(username=username, password=pw) is not None
            linked = "ndiyo" if hasattr(u, "member") else "hapana"
            status = "sawa" if (ok and auth) else "IMEVUNJIKA"
            if status != "sawa":
                broken.append(username)
            self.stdout.write(
                f"{username:<14}{'ndiyo' if u.is_active else 'HAPANA':<6}"
                f"{u.role:<16}{status:<12}{linked}")

        self.stdout.write("")
        if broken:
            self.stdout.write(self.style.ERROR(
                f"Zilizovunjika: {', '.join(broken)}\n"
                f"Rekebisha kwa:  python manage.py akaunti --reset-all"))
        else:
            self.stdout.write(self.style.SUCCESS("Akaunti zote ziko sawa."))

        member_user = User.objects.filter(username="mwanachama").first()
        if member_user and not hasattr(member_user, "member"):
            self.stdout.write(self.style.WARNING(
                "\nOnyo: 'mwanachama' hajaunganishwa na rekodi ya mwanachama. "
                "Ataingia lakini ataelekezwa nyumbani.\n"
                "Rekebisha kwa:  python manage.py akaunti --reset mwanachama"))
