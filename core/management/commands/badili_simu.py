"""
Badilisha namba ya simu ya mtumiaji.

Code ya kuingia huenda kwenye namba ya AKAUNTI YENYEWE, si kwenye
`SUPPORT_PHONE`. Namba ikiwa si sahihi, mwenye akaunti anafungiwa nje —
nenosiri ni sahihi lakini code haifiki popote.

    python manage.py badili_simu --orodha
    python manage.py badili_simu admin 0629712678

Inabadilisha namba ya `User` na ya `Member` yake (kama ipo) kwa pamoja.
Zikitofautiana, code inaweza kwenda kwenye ya zamani bila kueleweka.
"""
from django.core.management.base import BaseCommand, CommandError

from accounts.models import User
from core import sms


class Command(BaseCommand):
    help = "Badilisha namba ya simu ya mtumiaji (ndiko code za kuingia zinakoenda)"

    def add_arguments(self, parser):
        parser.add_argument("username", nargs="?", help="Jina la mtumiaji")
        parser.add_argument("phone", nargs="?", help="Namba mpya, mfano 0629712678")
        parser.add_argument("--orodha", action="store_true",
                            help="Onyesha maafisa na namba zao")

    def handle(self, *args, **opts):
        ok, err = self.style.SUCCESS, self.style.ERROR

        if opts["orodha"] or not opts["username"]:
            self.stdout.write("Maafisa na namba zao:\n")
            for u in User.objects.filter(is_staff=True).order_by("username"):
                member = getattr(u, "member", None)
                phone = (u.phone or "").strip() or "(haipo)"
                extra = f"  [member: {member.phone}]" if member and member.phone else ""
                self.stdout.write(
                    f"  {u.username:28} {phone:16} {u.get_full_name()}{extra}")
            if not opts["orodha"]:
                self.stdout.write(
                    "\nMatumizi: python manage.py badili_simu <username> <namba>")
            return

        phone = (opts["phone"] or "").strip()
        if not phone:
            raise CommandError("Weka namba mpya. Mfano: badili_simu admin 0629712678")

        # Kagua namba kabla ya kuhifadhi — namba mbovu ingemfungia mtu
        # nje tena, na wakati huo hatajua ni kwa nini.
        to = sms.msisdn(phone)
        if len(to) < 12:
            raise CommandError(f"Namba {phone!r} si sahihi (imekuwa {to!r}).")

        user = User.objects.filter(username=opts["username"]).first()
        if user is None:
            raise CommandError(f"Hakuna mtumiaji {opts['username']!r}. "
                               f"Tumia --orodha kuona waliopo.")

        zamani = user.phone
        user.phone = phone
        user.save(update_fields=["phone"])

        member = getattr(user, "member", None)
        if member:
            member.phone = phone
            member.save(update_fields=["phone"])

        self.stdout.write(ok(
            f"{user.username}: {zamani or '(haikuwepo)'} -> {phone}"))
        self.stdout.write(f"Code za kuingia sasa zitaenda {to}.")
