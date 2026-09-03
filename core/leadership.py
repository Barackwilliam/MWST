"""
Maswali ya sehemu ya uongozi.

KANUNI: hakuna swali linalouliza database bila kupita `geo.scope`.
Kila kazi hapa inachukua `user` na kuchuja kwa maeneo yake. Kusahau
mara moja kunamaanisha kiongozi wa Kata A anaona wanachama wa Kata B.
"""
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.translation import gettext as _

from geo.models import LeaderLevel, LEVEL_ORDER, Leadership
from geo.scope import (active_posts, areas_label, member_filter, scope_members,
                       sees_everyone, top_level)
from members.models import Member, MemberStatus
from programs.models import Broadcast, Case, CaseStatus, Thread


def is_leader(user):
    """Je, mtu huyu ana sehemu ya uongozi?"""
    return bool(active_posts(user)) or sees_everyone(user)


# ---------------------------------------------------------------------------
#  Matatizo
# ---------------------------------------------------------------------------
def scope_cases(user, qs=None):
    """
    Matatizo anayoruhusiwa kuona.

    Tofauti na wanachama, tatizo linaonekana kwa ngazi ILIYONALO SASA —
    si kwa kila ngazi iliyo juu. Kiongozi wa mkoa haoni kila tatizo la
    kila kata; anaona yaliyofika kwake, pamoja na aliyoyapandisha.

    Sababu: kama kila kiongozi wa juu angeona kila tatizo la chini,
    mtiririko wa kupandisha usingekuwa na maana — na dashibodi ya mkoa
    ingekuwa na kelele isiyo na mwisho.
    """
    qs = Case.objects.all() if qs is None else qs
    if sees_everyone(user):
        return qs

    posts = active_posts(user)
    if not posts:
        return qs.none()

    q = Q()
    for p in posts:
        if p.level == LeaderLevel.WARD and p.ward_id:
            q |= Q(level=LeaderLevel.WARD, ward_id=p.ward_id)
        elif p.level == LeaderLevel.DISTRICT and p.district_id:
            q |= Q(level=LeaderLevel.DISTRICT, district_id=p.district_id)
        elif p.level == LeaderLevel.REGION and p.region_id:
            q |= Q(level=LeaderLevel.REGION, region_id=p.region_id)
        elif p.level == LeaderLevel.ZONE and p.zone_id:
            q |= Q(level=LeaderLevel.ZONE, zone_id=p.zone_id)
        elif p.level == LeaderLevel.NATIONAL:
            q |= Q(level=LeaderLevel.NATIONAL)
    return qs.filter(q) if q else qs.none()


def case_rows(cases, limit=None):
    qs = cases.select_related("member", "ward", "district", "region")
    if limit:
        qs = qs[:limit]
    return [{
        "id": c.pk, "ref": c.reference, "subject": c.subject,
        "member": c.member.full_name, "member_no": c.member.membership_no,
        "category": c.get_category_display(),
        "urgency": c.get_urgency_display(), "urgent": c.urgency == "high",
        "status": c.get_status_display(), "badge": c.badge,
        "level": c.get_level_display(), "area": c.area_name,
        "days": c.days_at_level, "open": c.is_open,
        "date": c.created_at.strftime("%d/%m/%Y"),
    } for c in qs]


# ---------------------------------------------------------------------------
#  Dashibodi
# ---------------------------------------------------------------------------
def dashboard(user):
    """Takwimu za eneo lake pekee."""
    members = scope_members(user)
    cases = scope_cases(user)
    today = timezone.localdate()

    hai = members.filter(status=MemberStatus.ACTIVE).count()
    jumla = members.count()
    kuisha = members.filter(expires_on__isnull=False,
                            expires_on__lt=today).count()
    wazi = cases.filter(status__in=[CaseStatus.OPEN, CaseStatus.IN_PROGRESS,
                                    CaseStatus.ESCALATED]).count()
    haraka = cases.filter(urgency="high").exclude(
        status__in=[CaseStatus.RESOLVED, CaseStatus.CLOSED]).count()

    return {
        "kpis": [
            {"label": _("Wanachama Wangu"), "value": f"{jumla:,}",
             "icon": "users", "tint": "green",
             "note": _("Kwenye eneo lako")},
            {"label": _("Wanachama Hai"), "value": f"{hai:,}",
             "icon": "user-check", "tint": "navy",
             "note": f"{(hai * 100 // jumla) if jumla else 0}%"},
            {"label": _("Muda Umeisha"), "value": f"{kuisha:,}",
             "icon": "clock", "tint": "red" if kuisha else "gold",
             "note": _("Wanahitaji kuhuisha")},
            {"label": _("Matatizo Wazi"), "value": f"{wazi:,}",
             "icon": "alert", "tint": "gold" if wazi else "green",
             "note": _("Yanasubiri jibu lako")},
            {"label": _("Ya Haraka"), "value": f"{haraka:,}",
             "icon": "megaphone", "tint": "red" if haraka else "navy",
             "note": _("Yenye uzito wa juu")},
        ],
        "areas": areas_label(user),
        "level": top_level(user),
        "recent_cases": case_rows(cases.exclude(
            status__in=[CaseStatus.RESOLVED, CaseStatus.CLOSED]), limit=6),
        "breakdown": breakdown(user),
        "recent_members": [{
            "id": m.pk, "no": m.membership_no, "name": m.full_name,
            "phone": m.phone, "initials": _initials(m.full_name),
            "place": str(m.ward or m.district or "—"),
            "status": m.get_status_display(), "badge": _member_badge(m),
        } for m in members.select_related("ward", "district")
            .order_by("-created_at")[:6]],
    }


