"""
Onyesha ni wanachama gani mtumiaji anaruhusiwa kuona.

Awamu ya kwanza haina dashibodi ya kiongozi bado, kwa hiyo hii ndiyo
njia ya kuthibitisha kwamba ufinyu unafanya kazi kwa data YAKO halisi —
si kwa data ya mfano tu.

    python manage.py angalia_scope jaribio.kata.mwenyekiti
    python manage.py angalia_scope --wote          # linganisha viongozi wote
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from geo.scope import active_posts, areas_label, scope_members, sees_everyone
from members.models import Member

User = get_user_model()


class Command(BaseCommand):
    help = "Onyesha wanachama anaowaona mtumiaji"

    def add_arguments(self, parser):
        parser.add_argument("username", nargs="?")
        parser.add_argument("--wote", action="store_true",
                            help="Linganisha viongozi wote kwa pamoja")
        parser.add_argument("--orodha", type=int, default=5,
                            help="Wanachama wangapi wa kuorodhesha (0 = hakuna)")

    def handle(self, *args, **opts):
        ok, warn = self.style.SUCCESS, self.style.WARNING
        jumla = Member.objects.count()

        if opts["wote"] or not opts["username"]:
            viongozi = User.objects.filter(leaderships__isnull=False).distinct()
            if not viongozi:
                self.stdout.write(warn(
                    "Hakuna kiongozi yeyote. Endesha `seed_viongozi` kwanza."))
                return
            self.stdout.write(f"Wanachama wote: {jumla}\n")
            self.stdout.write(f"  {'Jina la mtumiaji':32} {'Eneo':34} {'Anaona'}")
            self.stdout.write("  " + "-" * 78)
            for u in viongozi.order_by("username"):
                n = scope_members(u).count()
                self.stdout.write(
                    f"  {u.username:32} {areas_label(u)[:33]:34} {n:>4}/{jumla}")
            return

        user = User.objects.filter(username=opts["username"]).first()
        if user is None:
            raise CommandError(f"Hakuna mtumiaji {opts['username']!r}.")

        posts = active_posts(user)
        self.stdout.write(f"\nMtumiaji : {user.username} ({user.get_full_name()})")
        self.stdout.write(f"Jukumu   : {user.role}")
        self.stdout.write(f"Anaona wote? {sees_everyone(user)}")

        self.stdout.write("\nNyadhifa zinazotumika:")
        if not posts:
            self.stdout.write("  (hakuna)")
        for p in posts:
            hadi = p.ended_on or "—"
            self.stdout.write(
                f"  {p.get_post_display():14} {p.get_level_display():10} "
                f"{p.area_name:26} tangu {p.started_on} hadi {hadi}")

        qs = scope_members(user)
        n = qs.count()
        self.stdout.write(ok(f"\nAnaona wanachama {n} kati ya {jumla}."))

        limit = opts["orodha"]
        if limit and n:
            self.stdout.write("\nMifano:")
            for m in qs.select_related("ward", "district", "region")[:limit]:
                mahali = " / ".join(str(x) for x in
                                    [m.ward, m.district, m.region] if x)
                self.stdout.write(f"  {m.membership_no or '—':24} "
                                  f"{m.full_name[:22]:24} {mahali}")

        # Wasiowaona ndiyo uthibitisho halisi. Idadi peke yake inaweza
        # kudanganya ikiwa wanachama wote wako eneo moja.
        nje = Member.objects.exclude(pk__in=qs.values("pk"))
        self.stdout.write(f"\nHAWAONEKANI kwake: {nje.count()}")
        if limit and nje.exists():
            for m in nje.select_related("ward", "district")[:limit]:
                mahali = " / ".join(str(x) for x in [m.ward, m.district] if x)
                self.stdout.write(f"  {m.full_name[:22]:24} {mahali}")
