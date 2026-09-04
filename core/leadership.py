"""
Maswali ya sehemu ya uongozi.

KANUNI: hakuna swali linalouliza database bila kupita `geo.scope`.
Kila kazi hapa inachukua `user` na kuchuja kwa maeneo yake. Kusahau
mara moja kunamaanisha kiongozi wa Kata A anaona wanachama wa Kata B.
"""
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.translation import gettext as _

from geo.models import LeaderLevel, LEVEL_ORDER, Leadership, next_level
from geo.scope import (active_posts, areas_label, member_filter, scope_members,
                       sees_everyone, top_level)
from members.models import Member, MemberStatus
from programs.models import Broadcast, Case, CaseStatus, Thread


def is_leader(user):
    """
    Je, mtu huyu ana sehemu ya uongozi?

    Inahitaji WADHIFA HALISI wa `Leadership`, si `sees_everyone` peke
    yake. Awali afisa wa usajili au wa malipo alifika `/uongozi/` kwa
    sababu jukumu lake linamruhusu kuona wanachama wote — lakini
    dashibodi ya uongozi si yake. Ana `/dashibodi/` na kurasa zake.

    Msimamizi mkuu anabaki na ufikiaji, kwa ajili ya kukagua.
    """
    return bool(active_posts(user)) or bool(getattr(user, "is_superuser", False))


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
    """
    Dashibodi inayolingana na KAZI ya ngazi husika.

    Ngazi si kichujio cha data pekee — ni kazi tofauti:

      * KATA anafanya kazi na WATU. Anampigia simu mwanachama,
        anamkumbusha ada. Orodha ya wanachama ndicho chombo chake.

      * WILAYA/MKOA/KANDA hawafanyi kazi na watu — wanafanya kazi na
        VIONGOZI walio chini yao. Kiongozi wa mkoa hawezi kumpigia
        kila mmoja wa wanachama 500; anahitaji kujua wilaya ipi
        inasuasua na kata ipi haina kiongozi.

      * TAIFA ni ngazi ya sera — ulinganisho wa kanda, si mtu mmoja.

    Ndiyo maana KPI na vipaumbele vinatofautiana hapa chini.
    """
    members = scope_members(user)
    cases = scope_cases(user)
    level = top_level(user)
    today = timezone.localdate()

    jumla = members.count()
    hai = members.filter(status=MemberStatus.ACTIVE).count()
    kuisha = members.filter(expires_on__isnull=False,
                            expires_on__lt=today).count()
    wazi = cases.filter(status__in=[CaseStatus.OPEN, CaseStatus.IN_PROGRESS,
                                    CaseStatus.ESCALATED]).count()
    haraka = cases.filter(urgency="high").exclude(
        status__in=[CaseStatus.RESOLVED, CaseStatus.CLOSED]).count()

    bd = breakdown(user)
    ctx = {
        "ticker": matangazo_ticker(user),
        "areas": areas_label(user),
        "level": level,
        "breakdown": bd,
        "is_field": level == LeaderLevel.WARD,
        "recent_cases": case_rows(cases.exclude(
            status__in=[CaseStatus.RESOLVED, CaseStatus.CLOSED]), limit=6),
    }

    if level == LeaderLevel.WARD:
        # Ngazi ya uwanjani: watu, si maeneo.
        ctx["kpis"] = [
            _kpi("Wanachama Wangu", jumla, "users", "green", "Kwenye kata yako"),
            _kpi("Wanachama Hai", hai, "user-check", "navy",
                 f"{(hai * 100 // jumla) if jumla else 0}%"),
            _kpi("Hawajalipa", kuisha, "clock", "red" if kuisha else "gold",
                 "Wanahitaji kupigiwa simu"),
            _kpi("Matatizo Wazi", wazi, "alert", "gold" if wazi else "green",
                 "Yanasubiri jibu lako"),
            _kpi("Ya Haraka", haraka, "megaphone", "red" if haraka else "navy",
                 "Yenye uzito wa juu"),
        ]
        ctx["recent_members"] = _member_cards(members)
    else:
        # Ngazi za usimamizi: maeneo na viongozi, si orodha bapa.
        rows = bd["rows"] if bd else []
        bila = sum(1 for r in rows if r["no_leader"])
        mbaya = max(rows, key=lambda r: r["cases"], default=None)
        ctx["kpis"] = [
            _kpi(f"Maeneo Yangu", len(rows), "map-pin", "navy",
                 bd["level_name"] if bd else ""),
            _kpi("Wanachama Wote", jumla, "users", "green",
                 f"Hai: {hai}"),
            _kpi("Hawana Kiongozi", bila, "user-plus",
                 "red" if bila else "green",
                 "Matatizo yao yanakuja kwako"),
            _kpi("Hawajalipa", kuisha, "clock", "gold" if kuisha else "green",
                 "Kwenye maeneo yako yote"),
            _kpi("Matatizo Kwangu", wazi, "alert", "gold" if wazi else "green",
                 f"Ya haraka: {haraka}"),
        ]
        ctx["worst"] = mbaya if mbaya and mbaya["cases"] else None
        ctx["recent_members"] = []
    return ctx


