"""
Tengeneza makundi ya ruhusa kwa kila jukumu na uwapange watumiaji.

Bila hii, afisa ana `is_staff=True` lakini hana ruhusa yoyote, kwa hiyo
kila ukurasa wa `/usimamizi/` unamkatalia (403).

Endesha:  python manage.py ruhusa
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Role

User = get_user_model()

#: Kila jukumu na models linazoruhusiwa kuzigusa.
#: "rw" = kusoma na kuandika, "r" = kusoma tu
MATRIX = {
    Role.SUPER_ADMIN: "ALL",
    Role.ADMIN: "ALL",
    Role.MANAGEMENT: {
        "r": ["members.member", "members.application", "members.card",
              "finance.payment", "finance.contribution", "finance.ledgerentry",
              "finance.donor", "finance.project", "finance.campaign",
              "programs.event", "programs.assistancerequest",
              "content.news", "content.mediaitem", "accounts.auditlog",
              "geo.region", "geo.district"],
        "rw": ["content.announcement", "content.sitesetting"],
    },
    Role.REGISTRATION: {
        "rw": ["members.member", "members.application", "members.card",
               "members.familymember", "members.beneficiary", "members.category"],
        "r": ["geo.region", "geo.district", "geo.ward", "geo.branch",
              "finance.payment"],
    },
    Role.FINANCE: {
        "rw": ["finance.payment", "finance.account"],
        "r": ["finance.ledgerentry", "finance.fund", "members.member",
              "members.category", "programs.pointtransaction"],
    },
    Role.CONTRIBUTIONS: {
        "rw": ["finance.contribution", "finance.project", "finance.campaign",
               "finance.donor", "finance.expense"],
        "r": ["finance.fund", "finance.ledgerentry", "members.member"],
    },
    Role.WELFARE: {
        "rw": ["programs.assistancerequest", "programs.assistancetype"],
        "r": ["members.member", "members.familymember", "members.beneficiary",
              "finance.expense"],
    },
    Role.OUTREACH: {
        "rw": ["finance.donor", "finance.campaign", "finance.project",
               "programs.event", "programs.eventtype", "programs.eventregistration",
               "content.mediaitem", "content.album", "content.news",
               "content.announcement"],
        "r": ["finance.contribution", "members.member", "geo.region"],
    },
    Role.COORDINATOR: {
        "rw": ["programs.event", "programs.eventregistration", "content.mediaitem",
               "content.announcement", "content.news", "finance.project"],
        "r": ["members.member", "members.application", "finance.payment",
              "finance.contribution", "geo.region", "geo.district", "geo.branch",
              "geo.zone", "geo.ward"],
    },
}

READ = ["view"]
WRITE = ["view", "add", "change", "delete"]

#: Kila mtumishi anapata haya. Nav inaonyesha viungo hivi kwa majukumu yote,
#: kwa hiyo bila msingi huu baadhi ya viungo vingekataliwa (403).
BASELINE_READ = [
    "content.contactmessage", "content.notification", "content.sitesetting",
    "content.announcement", "content.news", "content.album", "content.mediaitem",
    "accounts.user", "accounts.auditlog",
    "members.member", "members.card", "members.category", "members.familymember",
    "geo.region", "geo.district", "geo.branch",
    "finance.fund", "finance.project", "finance.campaign", "finance.donor",
    "programs.pointrule", "programs.pointtransaction", "programs.reward",
    "programs.event", "programs.assistancerequest",
]


class Command(BaseCommand):
    help = "Tengeneza makundi ya ruhusa kwa kila jukumu"

    @transaction.atomic
    def handle(self, *args, **opts):
        for role, spec in MATRIX.items():
            group, _created = Group.objects.get_or_create(name=str(role.label))
            group.permissions.clear()

            if spec == "ALL":
                group.permissions.set(Permission.objects.all())
                self.stdout.write(f"  {role.label:<26} ruhusa zote")
            else:
                perms = []
                baseline = [m for m in BASELINE_READ if m not in spec.get("rw", [])]
                for models, actions in ((baseline, READ),
                                        (spec.get("r", []), READ),
                                        (spec.get("rw", []), WRITE)):
                    for dotted in models:
                        app_label, model = dotted.split(".")
                        perms += list(Permission.objects.filter(
                            content_type__app_label=app_label,
                            content_type__model=model,
                            codename__in=[f"{a}_{model}" for a in actions]))
                group.permissions.set(perms)
                self.stdout.write(f"  {role.label:<26} ruhusa {len(perms)}")

            # Panga watumiaji wa jukumu hili kwenye kundi
            users = User.objects.filter(role=role)
            for u in users:
                u.groups.set([group])
                if not u.is_staff:
                    u.is_staff = True
                    u.save(update_fields=["is_staff"])

        # Mwanachama hapaswi kuingia kwenye usimamizi kabisa
        User.objects.filter(role=Role.MEMBER).update(is_staff=False)

        self.stdout.write(self.style.SUCCESS(
            "\nMakundi ya ruhusa yamekamilika. Wanachama wamezuiliwa /usimamizi/."))
