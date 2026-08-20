"""
Badilisha jina la chapa MWST -> MUWESTA ndani ya maudhui yaliyo kwenye
database (habari, matukio, maswali, historia, maelezo ya picha n.k.).

Kubadilisha code peke yake hakutoshi: maandishi mengi yanayoonekana kwenye
tovuti yamehifadhiwa kwenye database, si kwenye faili.

Sehemu za VITAMBULISHO hazibadilishwi:
    membership_no, receipt_no, reference, serial, code, slug, email, url
Namba za uanachama na risiti zilizokwisha tolewa zimechapishwa kwenye kadi
na kutumwa kwa watu. Zikibadilika, kumbukumbu za nyuma hazitalingana na
zilizopo mikononi mwa wanachama.
"""
import re

from django.db import migrations

#: Programu ambazo maudhui yake yanaonekana kwa umma.
APPS = ["content", "programs", "members", "finance", "geo", "accounts", "core"]

#: Sehemu zenye vitambulisho — hizi hazishikwi.
ID_FIELDS = {
    "membership_no", "receipt_no", "reference", "serial", "code", "slug",
    "email", "url", "username", "password", "file", "image", "phone",
}

PATTERN = re.compile(r"\bMWST\b")


def _fields(model):
    for field in model._meta.get_fields():
        if not getattr(field, "concrete", False):
            continue
        if field.get_internal_type() not in ("CharField", "TextField"):
            continue
        if field.name in ID_FIELDS:
            continue
        yield field.name


def rebrand(apps, schema_editor):
    total = 0
    for app_label in APPS:
        try:
            app_models = apps.get_app_config(app_label).get_models()
        except LookupError:
            continue
        for model in app_models:
            names = list(_fields(model))
            if not names:
                continue
            query = model.objects.all()
            for obj in query.iterator(chunk_size=500):
                touched = []
                for name in names:
                    value = getattr(obj, name, None)
                    if isinstance(value, str) and "MWST" in value:
                        new = PATTERN.sub("MUWESTA", value)
                        if new != value:
                            setattr(obj, name, new)
                            touched.append(name)
                if touched:
                    obj.save(update_fields=touched)
                    total += 1
    print(f"  MUWESTA: rekodi {total} zimebadilishwa")


def undo(apps, schema_editor):
    """Rudisha jina la awali ikibidi."""
    pattern = re.compile(r"\bMUWESTA\b")
    for app_label in APPS:
        try:
            app_models = apps.get_app_config(app_label).get_models()
        except LookupError:
            continue
        for model in app_models:
            names = list(_fields(model))
            if not names:
                continue
            for obj in model.objects.all().iterator(chunk_size=500):
                touched = []
                for name in names:
                    value = getattr(obj, name, None)
                    if isinstance(value, str) and "MUWESTA" in value:
                        setattr(obj, name, pattern.sub("MWST", value))
                        touched.append(name)
                if touched:
                    obj.save(update_fields=touched)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
        ("content", "0001_initial"),
        ("programs", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(rebrand, undo),
    ]
