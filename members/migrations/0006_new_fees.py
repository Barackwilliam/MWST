"""
Bei mpya za vifurushi kama alivyothibitisha mteja (08 Agosti 2026).

Madaraja sasa ni matano: Bronze, Silver, Gold, Platinum, Tanzanite.
`Diamond` (iliyoundwa na migration 0005) inastaafishwa — haifutwi ili
kumbukumbu za nyuma zisipotee, bali inaondolewa kwenye ukurasa wa vifurushi.

Ada ya mwaka haikutolewa safari hii, kwa hiyo imewekwa 0 na safu yake
inafichwa kwenye jedwali hadi itakapotolewa.
"""
from decimal import Decimal

from django.db import migrations

#  code, jina,      usajili,  mwezi,   rangi,     order, alama, +, kipaumbele, uongozi
TIERS = [
    ("B", "Bronze",      10000,   10000, "#a5682a", 0,   100, False, False, False),
    ("S", "Silver",      20000,   25000, "#9aa0a6", 1,   250, False, True,  False),
    ("G", "Gold",        50000,   50000, "#d4af37", 2,   500, False, True,  True),
    ("P", "Platinum",   100000,  100000, "#14417c", 3,  1000, False, True,  True),
    ("T", "Tanzanite", 1000000,  200000, "#6b1f8f", 4,  2000, True,  True,  True),
]


def apply_prices(apps, schema_editor):
    Category = apps.get_model("members", "Category")

    for code, name, reg, monthly, colour, order, points, plus, priority, lead in TIERS:
        values = {
            "registration_fee": Decimal(reg),
            "monthly_fee": Decimal(monthly),
            # Haikutolewa safari hii — safu inafichwa hadi itakapowekwa.
            "annual_fee": Decimal(0),
            "duration_years": 1,
            "colour": colour,
            "order": order,
            "is_special": False,
            "is_selectable": True,
            "recognition_points": points,
            "points_plus": plus,
            "has_card": True,
            "has_events": True,
            "has_reports": True,
            "has_certificate": True,
            "has_priority": priority,
            "has_leadership": lead,
        }
        cat = Category.objects.filter(code=code).first()
        if cat is None:
            Category.objects.create(
                code=code, name=name, name_en=name,
                points_per_payment=10, is_featured=(code == "G"), **values)
            continue
        for field, value in values.items():
            setattr(cat, field, value)
        cat.save(update_fields=list(values))

    # Diamond haitumiki tena. Tunaiacha kwenye database (huenda ina
    # kumbukumbu) lakini tunaiondoa kwenye ukurasa wa vifurushi.
    diamond = Category.objects.filter(code="D").first()
    if diamond is not None:
        diamond.registration_fee = Decimal(0)
        diamond.annual_fee = Decimal(0)
        diamond.is_selectable = False
        diamond.save(update_fields=["registration_fee", "annual_fee", "is_selectable"])


def undo(apps, schema_editor):
    """Hakuna cha kurudisha — ni thamani tu, si muundo."""


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0005_package_pricing"),
    ]

    operations = [
        migrations.RunPython(apply_prices, undo),
    ]
