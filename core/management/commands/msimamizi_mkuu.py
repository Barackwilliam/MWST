"""
Tengeneza au sasisha akaunti ya msimamizi mkuu.

Akaunti hii ni ya DJANGO ADMIN PEKEE. Haiwezi kuingia `/ingia/` —
`login_view` inakataa msimamizi mkuu kwa makusudi. Faida: hata mtu
aliyeiba nenosiri lake hawezi kulitumia kwenye ukurasa wa kawaida,
wala hawezi kujua kama nenosiri ni sahihi.

    python manage.py msimamizi_mkuu system
    python manage.py msimamizi_mkuu system --nenosiri "kisima-tende-dodoma"

Bila `--nenosiri`, itakuuliza (haitaonekana unapoandika).

Inaondoa pia `is_superuser` kwa akaunti nyingine zote — msimamizi mkuu
mmoja ndiye anayestahili kuwepo, na wengine wanaendelea na `/dashibodi/`
kama kawaida.
"""
import getpass

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from accounts.models import Role, User

#: Nenosiri linalojulikana kwa kila mtu duniani. Akaunti hii inafungua
#: database nzima — namba za vitambulisho, simu na rekodi za fedha.
DHAIFU = {
    "admin", "admin123", "password", "12345678", "123456", "1234",
    "mwst2026", "muwesta", "qwerty", "letmein", "changeme", "admin1234",
}


class Command(BaseCommand):
    help = "Tengeneza msimamizi mkuu wa Django admin (hawezi kuingia /ingia/)"

    def add_arguments(self, parser):
        parser.add_argument("username", help="Jina la mtumiaji, mfano: system")
        parser.add_argument("--nenosiri", default="", help="Nenosiri jipya")
        parser.add_argument("--lazimisha", action="store_true",
                            help="Kubali nenosiri dhaifu")
        parser.add_argument("--acha-wengine", action="store_true",
                            help="Usiondoe is_superuser kwa akaunti nyingine")

    def handle(self, *args, **opts):
        ok, warn, err = self.style.SUCCESS, self.style.WARNING, self.style.ERROR
        username = opts["username"].strip()

        password = opts["nenosiri"] or getpass.getpass("Nenosiri: ")
        if not password:
            raise CommandError("Nenosiri halikuwekwa.")

        if password.lower() in DHAIFU and not opts["lazimisha"]:
            raise CommandError(
                f"Nenosiri {password!r} ni miongoni mwa yanayojaribiwa kwanza "
                f"kabisa na mashambulizi. Akaunti hii inafungua database "
                f"nzima.\n\nJaribu maneno manne yasiyohusiana, mfano:\n"
                f"    kisima-tende-dodoma-nane\n\n"
                f"Ukiwa na uhakika, ongeza --lazimisha.")

        try:
            validate_password(password)
        except ValidationError as e:
            if not opts["lazimisha"]:
                raise CommandError(
                    "Nenosiri ni dhaifu:\n  " + "\n  ".join(e.messages) +
                    "\n\nUkiwa na uhakika, ongeza --lazimisha.")
            self.stdout.write(warn("Onyo: " + "; ".join(e.messages)))

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"first_name": "MUWESTA", "last_name": "System",
                      "role": Role.SUPER_ADMIN},
        )
        user.set_password(password)
        user.is_staff = True          # Django inadai hii ili aone admin
        user.is_superuser = True
        user.is_active = True
        user.save()

        self.stdout.write(ok(
            f"{'Imeundwa' if created else 'Imesasishwa'}: {username}"))

        if not opts["acha_wengine"]:
            wengine = User.objects.filter(is_superuser=True).exclude(pk=user.pk)
            majina = list(wengine.values_list("username", flat=True))
            if majina:
                # Hawapotezi `/dashibodi/` — `is_staff` inabaki.
                wengine.update(is_superuser=False)
                self.stdout.write(warn(
                    f"Wameondolewa umsimamizi mkuu (wanaendelea na "
                    f"/dashibodi/): {', '.join(majina)}"))

        self.stdout.write(
            "\nAkaunti hii ni ya Django admin PEKEE. Haiwezi kuingia /ingia/.\n"
            "Itumie kwenye njia yako ya siri (DJANGO_ADMIN_URL).")