def _kpi(label, value, icon, tint, note=""):
    return {"label": _(label), "value": f"{value:,}", "icon": icon,
            "tint": tint, "note": _(note) if note else ""}


def _member_cards(qs, limit=6):
    return [{
        "id": m.pk, "no": m.membership_no, "name": m.full_name,
        "phone": m.phone, "initials": _initials(m.full_name),
        "place": str(m.ward or m.district or "—"),
        "status": m.get_status_display(), "badge": _member_badge(m),
    } for m in qs.select_related("ward", "district").order_by("-created_at")[:limit]]


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
            "post_key": p.post,
            "area": p.area_name,
            "name": p.user.get_full_name() or p.user.username,
            "phone": getattr(p.user, "phone", "") or "",
            "initials": _initials(p.user.get_full_name() or p.user.username),
        })
    # Kutoka chini kwenda juu — kiongozi wa kata ndiye wa kwanza kuonwa,
    # kwa sababu ndiye wa kwanza kuwasiliana naye.
    #
    # Ndani ya ngazi, MWENYEKITI anatangulia. Awali nilipanga kwa jina la
    # wadhifa kwa alfabeti, kwa hiyo "Katibu" ilitangulia "Mwenyekiti" —
    # na kitufe cha simu kikamfuata katibu badala ya mwenyekiti.
    order = {lv: i for i, lv in enumerate(LEVEL_ORDER)}
    rank = {"chair": 0, "secretary": 1, "treasurer": 2}
    out.sort(key=lambda r: (order.get(r["level"], 99),
                            rank.get(r["post_key"], 9)))
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


def viongozi_chini(user):
    """
    Viongozi walio chini ya kiongozi huyu, pamoja na utendaji wao.

    Hiki ndicho chombo kikuu cha ngazi za juu. Kiongozi wa mkoa hawezi
    kumpigia simu kila mmoja wa wanachama 500 — anafanya kazi kupitia
    wenyeviti wa wilaya. Anahitaji kujua nani anajibu na nani hajibu.

    `open_cases` ni matatizo yaliyo KWENYE ngazi ya kiongozi huyo bado —
    yaani asiyoyashughulikia wala kuyapandisha. Ndio kipimo cha
    utendaji kinachoeleweka zaidi.
    """
    level = top_level(user)
    spec = BREAKDOWN.get(level)
    if spec is None:
        return None

    label, member_path, case_path = spec
    sub = next_level_down(level)
    areas = list(_areas_under(user, level))
    ids = [a.pk for a in areas]

    members = scope_members(user)
    counts = dict(members.values_list(f"{member_path}__id").annotate(
        n=Count("id")).values_list(f"{member_path}__id", "n"))

    # Matatizo yaliyo kwenye ngazi ya chini — hayajapandishwa wala
    # kutatuliwa. Ndiyo yanayoonyesha nani hajibu.
    from programs.models import Case
    open_by_area = dict(
        Case.objects.filter(level=sub, **{f"{case_path}_id__in": ids})
        .exclude(status__in=[CaseStatus.RESOLVED, CaseStatus.CLOSED])
        .values_list(f"{case_path}__id").annotate(n=Count("id"))
        .values_list(f"{case_path}__id", "n"))

    leaders = _leaders_by_area(areas, label)

    rows = []
    for a in areas:
        wao = leaders.get(a.pk, [])
        rows.append({
            "area": str(a), "id": a.pk,
            "members": counts.get(a.pk, 0),
            "cases": open_by_area.get(a.pk, 0),
            "leaders": wao,
            "no_leader": not wao,
        })
    # Wasio na kiongozi kwanza, kisha wenye matatizo mengi.
    rows.sort(key=lambda r: (not r["no_leader"], -r["cases"], r["area"]))
    return {"rows": rows, "sub_name": dict(LeaderLevel.choices).get(sub, ""),
            "label": label}


