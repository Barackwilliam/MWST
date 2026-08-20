"""
Weka alama kwenye ada za zamani ili zisisogeze uanachama tena.

`membership_applied` iliongezwa baada ya rekodi hizi kuundwa, kwa hiyo
zote zina `False`. Bila hii, rekodi ya zamani ikihifadhiwa tena kwa
sababu yoyote — afisa akihariri, script ikipitia — signal ingesogeza
tarehe ya kuisha ya mwanachama kwa kipindi kizima cha miaka mitatu
ambacho hakulipia.
"""
from django.db import migrations


def mark_applied(apps, schema_editor):
    Contribution = apps.get_model("finance", "Contribution")
    Contribution.objects.filter(purpose="ada").update(membership_applied=True)


def unmark(apps, schema_editor):
    Contribution = apps.get_model("finance", "Contribution")
    Contribution.objects.filter(purpose="ada").update(membership_applied=False)


class Migration(migrations.Migration):

    dependencies = [
        ("finance", "0006_contribution_application_and_more"),
    ]

    operations = [
        migrations.RunPython(mark_applied, unmark),
    ]
