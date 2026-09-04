"""
Hamisha waratibu wa kanda kuwa viongozi wa ngazi ya kanda.

TATIZO LILILOKUWEPO
Mfumo ulikuwa na NJIA MBILI za kuchuja wanachama kwa eneo:

  1. Ya zamani — `user.role == "coordinator"` pamoja na `user.region`.
     Ilikuwa ikitumika kwenye kurasa za `/wanachama/`, `/maombi/` n.k.
  2. Mpya — `Leadership` pamoja na `geo.scope`.

Mratibu alikuwa hana rekodi ya `Leadership`, kwa hiyo `scope_members()`
ilimrudishia SIFURI. Alikuwa amekwama katikati: hafiki `/uongozi/`, na
kurasa zake za zamani nazo hazimwonyeshi mtu.

SULUHISHO
Kila mratibu anapewa `Leadership` ya ngazi ya kanda. Baada ya hapo kuna
mfumo MMOJA wa kuchuja, si miwili — na `coordinator` inabaki kuwa jina
la jukumu tu, si mantiki ya kipekee.

    python manage.py hamisha_waratibu
    python manage.py hamisha_waratibu --onyesha    # ona bila kubadilisha
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Role
from geo.models import LeaderLevel, LeaderPost, Leadership, Zone

User = get_user_model()


class Command(BaseCommand):
    help = "Hamisha waratibu wa kanda kuwa viongozi wa ngazi ya kanda"

    def add_arguments(self, parser):
        parser.add_argument("--onyesha", action="store_true",
                            help="Onyesha bila kubadilisha chochote")

    def handle(self, *args, **opts):
        ok, warn = self.style.SUCCESS, self.style.WARNING
        onyesha = opts["onyesha"]

        waratibu = User.objects.filter(role=Role.COORDINATOR)
        if not waratibu.exists():
            self.stdout.write(warn("Hakuna mratibu kwenye mfumo."))
            return

        n = ruka = bila_kanda = 0
        for u in waratibu.select_related("region__zone"):
            zone = self._zone_for(u)
            if zone is None:
                bila_kanda += 1
                self.stdout.write(warn(
                    f"  {u.username}: hana kanda inayojulikana — amerukwa"))
                continue

            ipo = Leadership.objects.filter(
                user=u, level=LeaderLevel.ZONE, zone=zone,
                ended_on__isnull=True).exists()
            if ipo:
                ruka += 1
                self.stdout.write(f"  {u.username}: tayari ni kiongozi wa {zone}")
                continue

            self.stdout.write(f"  {u.username}: -> kiongozi wa kanda {zone}")
            if not onyesha:
                Leadership.objects.create(
                    user=u, level=LeaderLevel.ZONE, post=LeaderPost.CHAIR,
                    zone=zone, started_on=timezone.localdate(),
                    note="Amehamishwa kutoka jukumu la mratibu")
            n += 1

        if onyesha:
            self.stdout.write(warn(
                f"\n(onyesha tu) Wangehamishwa: {n}. "
                f"Waliopo tayari: {ruka}. Wasio na kanda: {bila_kanda}."))
            return

        self.stdout.write(ok(
            f"\nWamehamishwa: {n}. Waliokuwepo tayari: {ruka}. "
            f"Wasio na kanda: {bila_kanda}."))
        if n:
            self.stdout.write(
                "Sasa wanaona kanda zao kupitia `geo.scope`, na wanafika "
                "/uongozi/ pamoja na kurasa zao za zamani.")

    @staticmethod
    def _zone_for(user):
        """
        Kanda ya mratibu.

        Inatafutwa kwa njia mbili: kupitia `Zone.coordinator` (uhusiano wa
        moja kwa moja), au kupitia mkoa wake. Ya kwanza ni ya uhakika
        zaidi — ndiyo iliyowekwa na `seed` na `watumishi`.
        """
        zone = Zone.objects.filter(coordinator=user).first()
        if zone:
            return zone
        if user.region_id and user.region.zone_id:
            return user.region.zone
        return None
