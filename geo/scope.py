"""
Ufinyu wa kuona — nani anaruhusiwa kuona wanachama gani.

SEHEMU HII NI MOJA KWA MAKUSUDI.

Kiongozi wa Kata A hapaswi kuona mwanachama wa Kata B. Sheria hiyo ni
rahisi kusema, lakini kwenye mfumo huu inagusa kila orodha, ripoti,
utafutaji, KPI na hesabu. Kila mahali panapouliza database peke yake ni
mahali pa kusahau kuchuja — na kusahau MARA MOJA kunafichua namba za
vitambulisho na anwani za watu kwa asiyestahili.

Kwa hiyo hakuna sehemu nyingine inayopaswa kuandika mantiki hii. Kila
kitu kinapita `scope_members(user)`.

    from geo.scope import scope_members
    qs = scope_members(request.user)          # badala ya Member.objects.all()

Kanuni:
  * Ngazi ya Taifa, msimamizi, na wafanyakazi wa makao makuu — wanaona wote
  * Kanda  -> wanachama wa mikoa yote ya kanda yake
  * Mkoa   -> wanachama wa mkoa wake (wilaya zote)
  * Wilaya -> wanachama wa wilaya yake (kata zote)
  * Kata   -> wanachama wa kata yake pekee
  * Mwanachama asiye kiongozi -> hakuna (anaona rekodi yake tu, si orodha)

Mtu mwenye wadhifa zaidi ya mmoja anaona MUUNGANO wa maeneo yake yote.
"""
from django.db.models import Q

from .models import LeaderLevel, LEVEL_ORDER

#: Majukumu ya makao makuu yanayoona kila mwanachama. Ni ya kazi za
#: kitaifa — usajili, fedha, michango — na hayana eneo maalum.
NATIONAL_ROLES = {"super_admin", "admin", "management", "registration",
                  "finance", "contributions", "welfare", "outreach"}


def active_posts(user):
    """Nyadhifa zake zinazotumika leo. Zilizoisha muda hazihesabiwi."""
    if not user or not user.is_authenticated:
        return []
    from django.utils import timezone

    today = timezone.localdate()
    return [p for p in user.leaderships.select_related(
        "ward", "district", "region", "zone").all()
        if (p.started_on is None or p.started_on <= today)
        and (p.ended_on is None or p.ended_on >= today)]


def sees_everyone(user):
    """Je, mtu huyu anaona wanachama wote?"""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or getattr(user, "role", "") in NATIONAL_ROLES:
        return True
    return any(p.level == LeaderLevel.NATIONAL for p in active_posts(user))


def top_level(user):
    """
    Ngazi yake ya juu kabisa, au `None` asipokuwa kiongozi.

    Inatumiwa na menyu na ukurasa wa matatizo kuamua nini cha kuonyesha.
    """
    posts = active_posts(user)
    if not posts:
        return LeaderLevel.NATIONAL if sees_everyone(user) else None
    return max((p.level for p in posts), key=lambda lv: LEVEL_ORDER.index(lv))


def member_filter(user):
    """
    `Q` inayochuja wanachama anaoruhusiwa kuona.

    Hurudisha `None` ikiwa anaona wote (hakuna kuchuja), au `Q(pk__in=[])`
    ikiwa haruhusiwi kuona yeyote.

    Kutumia `Q` badala ya queryset kunaruhusu kuiunganisha na vichujio
    vingine bila kupoteza ufinyu — mfano utafutaji wa jina ndani ya kata
    yake pekee.
    """
    if sees_everyone(user):
        return None

    posts = active_posts(user)
    if not posts:
        return Q(pk__in=[])

    q = Q()
    for p in posts:
        if p.level == LeaderLevel.WARD and p.ward_id:
            q |= Q(ward_id=p.ward_id)
        elif p.level == LeaderLevel.DISTRICT and p.district_id:
            # Mwanachama anaweza kuwa na wilaya bila kata; tunachukua
            # wote wa wilaya, si wa kata zake pekee.
            q |= Q(district_id=p.district_id)
        elif p.level == LeaderLevel.REGION and p.region_id:
            q |= Q(region_id=p.region_id)
        elif p.level == LeaderLevel.ZONE and p.zone_id:
            q |= Q(region__zone_id=p.zone_id)

    # Wadhifa usio na eneo (data mbovu) usifungue kila kitu.
    return q if q else Q(pk__in=[])


def scope_members(user, qs=None):
    """
    Wanachama anaoruhusiwa kuona.

    Hii ndiyo kazi ya kutumia kila mahali badala ya `Member.objects`.
    """
    from members.models import Member

    qs = Member.objects.all() if qs is None else qs
    f = member_filter(user)
    return qs if f is None else qs.filter(f)


def scope_queryset(user, qs, path="member__"):
    """
    Chuja kitu chochote kinachounganishwa na mwanachama.

    `path` ni njia ya kufikia mwanachama kutoka kwenye modeli husika —
    mfano `"member__"` kwa michango, au `""` kwa `Member` yenyewe.
    """
    f = member_filter(user)
    if f is None:
        return qs
    if not path:
        return qs.filter(f)
    # Geuza Q ya `ward_id=...` kuwa `member__ward_id=...`
    return qs.filter(_prefix(f, path))


def _prefix(q, path):
    """Ongeza njia mbele ya kila sehemu ya `Q`."""
    out = Q()
    out.connector = q.connector
    out.negated = q.negated
    for child in q.children:
        if isinstance(child, Q):
            out.children.append(_prefix(child, path))
        else:
            key, value = child
            out.children.append((path + key, value))
    return out


def can_see_member(user, member):
    """Je, mtu huyu anaruhusiwa kuona rekodi ya mwanachama huyu?"""
    if sees_everyone(user):
        return True
    return scope_members(user).filter(pk=member.pk).exists()


def areas_label(user):
    """Maelezo mafupi ya maeneo yake — kwa kuonyesha kwenye dashibodi."""
    if sees_everyone(user):
        return str(LeaderLevel.NATIONAL.label)
    posts = active_posts(user)
    if not posts:
        return ""
    return ", ".join(f"{p.get_post_display()} — {p.area_name}" for p in posts)
