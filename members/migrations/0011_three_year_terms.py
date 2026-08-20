"""
Rekebisha muda wa uanachama na ada ya Tanzanite.

1. `duration_years` ilikuwa 1 kwa madaraja YOTE, ikipingana na uamuzi
   kwamba uanachama hudumu MIAKA MITATU. Kurasa za umma zilisoma thamani
   hii, kwa hiyo tovuti ilikuwa ikisema "mwaka 1" wakati mfumo ukisogeza
   tarehe kwa miaka mitatu.

2. Ada ya usajili ya Tanzanite ilikuwa TSh 1,000,000. Imepunguzwa hadi
   TSh 500,000 kwa kila kipindi cha miaka mitatu.
"""
from django.db import migrations


def forwards(apps, schema_editor):
    Category = apps.get_model("members", "Category")
    Category.objects.update(duration_years=3)
    Category.objects.filter(code="T").update(registration_fee=500000)


def backwards(apps, schema_editor):
    Category = apps.get_model("members", "Category")
    Category.objects.update(duration_years=1)
    Category.objects.filter(code="T").update(registration_fee=1000000)


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0010_alter_category_duration_years"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
