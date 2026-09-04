"""
Jedwali za marejeo — mikoa, wilaya, kata, kanda, kategoria.

TATIZO: jedwali hizi hazibadiliki (mikoa ya Tanzania ni ile ile),
lakini zilikuwa zikipakiwa mara 5-6 kwa ukurasa mmoja — kwenye
vichujio, orodha kunjuzi, ramani na takwimu. Ukurasa wa maombi ulikuwa
na maswali 6 ya mikoa na 5 ya wilaya peke yake.

SULUHISHO: cache ya dakika kumi, inayofutwa rekodi inapohifadhiwa.
Muda ni mfupi kiasi kwamba hata cache isipofutwa kwa sababu yoyote,
mabadiliko yanaonekana ndani ya dakika kumi.

    from core.refdata import regions, districts, categories

    for r in regions():
        ...
"""
from django.core.cache import cache

TTL = 600          # dakika kumi
PREFIX = "mwst:ref:"


def _get(key, builder):
    out = cache.get(PREFIX + key)
    if out is None:
        out = builder()
        cache.set(PREFIX + key, out, TTL)
    return out


def clear(key=None):
    """Futa cache. Inaitwa na `save()` ya modeli husika."""
    if key:
        cache.delete(PREFIX + key)
        return
    for k in ("zones", "regions", "districts", "wards", "categories", "funds"):
        cache.delete(PREFIX + k)


# ---------------------------------------------------------------------------
#  Orodha
#
#  Zinarudishwa kama LIST, si queryset — queryset ingeuliza database
#  tena kila inapopitiwa, na hiyo ndiyo tunayojaribu kuepuka.
# ---------------------------------------------------------------------------
def zones():
    from geo.models import Zone
    return _get("zones", lambda: list(Zone.objects.all().order_by("name")))


def regions():
    from geo.models import Region
    return _get("regions", lambda: list(
        Region.objects.select_related("zone").order_by("name")))


def districts():
    from geo.models import District
    return _get("districts", lambda: list(
        District.objects.select_related("region").order_by("name")))


def categories(only_selectable=False):
    from members.models import Category

    rows = _get("categories", lambda: list(Category.objects.all().order_by("order", "name")))
    if only_selectable:
        return [c for c in rows if getattr(c, "is_selectable", True)]
    return rows


def funds():
    from finance.models import Fund
    return _get("funds", lambda: list(Fund.objects.all().order_by("order")))


def by_id(rows, pk):
    """Tafuta rekodi kwenye orodha iliyohifadhiwa, bila kugusa database."""
    for r in rows:
        if r.pk == pk:
            return r
    return None