def _initials(name):
    parts = [p for p in (name or "").split() if p]
    return "".join(p[0].upper() for p in parts[:2]) or "?"


def _member_badge(m):
    if m.status == MemberStatus.ACTIVE:
        return "ok"
    if m.status == MemberStatus.EXPIRED:
        return "danger"
    return "warn"


def member_rows(user, q="", status="", area=None):
    """
    Orodha ya wanachama wa eneo lake, ikichujwa.

    `area` ni ("ward", 12) — kuchuja kwa eneo dogo lililobofywa kwenye
    mchanganuo. Ufinyu wa `scope_members` unabaki; hii inaongeza tu.
    """
    qs = scope_members(user).select_related("ward", "district", "region", "category")
    if area:
        field, value = area
        qs = qs.filter(**{f"{field}_id": value})
    if q:
        qs = qs.filter(Q(full_name__icontains=q) | Q(membership_no__icontains=q)
                       | Q(phone__icontains=q))
    if status:
        qs = qs.filter(status=status)
    return [{
        "id": m.pk, "no": m.membership_no or "—", "name": m.full_name,
        "phone": m.phone, "email": m.email,
        "category": m.category.name if m.category else "—",
        "place": " / ".join(str(x) for x in [m.ward, m.district] if x) or "—",
        "expires": m.expires_on.strftime("%d/%m/%Y") if m.expires_on else "—",
        "status": m.get_status_display(), "badge": _member_badge(m),
        "initials": _initials(m.full_name),
    } for m in qs.order_by("full_name")[:200]]


# ---------------------------------------------------------------------------
#  Mawasiliano
# ---------------------------------------------------------------------------
def leader_area(user):
    """
    Wadhifa wa juu kabisa na eneo lake — ndio unaotumika kutuma matangazo.

    Mtu mwenye wadhifa zaidi ya mmoja anatuma kwa niaba ya ule wa juu.
    """
    posts = active_posts(user)
    if not posts:
        return None
    return max(posts, key=lambda p: LEVEL_ORDER.index(p.level))


def broadcast_targets(user):
    """Wanachama watakaopokea tangazo lake."""
    return scope_members(user)


def broadcasts_for(user, limit=20):
    """Matangazo aliyoyatuma."""
    return Broadcast.objects.filter(sender=user).order_by("-created_at")[:limit]


def member_broadcasts(member, limit=20):
    """
    Matangazo yanayomhusu mwanachama — ya kata, wilaya, mkoa, kanda na taifa.

    Yanahesabiwa wakati wa kusoma, si kunakiliwa wakati wa kutuma. Kwa
    hiyo mwanachama mpya anaona ya nyuma, na aliyehama haoni ya kata
    aliyoiacha.
    """
    q = Q(level=LeaderLevel.NATIONAL)
    if member.ward_id:
        q |= Q(level=LeaderLevel.WARD, ward_id=member.ward_id)
    if member.district_id:
        q |= Q(level=LeaderLevel.DISTRICT, district_id=member.district_id)
    if member.region_id:
        q |= Q(level=LeaderLevel.REGION, region_id=member.region_id)
        if member.region.zone_id:
            q |= Q(level=LeaderLevel.ZONE, zone_id=member.region.zone_id)
    return Broadcast.objects.filter(q).select_related("sender").order_by("-created_at")[:limit]


