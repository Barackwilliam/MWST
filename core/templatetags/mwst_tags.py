"""Filters za MWST."""
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
