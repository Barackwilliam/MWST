"""
Weka mpangilio rasmi wa vifurushi kama ulivyo kwenye bango la MWST.

Inaweka thamani za sehemu MPYA pekee (ada ya usajili, ada ya mwaka, alama,
n.k.). Haiguswi `name`, `benefits` wala `colour` ya kategoria zilizopo tayari
— hizo ni maudhui ya mteja. `Diamond` inaundwa kama haipo.
"""
from decimal import Decimal

from django.db import migrations

#  code, jina,       usajili, mwaka,  alama, plus,  kipaumbele, uongozi, rangi, order
TIERS = [
    ("B", "Bronze",     5000,   20000,   100, False, False, False, "#a5682a", 0),
    ("S", "Silver",    10000,   50000,   250, False, True,  False, "#9aa0a6", 1),
    ("G", "Gold",      20000,  100000,   500, False, True,  True,  "#d4af37", 2),
    ("P", "Platinum",  30000,  250000,  1000, False, True,  True,  "#14417c", 3),
    ("D", "Diamond",   50000,  500000,  2000, True,  True,  True,  "#6b1f8f", 4),
]


def apply_tiers(apps, schema_editor):
    Category = apps.get_model("members", "Category")

    for code, name, reg, annual, points, plus, priority, leadership, colour, order in TIERS:
        pkg = {
            "registration_fee": Decimal(reg),
            "annual_fee": Decimal(annual),
            "duration_years": 1,
            "recognition_points": points,
            "points_plus": plus,
            "has_card": True,
            "has_events": True,
            "has_reports": True,
            "has_certificate": True,
            "has_priority": priority,
            "has_leadership": leadership,
            # Rangi za kadi ni sehemu ya muundo rasmi wa bango.
            "colour": colour,
        }
        cat = Category.objects.filter(code=code).first()
        if cat is None:
            # Kategoria mpya (kwa kawaida Diamond) — weka pia maudhui ya msingi.
            Category.objects.create(
                code=code, name=name, name_en=name, order=order,
                monthly_fee=Decimal(annual) / 12, points_per_payment=max(points // 10, 10),
                is_featured=(code == "G"), is_selectable=True, is_special=False,
                **pkg)
            continue
        for field, value in pkg.items():
            setattr(cat, field, value)
        cat.save(update_fields=list(pkg))


def undo(apps, schema_editor):
    """Hakuna cha kurudisha — sehemu mpya zitafutwa na migration ya schema."""


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0004_category_annual_fee_category_duration_years_and_more"),
    ]

    operations = [
        migrations.RunPython(apply_tiers, undo),
    ]