def threads_for_leader(user, limit=50):
    """Mazungumzo ya wanachama wa eneo lake, kwa ngazi yake."""
    post = leader_area(user)
    qs = Thread.objects.select_related("member")
    if sees_everyone(user) and not post:
        qs = qs.filter(level=LeaderLevel.NATIONAL)
    else:
        f = member_filter(user)
        qs = qs.filter(level=post.level)
        if f is not None:
            from geo.scope import _prefix
            qs = qs.filter(_prefix(f, "member__"))
    return qs.annotate(n=Count("messages")).order_by("-last_at")[:limit]


# ---------------------------------------------------------------------------
#  Upande wa mwanachama
# ---------------------------------------------------------------------------
def my_leaders(member):
    """
    Viongozi wa mwanachama huyu, kutoka kata hadi taifa.

    Mwanachama anaambiwa "toa taarifa kwa kiongozi wako" — ni haki yake
    kujua huyo ni nani, na namba yake ya simu. Bila hii, ujumbe huo hauna
    maana.

    Waliomaliza muda hawaonyeshwi; `Leadership.is_active` inashughulikia hilo.
    """
    from geo.models import Leadership

    q = Q(level=LeaderLevel.NATIONAL)
    if member.ward_id:
        q |= Q(level=LeaderLevel.WARD, ward_id=member.ward_id)
    if member.district_id:
        q |= Q(level=LeaderLevel.DISTRICT, district_id=member.district_id)
    if member.region_id:
        q |= Q(level=LeaderLevel.REGION, region_id=member.region_id)
        if member.region.zone_id:
            q |= Q(level=LeaderLevel.ZONE, zone_id=member.region.zone_id)

    posts = (Leadership.objects.filter(q)
             .select_related("user", "ward", "district", "region", "zone"))
    out = []
    for p in posts:
        if not p.is_active:
            continue
        out.append({
            "level": p.level,
            "level_name": p.get_level_display(),
            "post": p.get_post_display(),
            "area": p.area_name,
            "name": p.user.get_full_name() or p.user.username,
            "phone": getattr(p.user, "phone", "") or "",
            "initials": _initials(p.user.get_full_name() or p.user.username),
        })
    # Kutoka chini kwenda juu — kiongozi wa kata ndiye wa kwanza kuonwa,
    # kwa sababu ndiye wa kwanza kuwasiliana naye.
    order = {lv: i for i, lv in enumerate(LEVEL_ORDER)}
    out.sort(key=lambda r: (order.get(r["level"], 99), r["post"]))
    return out


def member_threads(member):
    """Mazungumzo yote ya mwanachama, kwa kila ngazi."""
    return (Thread.objects.filter(member=member)
            .annotate(n=Count("messages")).order_by("-last_at"))


def open_thread(member, level=LeaderLevel.WARD, subject=""):
    """
    Fungua mazungumzo na ngazi husika, au rudisha yaliyopo.

    Mazungumzo ni kati ya mwanachama na NGAZI, si mtu binafsi — kiongozi
    akibadilika, yanaendelea badala ya kupotea naye.
    """
    thread = Thread.objects.filter(member=member, level=level).first()
    if thread is None:
        thread = Thread.objects.create(member=member, level=level,
                                       subject=subject[:160])
    return thread


# ---------------------------------------------------------------------------
#  Mchanganuo wa ngazi za juu
#
#  Kiongozi wa kata anafaidika na orodha bapa ya wanachama 40. Kiongozi wa
#  mkoa mwenye wanachama 500 kwenye wilaya 8 haifai — hawezi kujua wilaya
#  ipi inasuasua wala kata ipi haina kiongozi.
#
#  Kila ngazi inaona ngazi moja chini yake:
#      Wilaya -> kata zake     Mkoa -> wilaya zake
#      Kanda  -> mikoa yake    Taifa -> kanda zote
# ---------------------------------------------------------------------------
#: (ngazi ya kiongozi) -> (jina la ngazi ya chini, njia ya kufikia
#: mwanachama, njia ya kufikia tatizo)
BREAKDOWN = {
    LeaderLevel.DISTRICT: ("ward", "ward", "ward"),
    LeaderLevel.REGION: ("district", "district", "district"),
    LeaderLevel.ZONE: ("region", "region", "region"),
    LeaderLevel.NATIONAL: ("zone", "region__zone", "zone"),
}