def next_level_down(level):
    """Ngazi moja chini ya hii, au `None` ikiwa ni ya chini kabisa."""
    try:
        i = LEVEL_ORDER.index(level)
    except ValueError:
        return None
    return LEVEL_ORDER[i - 1] if i > 0 else None


# ---------------------------------------------------------------------------
#  Mawasiliano kati ya viongozi
# ---------------------------------------------------------------------------
def wenzangu(user):
    """
    Viongozi ambao mtu huyu anaweza kuwasiliana nao.

    Makundi matatu, kwa mpangilio wa matumizi:
      * WALIO CHINI  — anaowasimamia; ndio anaowaandikia mara nyingi
      * WENZANGU     — wa ngazi ile ile, eneo moja (mwenyekiti na katibu)
      * WALIO JUU    — anaowaripoti

    Hakuna kiongozi anayeweza kuandikia mtu wa mnyororo mwingine —
    mwenyekiti wa Kata A hawezi kumwandikia wa Wilaya B.
    """
    from geo.models import Leadership

    posts = active_posts(user)
    if not posts and not sees_everyone(user):
        return {"chini": [], "wenzangu": [], "juu": []}

    chini, wenza, juu = [], [], []
    seen = {user.pk}

    for p in posts:
        # Walio chini: maeneo ya ngazi moja chini ya eneo lake
        sub = next_level_down(p.level)
        if sub:
            for l in _leaders_in(sub, _under(p)):
                if l.user_id not in seen:
                    seen.add(l.user_id)
                    chini.append(_leader_card(l, "chini"))

        # Wenzangu: ngazi ile ile, eneo lile lile
        for l in Leadership.objects.filter(level=p.level, **_area_filter(p)) \
                .select_related("user", "ward", "district", "region", "zone"):
            if l.user_id not in seen and l.is_active:
                seen.add(l.user_id)
                wenza.append(_leader_card(l, "wenzangu"))

        # Walio juu: ngazi moja juu, eneo linalomjumuisha
        up = next_level(p.level)
        if up:
            for l in _leaders_above(up, p):
                if l.user_id not in seen:
                    seen.add(l.user_id)
                    juu.append(_leader_card(l, "juu"))

    # Mwenyekiti kwanza kwenye kila kundi.
    rank = {"chair": 0, "secretary": 1, "treasurer": 2}
    for lst in (chini, wenza, juu):
        lst.sort(key=lambda r: (rank.get(r["post_key"], 9), r["area"]))
    return {"chini": chini, "wenzangu": wenza, "juu": juu}


def _area_filter(post):
    """Kichujio cha eneo la wadhifa huu."""
    for f in ("ward", "district", "region", "zone"):
        if getattr(post, f"{f}_id", None):
            return {f"{f}_id": getattr(post, f"{f}_id")}
    return {}


def _under(post):
    """Maeneo ya ngazi moja chini ya wadhifa huu."""
    from geo.models import District, Region, Ward, Zone

    if post.level == LeaderLevel.DISTRICT and post.district_id:
        return Ward.objects.filter(district_id=post.district_id)
    if post.level == LeaderLevel.REGION and post.region_id:
        return District.objects.filter(region_id=post.region_id)
    if post.level == LeaderLevel.ZONE and post.zone_id:
        return Region.objects.filter(zone_id=post.zone_id)
    if post.level == LeaderLevel.NATIONAL:
        return Zone.objects.all()
    return []


