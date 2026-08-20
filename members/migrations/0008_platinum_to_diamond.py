"""
Platinum inabadilishwa kuwa Diamond, na ada ya mwezi ya Silver inakuwa 25,000.

Njia iliyotumika: **safu ya Platinum inabadilishwa jina**, si kuhamisha
wanachama. Wanachama 19 waliokuwa Platinum wanakuwa Diamond papo hapo bila
rekodi yoyote kugusa — hakuna hatari ya kupoteza mtu njiani.

Safu ya zamani ya `Diamond` (iliyoundwa na migration 0005 na kustaafishwa
na 0006) haikuwa na mwanachama hata mmoja, kwa hiyo inafutwa ili jina na
herufi `D` zipatikane.

Namba za uanachama za zamani (`MWST/P/000123/2026`) hazibadiliki — ni
vitambulisho vilivyochapishwa kwenye kadi. Za baadaye zitatumia `D`.
"""
from decimal import Decimal

from django.db import migrations


def to_diamond(apps, schema_editor):
    Category = apps.get_model("members", "Category")
    Member = apps.get_model("members", "Member")

    # 1. Futa safu ya Diamond isiyotumika ili herufi "D" ipatikane.
    unused = Category.objects.filter(code="D").first()
    if unused is not None:
        if Member.objects.filter(category=unused).exists():
            # Ina wanachama kinyume na matarajio — usifute, ibadilishe jina.
            unused.name = "Diamond (ya zamani)"
            unused.code = "X"
            unused.is_selectable = False
            unused.save(update_fields=["name", "code", "is_selectable"])
        else:
            unused.delete()

    # 2. Platinum inakuwa Diamond.
    platinum = Category.objects.filter(code="P").first()
    if platinum is not None:
        platinum.code = "D"
        platinum.name = "Diamond"
        platinum.name_en = "Diamond"
        platinum.colour = "#6b1f8f"
        platinum.save(update_fields=["code", "name", "name_en", "colour"])

    # 3. Ada ya mwezi ya Silver.
    silver = Category.objects.filter(code="S").first()
    if silver is not None:
        silver.monthly_fee = Decimal(25000)
        silver.save(update_fields=["monthly_fee"])


def undo(apps, schema_editor):
    Category = apps.get_model("members", "Category")
    diamond = Category.objects.filter(code="D").first()
    if diamond is not None:
        diamond.code = "P"
        diamond.name = "Platinum"
        diamond.name_en = "Platinum"
        diamond.colour = "#14417c"
        diamond.save(update_fields=["code", "name", "name_en", "colour"])
    silver = Category.objects.filter(code="S").first()
    if silver is not None:
        silver.monthly_fee = Decimal(20000)
        silver.save(update_fields=["monthly_fee"])


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0007_application_id_type_member_id_type_and_more"),
    ]

    operations = [
        migrations.RunPython(to_diamond, undo),
    ]