def breakdown(user):
    """
    Mchanganuo wa maeneo yaliyo chini ya kiongozi.

    Hurudisha `None` kwa kiongozi wa kata — hana ngazi ya chini, na
    jedwali lisilo na safu haliongezi chochote.
    """
    level = top_level(user)
    spec = BREAKDOWN.get(level)
    if spec is None:
        return None

    label, member_path, case_path = spec
    members = scope_members(user)
    cases = scope_cases(user)
    today = timezone.localdate()

    # Hesabu zote kwa swali moja kwa kila kitu, si kwa kila eneo —
    # mkoa wenye wilaya 8 ungefanya maswali 24 badala ya matatu.
    counts = dict(members.values_list(f"{member_path}__id").annotate(
        n=Count("id")).values_list(f"{member_path}__id", "n"))
    expired = dict(members.filter(expires_on__lt=today)
                   .values_list(f"{member_path}__id").annotate(n=Count("id"))
                   .values_list(f"{member_path}__id", "n"))
    open_cases = dict(cases.exclude(
        status__in=[CaseStatus.RESOLVED, CaseStatus.CLOSED])
        .values_list(f"{case_path}__id").annotate(n=Count("id"))
        .values_list(f"{case_path}__id", "n"))

    areas = _areas_under(user, level)
    leaders = _leaders_by_area(areas, label)

    rows = []
    for a in areas:
        n = counts.get(a.pk, 0)
        rows.append({
            "id": a.pk, "name": str(a),
            "members": n,
            "expired": expired.get(a.pk, 0),
            "cases": open_cases.get(a.pk, 0),
            "leaders": leaders.get(a.pk, []),
            # Eneo lisilo na kiongozi ni tatizo la kiutawala, si la data.
            # Matatizo yake yatakwama hadi mtu awekwe.
            "no_leader": not leaders.get(a.pk),
            "share": round(n * 100 / max(counts and sum(counts.values()) or 1, 1)),
        })
    rows.sort(key=lambda r: (-r["cases"], -r["members"], r["name"]))
    return {"label": label, "rows": rows,
            "level_name": dict(LeaderLevel.choices).get(level, "")}


def _areas_under(user, level):
    """Maeneo ya ngazi moja chini ya kiongozi."""
    from geo.models import District, Region, Ward, Zone

    posts = active_posts(user)
    if level == LeaderLevel.DISTRICT:
        ids = [p.district_id for p in posts if p.district_id]
        return Ward.objects.filter(district_id__in=ids).select_related("district")
    if level == LeaderLevel.REGION:
        ids = [p.region_id for p in posts if p.region_id]
        return District.objects.filter(region_id__in=ids).select_related("region")
    if level == LeaderLevel.ZONE:
        ids = [p.zone_id for p in posts if p.zone_id]
        return Region.objects.filter(zone_id__in=ids)
    if level == LeaderLevel.NATIONAL:
        return Zone.objects.all()
    return []


def _leaders_by_area(areas, field):
    """Viongozi wa kila eneo, kwa swali moja."""
    from geo.models import Leadership

    ids = [a.pk for a in areas]
    out = {}
    qs = (Leadership.objects.filter(**{f"{field}_id__in": ids})
          .select_related("user"))
    for p in qs:
        if not p.is_active:
            continue
        out.setdefault(getattr(p, f"{field}_id"), []).append({
            "name": p.user.get_full_name() or p.user.username,
            "post": p.get_post_display(),
            "phone": getattr(p.user, "phone", "") or "",
        })
    return out


# ---------------------------------------------------------------------------
#  Vipengele vya mfumo vilivyochujwa kwa eneo la kiongozi
#
#  Kiongozi si afisa wa makao makuu, lakini anahitaji kujua yanayotokea
#  kwenye eneo lake — hasa ni nani hajalipa ada, kwa sababu kuhamasisha
#  ndiyo kazi yake ya msingi.
#
#  Vyote vinapita `scope_queryset`, kwa hiyo ufinyu ule ule unatumika.
# ---------------------------------------------------------------------------
def ada_rows(user, hali=""):
    """Ada za wanachama wa eneo lake."""
    from finance.models import Payment
    from geo.scope import scope_queryset

    qs = scope_queryset(user, Payment.objects.select_related(
        "member", "member__ward", "member__district"))
    if hali:
        qs = qs.filter(status=hali)
    return [{
        "id": p.pk, "receipt": p.receipt_no,
        "member": p.member.full_name if p.member else "—",
        "member_no": p.member.membership_no if p.member else "",
        "place": str(p.member.ward or p.member.district or "—") if p.member else "—",
        "amount": int(p.amount), "method": p.get_method_display(),
        "status": p.get_status_display(), "status_key": p.status,
        "badge": {"confirmed": "ok", "pending": "warn",
                  "failed": "danger", "cancelled": "muted"}.get(p.status, "muted"),
        "date": p.created_at.strftime("%d/%m/%Y"),
        "pending": p.status == "pending",
    } for p in qs.order_by("-created_at")[:200]]