def _leaders_in(level, areas):
    """Viongozi wa ngazi husika kwenye maeneo haya."""
    from geo.models import Leadership

    field = {LeaderLevel.WARD: "ward", LeaderLevel.DISTRICT: "district",
             LeaderLevel.REGION: "region", LeaderLevel.ZONE: "zone"}.get(level)
    if not field:
        return []
    ids = [a.pk for a in areas]
    return [l for l in Leadership.objects.filter(
        level=level, **{f"{field}_id__in": ids}).select_related(
        "user", "ward", "district", "region", "zone") if l.is_active]


def _leaders_above(level, post):
    """Viongozi wa ngazi ya juu wanaomsimamia mtu huyu."""
    from geo.models import Leadership

    qs = Leadership.objects.filter(level=level).select_related(
        "user", "ward", "district", "region", "zone")
    if level == LeaderLevel.DISTRICT and post.ward_id:
        qs = qs.filter(district_id=post.ward.district_id)
    elif level == LeaderLevel.REGION and post.district_id:
        qs = qs.filter(region_id=post.district.region_id)
    elif level == LeaderLevel.ZONE and post.region_id:
        qs = qs.filter(zone_id=post.region.zone_id)
    elif level != LeaderLevel.NATIONAL:
        return []
    return [l for l in qs if l.is_active]


def _leader_card(post, kundi):
    u = post.user
    return {
        "id": u.pk, "name": u.get_full_name() or u.username,
        "post": post.get_post_display(), "post_key": post.post,
        "level": post.get_level_display(),
        "area": post.area_name, "phone": getattr(u, "phone", "") or "",
        "initials": _initials(u.get_full_name() or u.username),
        "kundi": kundi,
    }


def chats_for(user):
    """Mazungumzo yake na viongozi wengine, mapya kwanza."""
    from django.db.models import Q as _Q
    from programs.models import Chat

    return (Chat.objects.filter(_Q(a=user) | _Q(b=user))
            .select_related("a", "b").order_by("-last_at"))


def can_chat(user, other):
    """Je, anaruhusiwa kuandikia kiongozi huyu?"""
    if sees_everyone(user) and active_posts(user):
        return True
    w = wenzangu(user)
    ids = {x["id"] for x in w["chini"] + w["wenzangu"] + w["juu"]}
    return other.pk in ids


def matangazo_ticker(user, limit=6):
    """
    Matangazo yanayomhusu kiongozi — ya mnyororo wake wote.

    Kiongozi wa kata anaona ya wilaya, mkoa, kanda na taifa. Ya kwake
    mwenyewe hayajumuishwi; anayajua tayari.

    Yanaonyeshwa kwa kuteleza juu ya dashibodi ili asiyakose — tangazo
    lililofichwa ndani ya menyu halisomwi.
    """
    from programs.models import Broadcast

    posts = active_posts(user)
    if not posts and not sees_everyone(user):
        return []

    q = Q(level=LeaderLevel.NATIONAL)
    mine = set()
    for p in posts:
        mine.add((p.level, getattr(p, f"{p.level}_id", None)))
        if p.ward_id:
            q |= Q(level=LeaderLevel.DISTRICT, district_id=p.ward.district_id)
            q |= Q(level=LeaderLevel.REGION, region_id=p.ward.district.region_id)
            if p.ward.district.region.zone_id:
                q |= Q(level=LeaderLevel.ZONE, zone_id=p.ward.district.region.zone_id)
        elif p.district_id:
            q |= Q(level=LeaderLevel.REGION, region_id=p.district.region_id)
            if p.district.region.zone_id:
                q |= Q(level=LeaderLevel.ZONE, zone_id=p.district.region.zone_id)
        elif p.region_id and p.region.zone_id:
            q |= Q(level=LeaderLevel.ZONE, zone_id=p.region.zone_id)

    rows = []
    for b in Broadcast.objects.filter(q).select_related("sender")[:limit * 2]:
        if (b.level, getattr(b, f"{b.level}_id", None)) in mine:
            continue          # yake mwenyewe
        rows.append({
            "id": b.pk, "subject": b.subject, "body": b.body,
            "sender": b.sender.get_full_name() or b.sender.username,
            "initials": _initials(b.sender.get_full_name() or b.sender.username),
            "level": b.get_level_display(), "area": b.area_name,
            "when": b.created_at,
        })
        if len(rows) >= limit:
            break
    return rows
