"""Filters za MUWESTA."""
from django import template
from django.utils.translation import gettext

register = template.Library()


@register.filter(name="tr")
def tr(value):
    """
    Tafsiri thamani inayotoka kwenye data (sio literal ya template).

    Matumizi:  {{ k.label|tr }}
    Kama neno halipo kwenye kamusi, linarudi kama lilivyo.
    """
    if value is None:
        return ""
    return gettext(str(value))


@register.filter(name="tx")
def tx(obj, field):
    """
    Rudisha thamani ya sehemu kwa lugha inayotumika sasa.

    Modeli zenye `Bilingual` zina `.tx("title")`, lakini kiolezo hakiwezi
    kuita method yenye hoja. Filter hii ndiyo daraja.
    """
    if hasattr(obj, "tx"):
        return obj.tx(field)
    return getattr(obj, field, "")