def wasiolipa(user, limit=100):
    """
    Wanachama ambao muda wao umeisha au unakaribia kuisha.

    Hii ndiyo orodha yenye thamani kubwa kwa kiongozi — ndio watu wa
    kuwapigia simu.
    """
    today = timezone.localdate()
    karibu = today + timezone.timedelta(days=60)
    qs = (scope_members(user)
          .filter(expires_on__isnull=False, expires_on__lte=karibu)
          .select_related("ward", "district"))
    return [{
        "id": m.pk, "no": m.membership_no or "—", "name": m.full_name,
        "phone": m.phone, "initials": _initials(m.full_name),
        "place": str(m.ward or m.district or "—"),
        "expires": m.expires_on.strftime("%d/%m/%Y"),
        "days": (m.expires_on - today).days,
        "imeisha": m.expires_on < today,
    } for m in qs.order_by("expires_on")[:limit]]


def maombi_rows(user, limit=100):
    """
    Maombi mapya ya uanachama kutoka eneo lake.

    KUONA TU. Kuidhinisha ni kazi ya afisa wa usajili — kiongozi
    anawajua watu, lakini uamuzi wa kuwakubali ni wa makao makuu.
    """
    from members.models import Application

    from geo.scope import member_filter, sees_everyone
    qs = Application.objects.select_related("category", "ward", "district", "region")
    if not sees_everyone(user):
        posts = active_posts(user)
        if not posts:
            return []
        q = Q()
        for p in posts:
            if p.level == LeaderLevel.WARD and p.ward_id:
                q |= Q(ward_id=p.ward_id)
            elif p.level == LeaderLevel.DISTRICT and p.district_id:
                q |= Q(district_id=p.district_id)
            elif p.level == LeaderLevel.REGION and p.region_id:
                q |= Q(region_id=p.region_id)
            elif p.level == LeaderLevel.ZONE and p.zone_id:
                q |= Q(region__zone_id=p.zone_id)
        if not q:
            return []
        qs = qs.filter(q)
    return [{
        "ref": a.reference, "name": a.full_name, "phone": a.phone,
        "category": a.category.name if a.category else "—",
        "place": " / ".join(str(x) for x in [a.ward, a.district] if x) or "—",
        "status": a.get_status_display(), "badge": a.badge,
        "date": a.created_at.strftime("%d/%m/%Y"),
        "initials": _initials(a.full_name),
        "verified": getattr(a, "phone_verified", False),
    } for a in qs.order_by("-created_at")[:limit]]


def michango_rows(user, limit=150):
    """Michango ya wanachama wa eneo lake."""
    from finance.models import Contribution
    from geo.scope import scope_queryset

    qs = scope_queryset(user, Contribution.objects.select_related(
        "member", "fund").exclude(member__isnull=True))
    return [{
        "receipt": c.receipt_no, "member": c.member.full_name if c.member else "—",
        "amount": int(c.amount), "fund": c.fund.name if c.fund else "—",
        "purpose": c.get_purpose_display() if hasattr(c, "get_purpose_display") else c.purpose,
        "status": c.get_status_display(), "badge":
            {"confirmed": "ok", "pending": "warn"}.get(c.status, "muted"),
        "date": c.created_at.strftime("%d/%m/%Y"),
    } for c in qs.order_by("-created_at")[:limit]]


def msaada_rows(user, limit=100):
    """Maombi ya msaada kutoka wanachama wa eneo lake."""
    from geo.scope import scope_queryset
    from programs.models import AssistanceRequest

    qs = scope_queryset(user, AssistanceRequest.objects.select_related(
        "member", "kind" if hasattr(AssistanceRequest, "kind") else "member"))
    return [{
        "id": r.pk, "ref": getattr(r, "reference", "") or f"#{r.pk}",
        "member": r.member.full_name if r.member else "—",
        "phone": r.member.phone if r.member else "",
        "status": r.get_status_display() if hasattr(r, "get_status_display") else "",
        "badge": {"approved": "ok", "pending": "warn",
                  "rejected": "danger"}.get(getattr(r, "status", ""), "muted"),
        "date": r.created_at.strftime("%d/%m/%Y"),
        "amount": int(getattr(r, "amount", 0) or 0),
    } for r in qs.order_by("-created_at")[:limit]]


def can_touch_payment(user, payment):
    """
    Je, kiongozi huyu anaruhusiwa kuthibitisha malipo haya?

    Lazima mwanachama awe wa eneo lake. Bila ukaguzi huu, kiongozi
    angeweza kuthibitisha malipo ya mtu asiyemjua kwa kubadilisha URL.
    """
    if payment.member_id is None:
        return False
    from geo.scope import can_see_member
    return can_see_member(user, payment.member)
