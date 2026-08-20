"""Viongozi wapya wa MUWESTA (Agosti 2026)."""
from django.db import migrations

LEADERS = [
    ("Ramadhani Juma Hussein", "Mwenyekiti",            "Chairman"),
    ("Ramadhani Juma Magembe", "Makamu Mwenyekiti",     "Vice Chairman"),
    ("Yahya Idd Nyambo",       "Katibu",                "Secretary"),
    ("Jumaa Bakari Mashango",  "Katibu Msaidizi",       "Assistant Secretary"),
    ("Mohammed O. Kapera",     "Mweka Hazina",          "Treasurer"),
    ("Omari Mziray",           "Mweka Hazina Msaidizi", "Assistant Treasurer"),
]


def set_leaders(apps, schema_editor):
    """
    Weka orodha rasmi. Viongozi wa zamani wanaondolewa kwa sababu orodha
    hii ndiyo iliyothibitishwa na shirika — si nyongeza.
    """
    Leader = apps.get_model("content", "Leader")
    Leader.objects.all().delete()
    for i, (name, role, role_en) in enumerate(LEADERS):
        Leader.objects.create(full_name=name, role=role, role_en=role_en,
                              order=i, is_active=True)


def undo(apps, schema_editor):
    """Hakuna cha kurudisha — orodha ya zamani haikuhifadhiwa."""


class Migration(migrations.Migration):

    dependencies = [("content", "0003_alter_announcement_options_announcement_approved_at_and_more")]

    operations = [migrations.RunPython(set_leaders, undo)]
