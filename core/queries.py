"""
Safu ya maswali (selectors).

Kila function hapa inarudisha muundo ULE ULE wa dict uliokuwa kwenye
`core/data/*`, lakini sasa data zinatoka database. Kwa hiyo templates
hazikubadilika hata kidogo.
"""
from collections import OrderedDict
from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.utils.translation import gettext, gettext as _

# ONYO: usitumie `_` kama variable ya kutupa hapa — inafunika gettext.
#       Tumia `_unused` badala yake.

from .data import giving as _g

from content.models import (Album, Announcement, Faq, Leader, MediaItem, Milestone,
                            News, Pillar, Service, SiteSetting, Verse)
from finance.models import (Account, Campaign, Contribution, Donor, Expense, Fund,
                            Payment, PaymentMethod, PaymentStatus, Project)
from geo.models import Branch, Region, Zone
from members.models import Application, ApplicationStatus, Category, Member, MemberStatus
from programs.models import (AssistanceRequest, Event, EventRegistration,
                             PointRule, PointTransaction)

MONTHS = ["Jan", "Feb", "Mac", "Apr", "Mei", "Jun", "Jul", "Ago", "Sep", "Okt", "Nov", "Des"]
MONTHS_SHORT_UP = ["JAN", "FEB", "MAC", "APR", "MEI", "JUN", "JUL", "AGO", "SEP", "OKT", "NOV", "DES"]

C = {"green": "#12864a", "navy": "#1b3b6f", "gold": "#d4af37", "purple": "#6d28d9",
     "teal": "#0891b2", "red": "#dc2626", "orange": "#ea580c", "mint": "#4cbd83",
     "slate": "#64748b", "blue": "#2563eb"}

#: Rangi za madaraja. Ni chelezo tu — rangi halisi inatoka `Category.colour`,
#: kwa hiyo daraja jipya likiongezwa admin halihitaji mabadiliko ya code.
CAT_COLOURS = {"Bronze": C["orange"], "Silver": C["slate"], "Gold": C["gold"],
               "Diamond": C["purple"], "Tanzanite": C["navy"]}


def cat_colour(category):
    """Rangi ya daraja: ile ya database kwanza, kisha chelezo."""
    return category.colour or CAT_COLOURS.get(category.name, C["green"])


# ===========================================================================
#  Msaada
# ===========================================================================
def tzs(n):
    return "TZS {:,}".format(int(n or 0))


def num(n):
    return "{:,}".format(int(n or 0))


def pct(part, whole, digits=1):
    if not whole:
        return "0"
    return f"{round(float(part) / float(whole) * 100, digits)}"


def delta(now, before):
    """Rudisha (asilimia, mwelekeo)."""
    if not before:
        return ("0%", "up")
    change = (float(now) - float(before)) / float(before) * 100
    return (f"{abs(round(change, 1))}%", "up" if change >= 0 else "down")


def monthly_series(qs, date_field, value_field=None, year=None):
    """Rudisha orodha ya thamani 12 (Jan..Des)."""
    year = year or timezone.localdate().year
    flt = {f"{date_field}__year": year}
    agg = Sum(value_field) if value_field else Count("id")
    rows = (qs.filter(**flt)
              .annotate(m=TruncMonth(date_field))
              .values("m").annotate(v=agg).order_by("m"))
    out = [0] * 12
    for r in rows:
        if r["m"]:
            out[r["m"].month - 1] = int(r["v"] or 0)
    return out


def page_meta(page, pages, per_page, total):
    """Taarifa za pagination kwa component ya pager (0 = mkato '...')."""
    start = (page - 1) * per_page + 1 if total else 0
    end = min(page * per_page, total)
    if pages <= 7:
        rng = list(range(1, pages + 1))
    elif page <= 4:
        rng = [1, 2, 3, 4, 5, 0, pages]
    elif page >= pages - 3:
        rng = [1, 0] + list(range(pages - 4, pages + 1))
    else:
        rng = [1, 0, page - 1, page, page + 1, 0, pages]
    return {"page_start": start, "page_end": end, "page_range": rng,
            "per_page": per_page}


def confirmed(qs):
    return qs.filter(status=PaymentStatus.CONFIRMED)


def _month_bounds(offset=0):
    today = timezone.localdate()
    first = today.replace(day=1)
    for _ in range(offset):
        first = (first - timedelta(days=1)).replace(day=1)
    nxt = (first + timedelta(days=32)).replace(day=1)
    return first, nxt


# ===========================================================================
#  MSIMAMIZI MKUU — TAIFA
# ===========================================================================
def national(year=None):
    today = timezone.localdate()
    year = year or today.year
    this_m, next_m = _month_bounds(0)
    prev_m, _unused = _month_bounds(1)

    members = Member.objects.all()
    total = members.count()
    total_prev = members.filter(joined_on__lt=this_m).count()
    new_this = members.filter(joined_on__gte=this_m).count()
    new_prev = members.filter(joined_on__gte=prev_m, joined_on__lt=this_m).count()
    pending = Application.objects.filter(status__in=[ApplicationStatus.PENDING,
                                                     ApplicationStatus.REVIEW]).count()

    pay = confirmed(Payment.objects.all())
    fees_month = pay.filter(paid_at__date__gte=this_m).aggregate(s=Sum("amount"))["s"] or 0
    fees_prev = pay.filter(paid_at__date__gte=prev_m,
                           paid_at__date__lt=this_m).aggregate(s=Sum("amount"))["s"] or 0
    contrib = confirmed(Contribution.objects.all())
    rev_year = ((pay.filter(paid_at__year=year).aggregate(s=Sum("amount"))["s"] or 0) +
                (contrib.filter(received_at__year=year).aggregate(s=Sum("amount"))["s"] or 0))
    points_year = PointTransaction.objects.filter(awarded_on__year=year)\
        .aggregate(s=Sum("points"))["s"] or 0

    d1, dir1 = delta(total, total_prev)
    d2, dir2 = delta(new_this, new_prev or 1)
    d4, dir4 = delta(fees_month, fees_prev)

    # -- Kategoria --
    cat_counts = {row["category_id"]: row["n"]
                  for row in members.values("category_id").annotate(n=Count("id"))}
    cat_rows = []
    for c in Category.objects.all():
        n = cat_counts.get(c.pk, 0)
        if n:
            cat_rows.append({"label": c.name, "value": n, "display": num(n),
                             "pct": pct(n, total), "color": cat_colour(c)})
    cat_rows.sort(key=lambda r: -r["value"])

    # -- Mikoa --
    region_counts = (members.values("region__name")
                     .annotate(n=Count("id")).order_by("-n"))
    top = [r for r in region_counts if r["region__name"]][:5]
    top_max = top[0]["n"] if top else 1
    top_regions = [{"name": r["region__name"], "value": r["n"], "display": num(r["n"]),
                    "pct": round(r["n"] / top_max * 100)} for r in top]

    # Hesabu zote kwa query MOJA badala ya moja kwa kila mkoa
    counts = {row["region_id"]: row["n"]
              for row in members.values("region_id").annotate(n=Count("id"))}
    regions = [{"name": r.name, "members": counts.get(r.pk, 0), "x": r.map_x, "y": r.map_y}
               for r in Region.objects.all()]

    # -- Mifuko --
    fund_totals = {row["fund_id"]: row["s"] for row in
                   contrib.filter(received_at__year=year)
                          .values("fund_id").annotate(s=Sum("amount"))}
    ada_total = pay.filter(paid_at__year=year).aggregate(s=Sum("amount"))["s"] or 0
    funds = []
    for f in Fund.objects.all()[:6]:
        amt = ada_total if f.code == "ada" else fund_totals.get(f.pk, 0)
        funds.append({"label": f.name, "value": tzs(amt), "icon": f.icon,
                      "tint": _fund_tint(f.code)})
    spent = Expense.objects.filter(spent_on__year=year).aggregate(s=Sum("amount"))["s"] or 0

    # -- Miradi --
    proj_rows = []
    labels = {"completed": ("Imekamilika", C["green"]), "ongoing": ("Inaendelea", C["gold"]),
              "paused": ("Imesimama", C["orange"]), "planned": ("Haijaanza", C["red"])}
    proj_counts = {row["status"]: row["n"] for row in
                   Project.objects.values("status").annotate(n=Count("id"))}
    proj_total = sum(proj_counts.values()) or 1
    for key, (label, colour) in labels.items():
        n = proj_counts.get(key, 0)
        proj_rows.append({"label": label, "value": n, "display": str(n),
                          "pct": pct(n, proj_total), "color": colour})

    return {
        "scope": "Tanzania Bara",
        "kpis": [
            {"label": "Wanachama Jumla", "value": num(total), "icon": "users", "tint": "green",
             "delta": d1, "dir": dir1, "note": "Ikilinganishwa na mwezi jana"},
            {"label": "Wanachama Wapya", "value": num(new_this), "icon": "user-plus", "tint": "navy",
             "delta": d2, "dir": dir2, "note": "Mwezi Huu"},
            {"label": "Maombi Yanayosubiri", "value": num(pending), "icon": "clock", "tint": "orange",
             "note": "Inasubiri idhini"},
            {"label": "Ada Zilizokusanywa (Mwezi Huu)", "value": tzs(fees_month), "icon": "wallet",
             "tint": "green", "money": True, "delta": d4, "dir": dir4,
             "note": "Ikilinganishwa na mwezi jana"},
            {"label": "Mapato ya Jumla (Mwaka Huu)", "value": tzs(rev_year), "icon": "chart-bar",
             "tint": "purple", "money": True, "note": _("Mwaka %(y)d") % {"y": year}},
            {"label": "Pointi Zilizotolewa (Mwaka Huu)", "value": num(points_year), "icon": "star",
             "tint": "gold", "note": _("Mwaka %(y)d") % {"y": year}},
        ],
        "members_month": {"labels": MONTHS,
                          "data": _cumulative(monthly_series(members, "joined_on", year=year), total)},
        "revenue_month": {"labels": MONTHS,
                          "data": monthly_series(pay, "paid_at", "amount", year)},
        "by_category": {"id": "chCat", "title": "Aina za Wanachama",
                        "center_value": num(total), "center_label": "Jumla", "rows": cat_rows},
        "top_regions": top_regions,
        "regions": regions,
        "activities": _recent_activity(),
        "quick_actions": {"title": "Quick Actions", "cols": 3, "items": [
            {"label": "Jumla ya Ripoti", "icon": "chart-bar", "tint": "green", "url": "/pakua/malipo/"},
            {"label": "Ripoti za Mikoa", "icon": "map", "tint": "navy", "url": "/pakua/mikoa/"},
            {"label": "Ripoti za Wilaya", "icon": "file", "tint": "purple", "url": "/pakua/wanachama/"},
            {"label": "Tuma SMS kwa Wote", "icon": "message", "tint": "teal", "url": "/ujumbe/"},
            {"label": "Tuma Email kwa Wote", "icon": "mail", "tint": "orange", "url": "/ujumbe/"},
            {"label": "Tangaza Habari", "icon": "megaphone", "tint": "gold", "url": "/mfumo/matangazo/mpya/"},
            {"label": "Ongeza Habari", "icon": "image", "tint": "green", "url": "/media/"},
            {"label": "Pakia Picha", "icon": "upload", "tint": "navy", "url": "/media/pakia/"},
            {"label": "Ongeza Matukio", "icon": "calendar", "tint": "red", "url": "/matukio/"},
        ]},
        "calendar_events": [
            {"d": e.start_at.strftime("%d"), "m": MONTHS_SHORT_UP[e.start_at.month - 1],
             "title": e.tx("title"), "venue": e.tx("venue"),
             "time": e.start_at.strftime("%I:%M %p")}
            for e in Event.objects.filter(start_at__gte=timezone.now()).order_by("start_at")[:5]
        ],
        "funds": funds,
        "fund_totals": [
            {"label": "Matumizi Jumla", "value": tzs(spent), "icon": "receipt",
             "tint": "red", "danger": True},
            {"label": "Salio la Mwaka", "value": tzs(rev_year - spent), "icon": "check-circle",
             "tint": "green"},
        ],
        "projects": {"id": "chProjects", "title": "Utekelezaji wa Miradi", "sub": f"({year})",
                     "center_value": str(Project.objects.count()),
                     "center_label": "Miradi Jumla", "rows": proj_rows},
        "media_news": [{"title": n.tx("title"), "date": n.published_on.strftime("%d %B %Y"),
                        "scene": n.scene} for n in News.objects.filter(is_published=True)[:3]],
        "zones": _zone_rows(members, year),
        "summary": [
            {"label": "Idadi ya Kanda", "value": num(Zone.objects.count()), "icon": "globe"},
            {"label": "Idadi ya Mikoa", "value": num(Region.objects.count()), "icon": "map"},
            {"label": "Idadi ya Wilaya", "value": num(_district_count()), "icon": "map-pin"},
            {"label": "Wanachama Hai", "value": num(members.filter(status=MemberStatus.ACTIVE).count()),
             "icon": "users"},
            {"label": "Wanachama Wapya (Mwezi)", "value": num(new_this), "icon": "user-plus"},
            {"label": "Ada Zilizokusanywa (Mwezi)", "value": tzs(fees_month), "icon": "wallet"},
        ],
    }


def _zone_rows(members, year):
    """Mchanganuo wa kila kanda kwa msimamizi wa taifa."""
    counts = {r["region__zone_id"]: r["n"] for r in
              members.values("region__zone_id").annotate(n=Count("id"))}
    fees = {r["member__region__zone_id"]: r["s"] for r in
            confirmed(Payment.objects.filter(paid_at__year=year))
            .values("member__region__zone_id").annotate(s=Sum("amount"))}
    cons = {r["member__region__zone_id"]: r["s"] for r in
            confirmed(Contribution.objects.filter(received_at__year=year))
            .values("member__region__zone_id").annotate(s=Sum("amount"))}
    apps = {r["region__zone_id"]: r["n"] for r in
            Application.objects.filter(status__in=[ApplicationStatus.PENDING,
                                                   ApplicationStatus.REVIEW])
            .values("region__zone_id").annotate(n=Count("id"))}
    top = max(counts.values()) if counts else 1
    rows = []
    for z in Zone.objects.select_related("coordinator").prefetch_related("regions"):
        n = counts.get(z.pk, 0)
        rows.append({
            "name": z.tx("name"), "code": z.code,
            "coordinator": (z.coordinator.get_full_name() if z.coordinator
                            else "—"),
            "office": z.office,
            "regions": z.regions.count(),
            "members": num(n), "value": n,
            "pct": round(n / (top or 1) * 100),
            "fees": tzs(fees.get(z.pk, 0)),
            "contributions": tzs(cons.get(z.pk, 0)),
            "pending": num(apps.get(z.pk, 0)),
        })
    rows.sort(key=lambda r: -r["value"])
    return rows


def _district_count():
    from geo.models import District
    return District.objects.count()


def _cumulative(series, total):
    """Geuza idadi ya kila mwezi kuwa jumla inayoongezeka."""
    out, running = [], max(total - sum(series), 0)
    for v in series:
        running += v
        out.append(running)
    return out


def _fund_tint(code):
    return {"ada": "green", "hiari": "navy", "zaka": "gold", "sadaqa": "purple",
            "waqf": "teal", "miradi": "orange"}.get(code, "green")


def _recent_activity(limit=5):
    items = []
    for m in Member.objects.order_by("-created_at")[:2]:
        items.append({"title": "Mwanachama mpya amejiunga",
                      "sub": gettext("Mkoa wa %(r)s") % {
                          "r": m.region.name if m.region else "—"},
                      "time": m.created_at.strftime("%I:%M %p"), "icon": "user-plus", "tint": "green"})
    for p in confirmed(Payment.objects.all()).order_by("-paid_at")[:1]:
        items.append({"title": "Malipo mapya yamepokelewa",
                      "sub": f"{tzs(p.amount)} kutoka {p.member.full_name}",
                      "time": p.paid_at.strftime("%I:%M %p"), "icon": "wallet", "tint": "navy"})
    for a in Application.objects.order_by("-created_at")[:1]:
        items.append({"title": "Maombi mapya ya uanachama",
                      "sub": gettext("Mkoa wa %(r)s") % {
                          "r": a.region.name if a.region else "—"},
                      "time": a.created_at.strftime("%I:%M %p"), "icon": "user-check", "tint": "purple"})
    for t in PointTransaction.objects.order_by("-created_at")[:1]:
        items.append({"title": "Pointi zimeongezwa",
                      "sub": gettext("Pointi %(n)s kwa %(name)s") % {
                          "n": num(t.points), "name": t.member.full_name},
                      "time": t.created_at.strftime("%I:%M %p"), "icon": "star", "tint": "gold"})
    return items[:limit]


# ===========================================================================
#  AFISA USAJILI
# ===========================================================================
def usajili(year=None, region_ids=None):
    today = timezone.localdate()
    year = year or today.year
    this_m, _unused = _month_bounds(0)
    prev_m, _unused = _month_bounds(1)
    apps = Application.objects.all()
    members_qs = Member.objects.all()
    if region_ids is not None:
        apps = apps.filter(region_id__in=region_ids)
        members_qs = members_qs.filter(region_id__in=region_ids)

    todays = apps.filter(created_at__date=today).count()
    month = apps.filter(created_at__date__gte=this_m).count()
    prev = apps.filter(created_at__date__gte=prev_m, created_at__date__lt=this_m).count()
    approved = apps.filter(status=ApplicationStatus.APPROVED).count()
    pending = apps.filter(status__in=[ApplicationStatus.PENDING, ApplicationStatus.REVIEW]).count()
    rejected = apps.filter(status=ApplicationStatus.REJECTED).count()
    total_apps = apps.count() or 1
    d, dr = delta(month, prev)

    members = members_qs
    from members.models import Card
    return {
        "kpis": [
            {"label": "Maombi Leo", "value": num(todays), "icon": "users", "tint": "green",
             "note": "ikilinganishwa na jana"},
            {"label": "Maombi Haya Mwezi", "value": num(month), "icon": "file", "tint": "navy",
             "delta": d, "dir": dr, "note": "mwezi jana"},
            {"label": "Maombi Yaliyopitishwa", "value": num(approved), "icon": "clock", "tint": "gold",
             "note": "mwezi jana"},
            {"label": "Maombi Yanayosubiri", "value": num(pending), "icon": "clock", "tint": "purple",
             "note": "mwezi jana"},
            {"label": "Maombi Yaliyoakataliwa", "value": num(rejected), "icon": "check-circle",
             "tint": "teal", "note": "mwezi jana"},
        ],
        "steps": [
            {"n": 1, "label": "Taarifa Binafsi", "state": "is-current"},
            {"n": 2, "label": "Taarifa za Mawasiliano", "state": ""},
            {"n": 3, "label": "Taarifa za Uanachama", "state": ""},
            {"n": 4, "label": "Malipo", "state": ""},
            {"n": 5, "label": "Ukaguzi & Uthibitisho", "state": ""},
        ],
        "step_help": [
            {"n": 1, "title": "Taarifa Binafsi", "text": "Jaza taarifa zako binafsi"},
            {"n": 2, "title": "Taarifa za Mawasiliano", "text": "Jaza anuani na mawasiliano"},
            {"n": 3, "title": "Taarifa za Uanachama", "text": "Chagua aina ya uanachama"},
            {"n": 4, "title": "Malipo", "text": "Rekodi malipo ya ada"},
            {"n": 5, "title": "Ukaguzi & Uthibitisho", "text": "Thibitisha na kamilisha usajili"},
        ],
        "summary": [
            {"label": "Jumla ya Wanachama", "value": num(members.count()), "icon": "users", "tint": "green"},
            {"label": "Wanachama Hai", "value": num(members.filter(status=MemberStatus.ACTIVE).count()),
             "icon": "check-circle", "tint": "green"},
            {"label": "Wanachama Waliositishwa",
             "value": num(members.filter(status=MemberStatus.SUSPENDED).count()),
             "icon": "x-circle", "tint": "gold"},
            {"label": "Kadi Zilizotolewa", "value": num(Card.objects.filter(is_active=True).count()),
             "icon": "id-card", "tint": "navy"},
            {"label": "Kadi Zinazosubiri", "value": num(Card.objects.filter(printed=False).count()),
             "icon": "clock", "tint": "orange"},
        ],
        "recent": [
            {"initials": _initials(a.full_name), "name": a.full_name,
             "place": f"{a.region.name if a.region else '—'} - {a.district.name if a.district else '—'}",
             "status": a.get_status_display(), "badge": a.badge,
             "time": a.created_at.strftime("%I:%M %p")}
            for a in apps.order_by("-created_at")[:5]
        ],
        "apps_month": {"labels": MONTHS, "data": monthly_series(apps, "created_at", year=year)},
        "apps_status": {"id": "chAppStatus", "title": "Hali ya Maombi", "sub": f"({year})",
                        "center_value": num(total_apps), "center_label": "Jumla", "rows": [
                            {"label": "Imepitishwa", "value": approved, "display": num(approved),
                             "pct": pct(approved, total_apps), "color": C["green"]},
                            {"label": "Inasubiri", "value": pending, "display": num(pending),
                             "pct": pct(pending, total_apps), "color": C["gold"]},
                            {"label": "Imekataliwa", "value": rejected, "display": num(rejected),
                             "pct": pct(rejected, total_apps), "color": C["red"]},
                        ]},
        "cards_month": {"labels": MONTHS,
                        "data": monthly_series(Card.objects.all(), "issued_on", year=year)},
        "actions": [
            {"label": "Sajili Mwanachama", "icon": "user-plus", "tint": "green", "url": "/usajili/"},
            {"label": "Maombi Mapya", "icon": "file", "tint": "navy", "url": "/maombi/"},
            {"label": "Idhinisha Maombi", "icon": "check-circle", "tint": "green", "url": "/maombi/"},
            {"label": "Rekodi Malipo", "icon": "wallet", "tint": "orange", "url": "/malipo/"},
            {"label": "Chapisha Kadi", "icon": "id-card", "tint": "purple", "url": "/mfumo/kadi/"},
            {"label": "Tengeneza Ripoti", "icon": "chart-bar", "tint": "teal", "url": "/pakua/wanachama/"},
            {"label": "Tuma SMS", "icon": "message", "tint": "navy", "url": "/ujumbe/"},
            {"label": "Tuma Email", "icon": "mail", "tint": "gold", "url": "/ujumbe/"},
        ],
        "categories": Category.objects.filter(is_selectable=True),
        "regions_list": Region.objects.all(),
    }


def _initials(full_name):
    parts = [p for p in (full_name or "").split() if p]
    if not parts:
        return "??"
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()


# ===========================================================================
#  AFISA MALIPO YA ADA
# ===========================================================================
def malipo(page=1, per_page=10, filters=None, year=None, region_ids=None):
    today = timezone.localdate()
    year = year or today.year
    this_m, _unused = _month_bounds(0)
    all_pay = Payment.objects.select_related("member", "member__category")
    members = Member.objects.all()
    if region_ids is not None:
        all_pay = all_pay.filter(member__region_id__in=region_ids)
        members = members.filter(region_id__in=region_ids)
    f = filters or {}
    if f.get("q"):
        all_pay = all_pay.filter(Q(member__full_name__icontains=f["q"]) |
                                 Q(member__membership_no__icontains=f["q"]) |
                                 Q(receipt_no__icontains=f["q"]) |
                                 Q(reference__icontains=f["q"]))
    if f.get("status"):
        all_pay = all_pay.filter(status=f["status"])
    if f.get("method"):
        all_pay = all_pay.filter(method=f["method"])
    if f.get("from"):
        all_pay = all_pay.filter(paid_at__date__gte=f["from"])
    if f.get("to"):
        all_pay = all_pay.filter(paid_at__date__lte=f["to"])
    ok = confirmed(all_pay)
    total_rows = all_pay.count()
    pages = max((total_rows + per_page - 1) // per_page, 1)
    page = min(max(page, 1), pages)          # bana ndani ya mipaka

    today_amt = ok.filter(paid_at__date=today).aggregate(s=Sum("amount"))["s"] or 0
    today_n = ok.filter(paid_at__date=today).count()
    month_amt = ok.filter(paid_at__date__gte=this_m).aggregate(s=Sum("amount"))["s"] or 0
    month_n = ok.filter(paid_at__date__gte=this_m).count()
    year_amt = ok.filter(paid_at__year=year).aggregate(s=Sum("amount"))["s"] or 0
    target = Decimal("500000000")
    missed = all_pay.filter(status=PaymentStatus.FAILED)
    missed_amt = missed.aggregate(s=Sum("amount"))["s"] or 0
    total_n = all_pay.count() or 1
    conf_rate = round(ok.count() / total_n * 100, 1)

    # -- kwa kategoria --
    cat_rows = []
    for c in Category.objects.all():
        amt = ok.filter(member__category=c).aggregate(s=Sum("amount"))["s"] or 0
        if amt:
            cat_rows.append({"label": c.name, "value": int(amt), "display": tzs(amt),
                             "color": cat_colour(c)})
    tot_cat = sum(r["value"] for r in cat_rows) or 1
    for r in cat_rows:
        r["pct"] = pct(r["value"], tot_cat)

    # -- hali --
    status_rows = []
    for key, label, colour in [(PaymentStatus.CONFIRMED, "Yaliyolipwa", C["green"]),
                               (PaymentStatus.FAILED, "Yaliyokosekana", C["red"]),
                               (PaymentStatus.PENDING, "Yanasubiri Uthibitisho", C["slate"]),
                               (PaymentStatus.CANCELLED, "Yameghairiwa", C["gold"])]:
        n = all_pay.filter(status=key).count()
        status_rows.append({"label": label, "value": n, "display": num(n),
                            "pct": pct(n, total_n), "color": colour})

    # -- vyanzo --
    src_rows = (ok.filter(paid_at__date__gte=this_m).values("method")
                .annotate(s=Sum("amount")).order_by("-s"))
    src_total = sum(r["s"] or 0 for r in src_rows) or 1
    method_colour = {"bank": C["navy"], "mpesa": C["green"], "tigo": C["blue"],
                     "airtel": C["red"], "cash": C["slate"]}
    from finance.models import PaymentMethod
    labels = dict(PaymentMethod.choices)
    sources = [{"label": str(labels.get(r["method"], r["method"])), "value": tzs(r["s"]),
                "pct": round(float(r["s"] or 0) / float(src_total) * 100, 1),
                "color": method_colour.get(r["method"], C["slate"])} for r in src_rows[:5]]

    # -- table --
    start = (page - 1) * per_page
    rows = []
    for i, p in enumerate(all_pay.order_by("-paid_at")[start:start + per_page], start=start + 1):
        rows.append({
            "n": i, "id": p.pk, "member_id": p.member_id,
            "no": p.member.membership_no, "name": p.member.full_name,
            "cat": p.member.category.name, "year": p.year, "amount": num(p.amount),
            "date": p.paid_at.strftime("%d/%m/%Y %I:%M %p"), "method": p.method_label,
            "status": p.get_status_display(), "badge": p.badge, "receipt": p.receipt_no,
            "pending": p.status == PaymentStatus.PENDING,
        })

    missed_rows = (missed.values("member__region__name")
                   .annotate(s=Sum("amount")).order_by("-s")[:5])

    return {
        "kpis": [
            {"label": "Jumla ya Wanachama", "value": num(members.count()), "icon": "users",
             "tint": "green", "sub_label": "Wanachama Hai",
             "sub_value": num(members.filter(status=MemberStatus.ACTIVE).count())},
            {"label": "Ada Zilizokusanywa Leo", "value": tzs(today_amt), "icon": "cash",
             "tint": "navy", "money": True, "sub_label": "Idadi ya Malipo", "sub_value": num(today_n)},
            {"label": "Mapato ya Mwezi Huu", "value": tzs(month_amt), "icon": "chart-line",
             "tint": "green", "money": True, "sub_label": "Malipo Yenye Uthibitisho",
             "sub_value": num(month_n)},
            {"label": "Mapato ya Mwaka Huu", "value": tzs(year_amt), "icon": "coins",
             "tint": "gold", "money": True, "sub_label": "Lengo la Mwaka", "sub_value": tzs(target),
             "gauge": min(round(float(year_amt) / float(target) * 100), 100)},
            {"label": "Malipo Yaliyokosekana", "value": tzs(missed_amt), "icon": "clock",
             "tint": "purple", "money": True, "sub_label": "Idadi", "sub_value": num(missed.count())},
            {"label": "Malipo Yaliyothibitishwa", "value": f"{conf_rate}%", "icon": "check-circle",
             "tint": "teal", "sub_label": "Kiwango cha Uthibitisho", "sub_value": "Mzuri"},
        ],
        "revenue_month": {"labels": MONTHS, "data": monthly_series(ok, "paid_at", "amount", year)},
        "by_category": {"id": "chPayCat", "title": "Malipo kwa Aina ya Uanachama",
                        "center_value": "", "center_label": "", "rows": cat_rows},
        "status_mix": {"id": "chPayStatus", "title": "Hali ya Malipo", "sub": "(Mwezi Huu)",
                       "center_value": "", "center_label": "", "rows": status_rows},
        "sources": sources, "sources_total": tzs(src_total),
        "records": rows,
        "page": page, "pages": pages, "total_records": total_rows,
        **page_meta(page, pages, per_page, total_rows),
        "missed": [{"n": i, "label": r["member__region__name"] or "—", "value": tzs(r["s"])}
                   for i, r in enumerate(missed_rows, 1)],
        "missed_total": tzs(missed_amt),
        "statuses": PaymentStatus.choices, "methods": PaymentMethod.choices,
        "year": year,
        "suggestions": [
            {"label": "Tuma Kikumbusho kwa Waliokosekana", "icon": "bell", "tint": "gold", "url": "/ujumbe/"},
            {"label": "Tengeneza Ripoti ya Malipo", "icon": "file", "tint": "navy", "url": "/pakua/malipo/"},
            {"label": "Rekodi Malipo Mpya", "icon": "plus", "tint": "green", "url": "/malipo/"},
        ],
    }


# ===========================================================================
#  AFISA MICHANGO
# ===========================================================================
def michango(page=1, per_page=10, filters=None, year=None, region_ids=None):
    year = year or timezone.localdate().year
    all_c = Contribution.objects.select_related("fund", "member", "donor", "project")
    if region_ids is not None:
        all_c = all_c.filter(member__region_id__in=region_ids)
    f = filters or {}
    if f.get("q"):
        all_c = all_c.filter(Q(donor_name__icontains=f["q"]) |
                             Q(member__full_name__icontains=f["q"]) |
                             Q(donor__name__icontains=f["q"]) |
                             Q(receipt_no__icontains=f["q"]))
    if f.get("fund"):
        all_c = all_c.filter(fund_id=f["fund"])
    if f.get("status"):
        all_c = all_c.filter(status=f["status"])
    if f.get("from"):
        all_c = all_c.filter(received_at__date__gte=f["from"])
    if f.get("to"):
        all_c = all_c.filter(received_at__date__lte=f["to"])
    ok = confirmed(all_c).filter(received_at__year=year)
    total_rows = all_c.count()
    pages = max((total_rows + per_page - 1) // per_page, 1)
    page = min(max(page, 1), pages)
    total = ok.aggregate(s=Sum("amount"))["s"] or 0

    def fund_total(code):
        return ok.filter(fund__code=code).aggregate(s=Sum("amount"))["s"] or 0

    hiari, zaka, sadaqa, waqf = (fund_total("hiari"), fund_total("zaka"),
                                 fund_total("sadaqa"), fund_total("waqf"))
    verified = total
    tint = {"hiari": "navy", "zaka": "purple", "sadaqa": "orange", "waqf": "teal"}

    type_rows = []
    for f in Fund.objects.exclude(code="ada")[:5]:
        amt = fund_total(f.code)
        if amt:
            type_rows.append({"label": f.name, "value": int(amt),
                              "display": f"{pct(amt, total)}%", "pct": None,
                              "color": f.colour, "note": tzs(amt)})

    region_rows = (ok.values("member__region__name").annotate(s=Sum("amount"))
                   .exclude(member__region__name=None).order_by("-s")[:5])
    rmax = region_rows[0]["s"] if region_rows else 1
    by_region = [{"name": r["member__region__name"], "display": tzs(r["s"]),
                  "pct": round(float(r["s"]) / float(rmax) * 100)} for r in region_rows]

    proj_rows = (ok.values("project_id").annotate(s=Sum("amount"))
                 .exclude(project_id=None).order_by("-s")[:5])
    proj_names = {p_.pk: p_.tx("title") for p_ in
                  Project.objects.filter(pk__in=[r["project_id"] for r in proj_rows])}
    by_project = [{"n": i, "label": proj_names.get(r["project_id"], "—"),
                   "value": tzs(r["s"])} for i, r in enumerate(proj_rows, 1)]

    start = (page - 1) * per_page
    records = []
    badge_of = {"hiari": "green", "zaka": "purple", "sadaqa": "orange", "waqf": "teal"}
    for i, c in enumerate(all_c.order_by("-received_at")[start:start + per_page], start=start + 1):
        records.append({
            "n": i, "id": c.pk, "name": c.display_name, "receipt": c.receipt_no,
            "pending": c.status == PaymentStatus.PENDING,
            "no": c.member.membership_no if c.member else "—",
            "type": c.fund.name, "badge": badge_of.get(c.fund.code, "green"),
            "amount": num(c.amount),
            "project": c.project.tx("title") if c.project else (c.note or "Uendeshaji wa Jumla"),
            "date": c.received_at.strftime("%d/%m/%Y %I:%M %p"),
            "method": c.bank_name or c.get_method_display(),
        })

    targets, t_target, t_actual = [], Decimal(0), Decimal(0)
    for f in Fund.objects.exclude(code="ada")[:5]:
        amt = fund_total(f.code)
        tgt = f.annual_target or Decimal(1)
        targets.append({"label": f.name, "target": num(tgt), "actual": num(amt),
                        "pct": round(float(amt) / float(tgt) * 100, 1)})
        t_target += tgt
        t_actual += amt

    return {
        "kpis": [
            {"label": "Jumla ya Michango", "value": tzs(total), "icon": "users", "tint": "green",
             "money": True, "note": _("Mwaka %(y)d") % {"y": year}},
            {"label": "Michango ya Hiari", "value": tzs(hiari), "icon": "hand-heart", "tint": "navy",
             "money": True, "note": _("Mwaka %(y)d") % {"y": year}},
            {"label": "Zaka", "value": tzs(zaka), "icon": "user", "tint": "purple",
             "money": True, "note": _("Mwaka %(y)d") % {"y": year}},
            {"label": "Sadaqa", "value": tzs(sadaqa), "icon": "gift", "tint": "orange",
             "money": True, "note": _("Mwaka %(y)d") % {"y": year}},
            {"label": "Waqf", "value": tzs(waqf), "icon": "mosque", "tint": "teal",
             "money": True, "note": _("Mwaka %(y)d") % {"y": year}},
            {"label": "Michango iliyothibitishwa", "value": tzs(verified), "icon": "check-circle",
             "tint": "green", "money": True, "note": "Asilimia",
             "big_note": f"{pct(confirmed(all_c).count(), all_c.count() or 1)}%"},
        ],
        "by_month": {"labels": MONTHS,
                     "data": monthly_series(confirmed(all_c), "received_at", "amount", year)},
        "by_type": {"id": "chDonType", "title": "Michango kwa Aina", "sub": _("(Mwaka %(y)d)") % {"y": year},
                    "center_value": "", "center_label": "", "rows": type_rows},
        "by_region": by_region, "by_project": by_project, "records": records,
        "page": page, "pages": pages, "total_records": total_rows,
        **page_meta(page, pages, per_page, total_rows),
        "targets": targets,
        "statuses": PaymentStatus.choices, "year": year,
        "funds_list": Fund.objects.exclude(code="ada"),
        "targets_total": {"label": "Jumla", "target": num(t_target), "actual": num(t_actual),
                          "pct": round(float(t_actual) / float(t_target or 1) * 100, 1)},
        "actions": [
            {"label": "Rekodi Mchango", "icon": "plus", "tint": "green", "url": "/michango/"},
            {"label": "Tafuta Mchangiaji", "icon": "search", "tint": "navy", "url": "/michango/"},
            {"label": "Tengeneza Risiti", "icon": "receipt", "tint": "purple", "url": "/malipo/"},
            {"label": "Tuma Shukrani", "icon": "mail", "tint": "orange", "url": "/ujumbe/"},
            {"label": "Ripoti za Michango", "icon": "chart-bar", "tint": "teal", "url": "/pakua/michango/"},
        ],
    }


# ===========================================================================
#  WADAU NA WAHISANI
# ===========================================================================
def wadau(year=None):
    year = year or timezone.localdate().year
    this_m, _unused = _month_bounds(0)
    prev_m, _unused = _month_bounds(1)
    ok = confirmed(Contribution.objects.all())
    total_all = ok.aggregate(s=Sum("amount"))["s"] or 0
    month = ok.filter(received_at__date__gte=this_m).aggregate(s=Sum("amount"))["s"] or 0
    prev = ok.filter(received_at__date__gte=prev_m,
                     received_at__date__lt=this_m).aggregate(s=Sum("amount"))["s"] or 0
    d, dr = delta(month, prev)
    partners = Donor.objects.filter(is_partner=True, is_active=True).count()
    donors = Donor.objects.filter(is_active=True).count()
    campaigns = Campaign.objects.filter(is_active=True)
    setting = SiteSetting.get()
    goal = setting.fundraising_target or Decimal(1)
    raised_year = ok.filter(received_at__year=year).aggregate(s=Sum("amount"))["s"] or 0
    goal_pct = round(float(raised_year) / float(goal) * 100, 2)

    fund_totals = {row["fund_id"]: row["s"]
                   for row in ok.values("fund_id").annotate(s=Sum("amount"))}
    type_rows = []
    for f in Fund.objects.exclude(code="ada"):
        amt = fund_totals.get(f.pk, 0)
        if amt:
            type_rows.append({"label": f.name, "value": int(amt),
                              "display": f"{pct(amt, total_all, 0)}%", "color": f.colour})
    type_rows.sort(key=lambda r: -r["value"])
    type_rows = type_rows[:7]

    # Wahisani watano wakubwa — query moja, si moja kwa kila mhisani
    top = (Donor.objects.annotate(
                given=Sum("contributions__amount",
                          filter=Q(contributions__status=PaymentStatus.CONFIRMED)))
           .order_by("-given")[:5])

    reg_counts = {row["member__region_id"]: row["n"]
                  for row in ok.values("member__region_id").annotate(n=Count("id"))}
    regions = [{"name": r.name, "members": reg_counts.get(r.pk, 0),
                "x": r.map_x, "y": r.map_y} for r in Region.objects.all()]
    reg_rows = (ok.values("member__region__name").annotate(s=Sum("amount"))
                .exclude(member__region__name=None).order_by("-s")[:5])
    reg_total = sum(r["s"] for r in reg_rows) or 1

    return {
        "kpis": [
            {"label": "Jumla ya Wadau Waliosajiliwa", "value": num(partners), "icon": "users",
             "tint": "green", "note": "Wadau hai"},
            {"label": "Jumla ya Wahisani", "value": num(donors), "icon": "heart", "tint": "navy",
             "note": "Wahisani hai"},
            {"label": "Jumla ya Michango Iliyopokelewa", "value": tzs(total_all), "icon": "wallet",
             "tint": "teal", "money": True, "note": "Takwimu zote"},
            {"label": "Michango ya Mwezi Huu", "value": tzs(month), "icon": "calendar",
             "tint": "gold", "money": True, "delta": d, "dir": dr, "note": "Mwezi Huu"},
            {"label": "Kampeni Zinazoendelea", "value": num(campaigns.count()), "icon": "target",
             "tint": "green", "note": "Kampeni hai"},
            {"label": "Asilimia ya Lengo Lililofikiwa", "value": f"{round(goal_pct)}%",
             "icon": "trophy", "tint": "gold", "progress": min(round(goal_pct), 100)},
        ],
        "trend": {"labels": MONTHS, "data": monthly_series(ok, "received_at", "amount", year)},
        "by_type": {"id": "chDonorType", "title": "Mgawanyo wa Michango kwa Aina",
                    "center_value": tzs(total_all).replace("TZS ", "TZS "),
                    "center_label": "", "rows": type_rows},
        "campaigns": [{"title": c.tx("title"), "raised": tzs(c.raised()),
                       "goal": num(c.target_amount), "pct": c.progress(),
                       "bar": c.progress_bar(),
                       "days": _("Siku %(n)d") % {"n": c.days_left()}, "scene": c.scene}
                      for c in campaigns[:4]],
        "top_donors": [{"n": i, "name": d_.name, "value": tzs(d_.given or 0)}
                       for i, d_ in enumerate(top, 1)],
        "recent": [{"name": c.display_name, "type": c.fund.name, "value": tzs(c.amount),
                    "date": c.received_at.strftime("%d/%m/%Y - %I:%M %p"), "tint": "red"}
                   for c in ok.order_by("-received_at")[:5]],
        "regions": regions,
        "region_share": [{"name": r["member__region__name"],
                          "pct": round(float(r["s"]) / float(reg_total) * 100)} for r in reg_rows],
        "alerts": _alerts(),
        "year_goal": {"goal": tzs(goal), "raised": tzs(raised_year), "pct": goal_pct},
        "actions": [
            {"label": "Sajili Mdau Mpya", "icon": "user-plus", "tint": "green", "url": "/mfumo/wahisani/mpya/"},
            {"label": "Sajili Mhisani", "icon": "heart", "tint": "navy", "url": "/mfumo/wahisani/mpya/"},
            {"label": "Rekodi Mchango", "icon": "wallet", "tint": "teal", "url": "/michango/"},
            {"label": "Fungua Kampeni Mpya", "icon": "target", "tint": "gold", "url": "/mfumo/kampeni/mpya/"},
            {"label": "Tengeneza Risiti", "icon": "receipt", "tint": "purple", "url": "/malipo/"},
            {"label": "Tuma Barua ya Shukrani", "icon": "mail", "tint": "orange", "url": "/ujumbe/"},
            {"label": "Pakua Ripoti", "icon": "download", "tint": "navy", "url": "/pakua/wahisani/"},
        ],
    }


def _alerts():
    """Arifa za wadau. Maandishi yanapitia gettext ili yatafsirike."""
    out = []
    pend = Contribution.objects.filter(status=PaymentStatus.PENDING).count()
    if pend:
        out.append({"text": _("Michango %(n)d inasubiri kuthibitishwa.") % {"n": pend},
                    "time": "Sasa hivi", "icon": "file", "tint": "navy"})
    for c in Campaign.objects.filter(is_active=True).order_by("end_date")[:1]:
        out.append({"text": _("Kampeni ya %(title)s itamalizika baada ya siku %(days)d.")
                            % {"title": c.tx("title"), "days": c.days_left()},
                    "time": "Leo", "icon": "alert", "tint": "gold"})
    for d_ in Donor.objects.order_by("-created_at")[:1]:
        out.append({"text": _("Mdau mpya amesajiliwa: %(name)s") % {"name": d_.name},
                    "time": d_.created_at.strftime("%d/%m/%Y"), "icon": "user-plus", "tint": "green"})
    today_ok = confirmed(Contribution.objects.all()).filter(
        received_at__date=timezone.localdate()).count()
    out.append({"text": _("Michango %(n)d imethibitishwa leo.") % {"n": today_ok},
                "time": "Leo", "icon": "check-circle", "tint": "green"})
    return out[:5]


# ===========================================================================
#  MATUKIO
# ===========================================================================
def matukio(month_key=None, year=None, region_ids=None):
    now = timezone.now()
    year = year or now.year
    this_m, next_m = _month_bounds(0)
    evs = Event.objects.select_related("event_type", "region")
    if region_ids is not None:
        evs = evs.filter(region_id__in=region_ids)
    month_evs = evs.filter(start_at__date__gte=this_m, start_at__date__lt=next_m)
    done = evs.filter(status="done").count()
    upcoming = evs.filter(start_at__gte=now).count()
    total = evs.count() or 1
    participants = EventRegistration.objects.count()
    regions_n = evs.exclude(region=None).values("region").distinct().count()

    type_rows = []
    for t in evs.values("event_type__name", "event_type__colour").annotate(n=Count("id")).order_by("-n"):
        type_rows.append({"label": t["event_type__name"], "value": t["n"], "display": str(t["n"]),
                          "pct": pct(t["n"], total), "color": t["event_type__colour"]})

    status_rows = []
    for key, label, colour in [("done", "Imefanyika", C["green"]), ("planned", "Imepangwa", C["blue"]),
                               ("postponed", "Imeahirishwa", C["gold"]),
                               ("cancelled", "Imeghairiwa", C["red"])]:
        n = evs.filter(status=key).count()
        status_rows.append({"label": label, "value": n, "display": str(n),
                            "pct": pct(n, total), "color": colour})

    part_rows = (EventRegistration.objects.values("event__region__name")
                 .annotate(n=Count("id")).exclude(event__region__name=None).order_by("-n")[:5])
    pmax = part_rows[0]["n"] if part_rows else 1
    colours = [C["green"], C["blue"], C["gold"], C["purple"], C["teal"]]

    cal = _calendar(this_m, evs, month_key)
    month_sum = []
    for t in month_evs.values("event_type__name", "event_type__colour").annotate(n=Count("id")).order_by("-n"):
        month_sum.append({"label": t["event_type__name"], "value": t["n"],
                          "pct": round(t["n"] / max(month_evs.count(), 1) * 100),
                          "color": t["event_type__colour"]})

    return {
        "kpis": [
            {"label": "Jumla ya Matukio", "value": num(evs.count()), "icon": "calendar",
             "tint": "green", "note": "Mwezi huu"},
            {"label": "Matukio Yaliyofanyika", "value": num(done), "icon": "calendar-check",
             "tint": "navy", "note": "Mwezi huu"},
            {"label": "Matukio Yanayokuja", "value": num(upcoming), "icon": "clock",
             "tint": "purple", "note": "Mwezi huu"},
            {"label": "Jumla ya Washiriki", "value": num(participants), "icon": "users",
             "tint": "gold", "note": "Mwezi huu"},
            {"label": "Mikoa Inayohusika", "value": num(regions_n), "icon": "map-pin",
             "tint": "teal", "note": "Mwezi huu"},
            {"label": "Asilimia ya Utekelezaji", "value": f"{pct(done, total, 0)}%",
             "icon": "pie", "tint": "gold", "progress": int(float(pct(done, total, 0)))},
        ],
        "trend": {"labels": MONTHS,
                  "data_done": monthly_series(evs.filter(status="done"), "start_at", year=year),
                  "data_up": monthly_series(evs.filter(status="planned"), "start_at", year=year)},
        "by_type": {"id": "chEvType", "title": "Matukio kwa Aina",
                    "center_value": num(evs.count()), "center_label": "Jumla", "rows": type_rows},
        "upcoming": [{"title": e.tx("title"), "date": e.start_at.strftime("%d/%m/%Y"),
                      "place": e.region.name if e.region else "—",
                      "in": _("Siku %(n)d") % {"n": max(e.days_until, 0)}, "scene": e.scene}
                     for e in evs.filter(start_at__gte=now).order_by("start_at")[:5]],
        "recent": [{"title": e.tx("title"), "date": e.start_at.strftime("%d/%m/%Y"),
                    "place": e.region.name if e.region else "—",
                    "status": e.get_status_display()}
                   for e in evs.filter(status="done").order_by("-start_at")[:5]],
        "participants": [{"n": i, "name": r["event__region__name"], "value": num(r["n"]),
                          "pct": round(r["n"] / pmax * 100), "color": colours[(i - 1) % 5]}
                         for i, r in enumerate(part_rows, 1)],
        "participants_total": num(participants),
        "status_mix": {"id": "chEvStatus", "title": "Matukio kwa Hali",
                       "center_value": num(evs.count()), "center_label": "", "rows": status_rows},
        "alerts": [{"text": _("%(title)s lipo baada ya siku %(days)d.")
                             % {"title": e.tx("title"), "days": max(e.days_until, 0)},
                    "time": e.start_at.strftime("%d/%m/%Y"), "icon": "bell", "tint": "green"}
                   for e in evs.filter(start_at__gte=now).order_by("start_at")[:4]],
        "calendar": cal,
        "month_summary": month_sum,
        "month_total": num(month_evs.count()),
        "actions": [
            {"label": "Ongeza Tukio", "icon": "calendar", "tint": "green", "url": "/mfumo/matukio/mpya/"},
            {"label": "Panga Matukio", "icon": "clock", "tint": "navy", "url": "/mfumo/matukio/"},
            {"label": "Orodha ya Washiriki", "icon": "users", "tint": "gold", "url": "/mfumo/usajili-matukio/"},
            {"label": "Tuma Ualikaji", "icon": "mail", "tint": "purple", "url": "/ujumbe/"},
            {"label": "Kalenda Kamili", "icon": "calendar-check", "tint": "teal", "url": "/matukio/"},
            {"label": "Tengeneza Ripoti", "icon": "chart-bar", "tint": "orange", "url": "/pakua/wanachama/"},
        ],
    }


def _calendar(first, events, month_key=None):
    """Kalenda ya mwezi. `month_key` ni "YYYY-MM" kwa kuvinjari miezi mingine."""
    import calendar as cal_mod
    year, month = first.year, first.month
    if month_key:
        try:
            year, month = (int(x) for x in month_key.split("-")[:2])
            month = min(max(month, 1), 12)
        except (ValueError, TypeError):
            pass
    weeks = cal_mod.Calendar(firstweekday=0).monthdayscalendar(year, month)
    marks = {}
    tints = ["ev", "ev2", "ev3"]
    for i, e in enumerate(events.filter(start_at__year=year, start_at__month=month)):
        marks[e.start_at.day] = tints[i % 3]
    prev_y, prev_m = (year - 1, 12) if month == 1 else (year, month - 1)
    next_y, next_m = (year + 1, 1) if month == 12 else (year, month + 1)
    return {
        "title": f"{MONTHS[month - 1]} {year}",
        "year": year,
        "prev": f"{prev_y}-{prev_m:02d}",
        "next": f"{next_y}-{next_m:02d}",
        "dow": ["Jtt", "Jnn", "Jtn", "Alh", "Ijm", "Jms", "Jpl"],
        "days": [[d if d else None for d in wk] for wk in weeks],
        "marks": marks,
    }


# ===========================================================================
#  PICHA NA VIDEO
# ===========================================================================
def media(year=None):
    year = year or timezone.localdate().year
    this_m, _unused = _month_bounds(0)
    items = MediaItem.objects.all()
    photos = items.filter(kind="photo")
    videos = items.filter(kind="video")
    setting = SiteSetting.get()
    used = float(items.aggregate(s=Sum("size_mb"))["s"] or 0) / 1024
    quota = setting.storage_quota_gb or 100
    used_pct = min(round(used / quota * 100), 100)
    p_used = float(photos.aggregate(s=Sum("size_mb"))["s"] or 0) / 1024
    v_used = float(videos.aggregate(s=Sum("size_mb"))["s"] or 0) / 1024

    def cat_rows(qs, total):
        labels = dict(MediaItem.CATEGORY)
        colours = [C["green"], C["blue"], C["gold"], C["purple"], C["teal"], C["red"]]
        rows = []
        for i, r in enumerate(qs.values("category").annotate(n=Count("id")).order_by("-n")):
            rows.append({"label": str(labels.get(r["category"], r["category"])),
                         "value": r["n"], "display": f"{pct(r['n'], total)}%",
                         "color": colours[i % 6]})
        return rows

    return {
        "kpis": [
            {"label": "Jumla ya Picha", "value": num(photos.count()), "icon": "image",
             "tint": "green", "note": "Mwezi huu"},
            {"label": "Jumla ya Video", "value": num(videos.count()), "icon": "video",
             "tint": "navy", "note": "Mwezi huu"},
            {"label": "Pakiwa Mwezi Huu", "value": num(items.filter(uploaded_on__gte=this_m).count()),
             "icon": "upload", "tint": "purple", "note": "Mwezi huu"},
            {"label": "Pakuliwa (Downloads)", "value": num(items.aggregate(s=Sum("downloads"))["s"] or 0),
             "icon": "download", "tint": "gold", "note": "Mwezi huu"},
            {"label": "Albamu", "value": num(Album.objects.count()), "icon": "folder",
             "tint": "teal", "note": "Mkusanyiko wa albamu"},
            {"label": "Hifadhi Inayopatikana", "value": f"{used:.1f} GB", "icon": "database",
             "tint": "navy", "note": f"ya {quota} GB ({used_pct}%)", "progress": used_pct},
        ],
        "trend": {"labels": MONTHS,
                  "photos": monthly_series(photos, "uploaded_on", year=year),
                  "videos": monthly_series(videos, "uploaded_on", year=year)},
        "photo_cat": {"id": "chPhotoCat", "title": "Picha kwa Kategoria",
                      "center_value": num(photos.count()), "center_label": "Jumla",
                      "rows": cat_rows(photos, photos.count() or 1)},
        "video_cat": {"id": "chVideoCat", "title": "Video kwa Kategoria",
                      "center_value": num(videos.count()), "center_label": "Jumla",
                      "rows": cat_rows(videos, videos.count() or 1)},
        "storage": {"used": f"{used:.1f} GB", "total": f"{quota} GB", "pct": used_pct,
                    "rows": [{"label": "Picha", "value": f"{p_used:.1f} GB"},
                             {"label": "Video", "value": f"{v_used:.1f} GB"},
                             {"label": "Nyaraka Nyingine", "value": "0.0 GB"}]},
        "photos": [{"title": p.tx("title"), "date": p.uploaded_on.strftime("%d/%m/%Y"),
                    "views": num(p.views), "size": f"{p.size_mb} MB", "scene": p.scene,
                    "url": p.file.url if p.file else ""}
                   for p in photos.order_by("-uploaded_on")[:5]],
        "videos": [{"title": v.tx("title"), "date": v.uploaded_on.strftime("%d/%m/%Y"),
                    "dur": v.duration or "00:00", "size": f"{v.size_mb} MB", "scene": v.scene,
                    "url": v.file.url if v.file else ""}
                   for v in videos.order_by("-uploaded_on")[:5]],
        "uploads": [{"name": m.tx("title"),
                     "meta": m.uploaded_on.strftime("%d/%m/%Y  %I:%M %p"),
                     "size": f"{m.size_mb} MB", "scene": m.scene}
                    for m in items.order_by("-uploaded_on")[:5]],
        "actions": [
            {"label": "Pakia Picha", "icon": "image", "tint": "green", "url": "/media/pakia/"},
            {"label": "Pakia Video", "icon": "video", "tint": "navy", "url": "/media/pakia/"},
            {"label": "Unda Albamu", "icon": "folder", "tint": "purple", "url": "/mfumo/albamu/mpya/"},
            {"label": "Panga Faili", "icon": "settings", "tint": "gold", "url": "/mfumo/media/"},
        ],
    }


# ===========================================================================
#  DASHIBODI KUU
# ===========================================================================
def superadmin(year=None):
    year = year or timezone.localdate().year
    n = _superadmin_shared(year)
    this_m, _unused = _month_bounds(0)
    ok = confirmed(Payment.objects.all())
    mix = []
    ada = ok.filter(paid_at__date__gte=this_m).aggregate(s=Sum("amount"))["s"] or 0
    conts = confirmed(Contribution.objects.filter(received_at__date__gte=this_m))
    hiari = conts.filter(fund__code="hiari").aggregate(s=Sum("amount"))["s"] or 0
    misaada = conts.filter(fund__code__in=["sadaqa", "dharura"]).aggregate(s=Sum("amount"))["s"] or 0
    other = (conts.aggregate(s=Sum("amount"))["s"] or 0) - hiari - misaada
    total_mix = ada + hiari + misaada + other or 1
    for label, amt, colour in [("Ada za Uanachama", ada, C["green"]),
                               ("Michango", hiari, C["navy"]),
                               ("Misaada", misaada, C["gold"]),
                               ("Ada Nyingine", max(other, 0), C["purple"])]:
        mix.append({"label": label, "value": int(amt), "display": num(amt),
                    "pct": pct(amt, total_mix), "color": colour})

    return {
        "kpis": n["kpis"][:1] + [
            {"label": "Wanachama Hai",
             "value": num(Member.objects.filter(status=MemberStatus.ACTIVE).count()),
             "icon": "user-check", "tint": "navy",
             "note": f"{pct(Member.objects.filter(status=MemberStatus.ACTIVE).count(), Member.objects.count() or 1)}% ya jumla ya wanachama"},
            {"label": "Jumla ya Michango",
             "value": tzs(confirmed(Contribution.objects.all()).aggregate(s=Sum('amount'))['s'] or 0),
             "icon": "coins", "tint": "gold", "money": True},
            {"label": "Pointi Zilizotolewa",
             "value": num(PointTransaction.objects.aggregate(s=Sum("points"))["s"] or 0),
             "icon": "star", "tint": "purple"},
            {"label": "Misaada Iliyotolewa",
             "value": tzs(Expense.objects.aggregate(s=Sum("amount"))["s"] or 0),
             "icon": "hand-heart", "tint": "teal", "money": True},
        ],
        "growth": n["members_month"],
        "by_category": {**n["by_category"], "id": "chCategory", "title": "Wanachama kwa Kategoria"},
        "recent_members": [{"full_name": m.full_name, "initials": m.initials,
                            "category": m.category.name,
                            "joined": m.joined_on.strftime("%d %b %Y")}
                           for m in Member.objects.order_by("-created_at")[:5]],
        "revenue": {"labels": MONTHS, "data": monthly_series(ok, "paid_at", "amount", year)},
        "payment_mix": {"id": "chPayments", "title": "Muhtasari wa Malipo", "control": "Mwezi Huu",
                        "center_value": tzs(total_mix), "center_label": "Jumla", "rows": mix},
        "quick_actions": {"title": "Vitendo vya Haraka", "cols": 4, "items": [
            {"label": "Ongeza Mwanachama", "icon": "user-plus", "tint": "green", "url": "/usajili/"},
            {"label": "Rekodi Malipo", "icon": "cash", "tint": "navy", "url": "/malipo/"},
            {"label": "Ongeza Mchango", "icon": "hand-heart", "tint": "teal", "url": "/michango/"},
            {"label": "Maombi ya Msaada", "icon": "heart", "tint": "purple", "url": "/mfumo/programs/assistancerequest/"},
            {"label": "Ongeza Tukio", "icon": "calendar", "tint": "gold", "url": "/matukio/"},
            {"label": "Tuma Ujumbe", "icon": "message", "tint": "green", "url": "/ujumbe/"},
            {"label": "Pakua Ripoti", "icon": "download", "tint": "orange", "url": "/pakua/wahisani/"},
            {"label": "Mipangilio", "icon": "settings", "tint": "navy", "url": "/mfumo/mipangilio/"},
        ]},
        "recent_payments": [
            {"date": p.paid_at.strftime("%d %b %Y"), "member": p.member.full_name,
             "desc": _("Ada ya Uanachama"), "amount": num(p.amount), "method": p.method_label,
             "receipt_no": p.receipt_no, "status": p.get_status_display()}
            for p in ok.order_by("-paid_at")[:5]],
        "announcements": [{"title": a.tx("title"), "icon": a.icon, "tint": a.tint,
                           "body": a.tx("body"), "date": a.published_on.strftime("%d %b %Y")}
                          for a in Announcement.objects.filter(is_active=True, status="approved")[:3]],
    }


def _superadmin_shared(year=None):
    """
    Sehemu ndogo ya `national()` inayohitajika kwenye dashibodi kuu.
    Kuita `national()` nzima kulikuwa kunaleta queries nyingi zisizohitajika.
    """
    year = year or timezone.localdate().year
    total = Member.objects.count()
    members = Member.objects.all()
    cat_counts = {row["category_id"]: row["n"]
                  for row in members.values("category_id").annotate(n=Count("id"))}
    cat_rows = []
    for c in Category.objects.all():
        cnt = cat_counts.get(c.pk, 0)
        if cnt:
            cat_rows.append({"label": c.name, "value": cnt, "display": num(cnt),
                             "pct": pct(cnt, total or 1),
                             "color": cat_colour(c)})
    cat_rows.sort(key=lambda r: -r["value"])
    this_m, _unused = _month_bounds(0)
    prev_total = members.filter(joined_on__lt=this_m).count()
    d1, dir1 = delta(total, prev_total)
    return {
        "kpis": [{"label": "Wanachama Jumla", "value": num(total), "icon": "users",
                  "tint": "green", "delta": d1, "dir": dir1,
                  "note": "Ikilinganishwa na mwezi jana"}],
        "members_month": {"labels": MONTHS,
                          "data": _cumulative(monthly_series(members, "joined_on", year=year), total)},
        "by_category": {"id": "chCat", "title": "Aina za Wanachama",
                        "center_value": num(total), "center_label": "Jumla", "rows": cat_rows},
    }


# ===========================================================================
#  MWANACHAMA
# ===========================================================================
def member_dashboard(member):
    account, _created = Account.objects.get_or_create(member=member)
    balance = account.balance()
    points = PointTransaction.balance(member)
    this_m, _unused = _month_bounds(0)
    month_points = (PointTransaction.objects.filter(member=member, awarded_on__gte=this_m)
                    .aggregate(s=Sum("points"))["s"] or 0)
    card = member.cards.filter(is_active=True).first()
    contributed = (confirmed(member.contributions.all()).aggregate(s=Sum("amount"))["s"] or 0)
    paid = (confirmed(member.payments.all()).aggregate(s=Sum("amount"))["s"] or 0)
    pending = member.payments.filter(status=PaymentStatus.PENDING).aggregate(s=Sum("amount"))["s"] or 0
    # Safari inaonyeshwa kuelekea KIWANGO kinachofuata, si tuzo. Kiwango
    # ndicho mwanachama anachokiona kwenye kadi yake, kwa hiyo ndicho
    # chenye maana kwake.
    from programs import points as _pts
    tier = _pts.tier_for(points)
    nxt_tier = _pts.next_tier(points)
    remaining = (nxt_tier["min"] - points) if nxt_tier else 0
    floor = tier["min"]
    span = max((nxt_tier["min"] if nxt_tier else points + 1) - floor, 1)
    progress = min(round((points - floor) / span * 100), 100)

    return {
        "member": {
            "full_name": member.full_name, "initials": member.initials,
            "membership_no": member.membership_no, "account_no": member.account_no,
            "category": member.category.name, "category_label": f"{member.category.name} Member",
            "national_id": member.national_id, "phone": member.phone, "email": member.email,
            "issued": (card.issued_on if card else member.joined_on).strftime("%d %b %Y"),
            "valid_range": f"{member.joined_on.year} - {member.expires_on.year}" if member.expires_on else "—",
            "registered": member.joined_on.strftime("%d %b %Y"),
            "card_serial": card.serial if card else "—",
            "verify_url": card.verify_path if card else "",
        },
        "kpis": [
            {"label": "Hali ya Uanachama", "value": member.get_status_display(),
             "icon": "check-circle", "tint": _status_tint(member),
             "note": _status_note(member)},
            {"label": "Halali Hadi",
             "value": member.expires_on.strftime("%d %b %Y") if member.expires_on else "—",
             "icon": "calendar", "tint": _expiry_tint(member), "money": True,
             "note": _expiry_note(member)},
            {"label": "Pointi Zako", "value": num(points), "icon": "star", "tint": "gold",
             "note": "Jumla ya pointi"},
            {"label": "Ada ya Mwezi", "value": tzs(member.category.monthly_fee),
             "icon": "wallet", "tint": "orange", "money": True,
             "note": "Unalipia miezi unayotaka"},
            {"label": "Malipo Yanayofuata", "value": _next_due(member), "icon": "clock",
             "tint": "purple", "money": True, "note": "Tarehe ya malipo ijayo"},
            {"label": "Jumla ya Michango", "value": tzs(contributed + paid), "icon": "chart-bar",
             "tint": "teal", "money": True, "note": "Michango yote hadi sasa"},
        ],
        "wallet": {"balance": tzs(balance), "rows": [
            {"label": "Akiba / Savings", "value": tzs(account.savings)},
            {"label": "Michango ya Ustawi", "value": tzs(account.total_by_fund("sadaqa"))},
            {"label": "Michango Mengine", "value": tzs(account.total_by_fund("hiari"))},
            {"label": "Malipo Yanayosubiri", "value": tzs(pending), "danger": bool(pending)},
        ]},
        #: `level` ni KIWANGO cha pointi (Mshiriki, Nguzo...), si daraja la
        #: uanachama (Bronze, Silver...). Ni vitu viwili tofauti kabisa —
        #: daraja linatokana na ada anayolipa, kiwango na ushiriki wake.
        "points": {"current": num(points), "earned_this_month": f"+{num(month_points)}",
                   "level": _g.tx(tier, "name"), "tier_icon": tier["icon"],
                   "tier_note": _g.tx(tier, "note"),
                   "next_tier": (_g.tx(nxt_tier, "name") if nxt_tier else ""),
                   "next_reward_remaining": num(remaining),
                   "progress": min(progress, 100)},
        "quick_actions": {"title": "Hatua za Haraka", "cols": 4, "items": [
            {"label": "Sajili Mwanafamilia", "icon": "users", "tint": "green", "url": "/mwanachama/familia/"},
            {"label": "Lipa Ada", "icon": "cash", "tint": "navy", "url": "/mwanachama/malipo/"},
            {"label": "Omba Msaada", "icon": "hand-heart", "tint": "teal", "url": "/mwanachama/msaada/"},
            {"label": "Changia / Donate", "icon": "heart", "tint": "red", "url": "/mwanachama/michango/"},
            {"label": "Kadi Yangu", "icon": "id-card", "tint": "gold", "url": "/mwanachama/kadi/"},
            {"label": "Pointi Zangu", "icon": "star", "tint": "purple", "url": "/mwanachama/pointi/"},
            {"label": "Tuma Maoni", "icon": "message", "tint": "orange", "url": "/mawasiliano/"},
            {"label": "Sasisha Wasifu", "icon": "settings", "tint": "navy", "url": "/mwanachama/wasifu/"},
        ]},
        "transactions": [
            {"date": p.paid_at.strftime("%d %b %Y"), "desc": _("Ada ya Uanachama (Mwezi)"),
             "amount": num(p.amount), "status": p.get_status_display()}
            for p in member.payments.order_by("-paid_at")[:4]],
        "events": [{"id": e.pk, "title": e.tx("title"),
                    "when": e.start_at.strftime("%d %b %Y  |  %I:%M %p"),
                    "venue": e.tx("venue"), "icon": "calendar", "tint": "green"}
                   for e in Event.objects.filter(start_at__gte=timezone.now()).order_by("start_at")[:3]],
        "announcements": [{"title": a.tx("title"), "icon": a.icon, "tint": a.tint,
                           "body": a.tx("body"), "date": a.published_on.strftime("%d %b %Y")}
                          for a in Announcement.objects.filter(is_active=True, status="approved")[:3]],
    }



def _expiry_tint(member):
    """
    Rangi inayoonyesha uzito wa hali. Nyekundu ikiisha, machungwa
    ikikaribia, kijani ikiwa bado kuna muda.
    """
    left = member.days_left
    if left is None:
        return "navy"
    if left < 0:
        return "red"
    return "orange" if left <= 90 else "green"


def _expiry_note(member):
    left = member.days_left
    if left is None:
        return "Tarehe haijawekwa"
    if left < 0:
        return _("Muda umeisha — huisha uanachama wako")
    if left == 0:
        return _("Unaisha leo")
    if left <= 90:
        return _("Umebakiwa na siku %(n)d") % {"n": left}
    years = Member.TERM_YEARS
    return _("Kipindi cha miaka %(y)d") % {"y": years}


def _status_tint(member):
    if member.status == "expired" or member.has_expired:
        return "red"
    return "green" if member.status == "active" else "orange"


def _status_note(member):
    if member.has_expired:
        return _("Muda wa uanachama umeisha")
    if member.status == "active":
        return _("Uanachama wako ni hai")
    return member.get_status_display()


def _next_due(member):
    """
    Tarehe ya kulipia tena — mwisho wa kipindi cha miaka mitatu.

    `expires_on` ndiyo chanzo cha ukweli; inasogezwa kila malipo
    yanapothibitishwa. Ikikosekana (rekodi za zamani), tunahesabu kutoka
    tarehe ya kujiunga.
    """
    if member.expires_on:
        return member.expires_on.strftime("%d %b %Y")
    base = member.joined_on or timezone.localdate()
    try:
        return base.replace(year=base.year + 3).strftime("%d %b %Y")
    except ValueError:          # 29 Feb
        return base.replace(year=base.year + 3, day=28).strftime("%d %b %Y")


# ===========================================================================
#  TOVUTI YA UMMA
# ===========================================================================
def public_home():
    s = SiteSetting.get()
    now = timezone.now()
    return {
        "contacts": {"phone": s.phone, "email": s.email, "address": s.tx("address")},
        "hero": {
            "eyebrow": "Karibu kwenye Mfumo wa Usimamizi wa Uanachama wa MUWESTA",
            "title": "Imani kwa Vitendo,<br>Huduma na Maendeleo<br>kwa Binadamu",
            "text": s.tx("about"),
        },
        "services": [
            {"label": "Uanachama", "icon": "users", "url": "/uanachama/"},
            {"label": "Malipo & Michango", "icon": "wallet", "url": "/uanachama/"},
            {"label": "Pointi & Tuzo", "icon": "star", "url": "/uanachama/"},
            {"label": "Huduma za Ustawi", "icon": "hand-heart", "url": "/huduma/"},
            {"label": "Matukio", "icon": "calendar", "url": "/matukio-yetu/"},
            {"label": "Habari", "icon": "megaphone", "url": "/habari/"},
            {"label": "Nyaraka", "icon": "file", "url": "/kuhusu/"},
            {"label": "Mawasiliano", "icon": "phone", "url": "/mawasiliano/"},
        ],
        "events": [_pub_event(e) for e in
                   Event.objects.filter(is_public=True, start_at__gte=now).order_by("start_at")[:3]],
        "news": [{"title": n.tx("title"), "date": n.published_on.strftime("%d %b %Y"),
                  "text": n.tx("summary"), "scene": n.scene}
                 for n in News.objects.filter(is_published=True)[:3]],
        "gallery": [{"cap": a.tx("name"), "count": _("%(n)d Picha") % {"n": a.item_count()}, "scene": a.scene}
                    for a in Album.objects.filter(is_public=True)[:6]],
        #: Miradi michache inayoendelea. Mgeni anataka kuona kazi HALISI
        #: kabla ya kuombwa kuchangia; kiungo cha "tazama zote" kinampeleka
        #: kwenye orodha kamili badala ya kujaza ukurasa wa nyumbani.
        "projects": [{"title": p.tx("title"),
                      "text": p.tx("summary"),
                      "place": p.region.name if p.region else "",
                      "pct": p.progress(), "bar": p.progress_bar(),
                      "raised": tzs(p.raised()), "goal": tzs(p.target_amount),
                      "purpose": _project_purpose(p), "scene": p.scene}
                     for p in Project.objects.filter(status="ongoing")
                     .order_by("-created_at")[:3]],
        "projects_total": Project.objects.filter(status="ongoing").count(),
        "bottom_stats": _bottom_stats(),
    }


def _pub_event(e):
    return {"d": e.start_at.strftime("%d"), "m": MONTHS_SHORT_UP[e.start_at.month - 1],
            "y": e.start_at.strftime("%Y"), "title": e.tx("title"), "venue": e.tx("venue"),
            "time": (f"{e.start_at.strftime('%I:%M %p')} - {e.end_at.strftime('%I:%M %p')}"
                     if e.end_at else e.start_at.strftime("%I:%M %p")),
            "status": e.get_status_display(), "badge": e.badge, "scene": e.scene,
            "text": e.tx("summary"), "cat": e.event_type.slug,
            "cat_label": e.event_type.tx("name"), "id": e.pk}


def _bottom_stats():
    this_m, _unused = _month_bounds(0)
    return [
        {"label": "Matukio Yaliyofanyika Mwezi Huu",
         "value": _("%(n)d Matukio") % {"n": Event.objects.filter(
             start_at__date__gte=this_m, status="done").count()},
         "icon": "calendar", "tint": "gold", "delta": ""},
        {"label": "Habari Zilizochapishwa Mwezi Huu",
         "value": _("%(n)d Habari") % {"n": News.objects.filter(published_on__gte=this_m).count()},
         "icon": "file", "tint": "green", "delta": ""},
        {"label": "Picha Zilizohudumiwa Mwezi Huu",
         "value": _("%(n)d Picha") % {"n": MediaItem.objects.filter(
             kind="photo", uploaded_on__gte=this_m).count()},
         "icon": "image", "tint": "navy", "delta": ""},
        {"label": "Wanufaika Mwezi Huu",
         "value": _("%(n)s Watu") % {"n": num(
             EventRegistration.objects.filter(created_at__date__gte=this_m).count())},
         "icon": "users", "tint": "teal", "delta": ""},
    ]


def public_kuhusu():
    return {
        "hero": {"eyebrow": "Kuhusu Sisi", "scene": "msikiti",
                 "title": "Historia, Dira na Dhamira ya MUWESTA",
                 "text": SiteSetting.get().tx("about")},
        "pillars": [{"title": p.tx("title"), "text": p.tx("body"), "icon": p.icon, "tint": p.tint}
                    for p in Pillar.objects.all()],
        "counters": [
            {"value": Member.objects.count(), "label": "Wanachama Nchini Kote"},
            {"value": Region.objects.count(), "label": "Mikoa Tunayofanya Kazi"},
            {"value": _district_count(), "label": "Wilaya Tulizofikia"},
            {"value": Project.objects.count(), "label": "Miradi Inayoendelea"},
        ],
        "timeline": [{"year": m.year, "title": m.tx("title"), "text": m.tx("body")}
                     for m in Milestone.objects.all()],
        "leaders": [{"initials": l.initials, "name": l.full_name, "role": l.tx("role")}
                    for l in Leader.objects.filter(is_active=True)],
        "faqs": [{"q": f.tx("question"), "a": f.tx("answer")}
                 for f in Faq.objects.filter(page="kuhusu", is_active=True)],
    }


def public_uanachama():
    tiers = []
    for c in Category.objects.filter(is_selectable=True):
        tiers.append({"name": c.name, "price": tzs(c.monthly_fee), "per": "kwa mwezi",
                      "featured": c.is_featured, "items": c.benefit_list()})
    special = Category.objects.filter(is_special=True).first()
    return {
        "hero": {"eyebrow": "Uanachama", "scene": "jamii",
                 "title": "Jiunge na Familia ya MUWESTA",
                 "text": "Uanachama wa MUWESTA unakupa fursa ya kushiriki katika huduma za "
                         "kijamii, kupata msaada wa ustawi, na kujenga jamii bora kwa pamoja."},
        "benefits": [
            {"title": "Kadi ya Kidijitali", "icon": "id-card", "tint": "green",
             "text": "Kadi yenye QR code inayothibitisha uanachama wako popote."},
            {"title": "Msaada wa Ustawi", "icon": "hand-heart", "tint": "navy",
             "text": "Fursa ya kuomba msaada wa dharura, matibabu au elimu."},
            {"title": "Pointi na Tuzo", "icon": "star", "tint": "gold",
             "text": "Pata pointi kwa kila mchango na ushiriki, kisha ubadilishe na tuzo."},
            {"title": "Akaunti Yako", "icon": "wallet", "tint": "purple",
             "text": "Akaunti binafsi inayoonyesha michango, malipo na salio lako."},
            {"title": "Matukio na Mafunzo", "icon": "calendar", "tint": "teal",
             "text": "Alika kwenye semina, mafunzo na mikutano ya jumuiya."},
            {"title": "Sauti kwenye Maamuzi", "icon": "users", "tint": "orange",
             "text": "Haki ya kupiga kura kwenye Mkutano Mkuu wa mwaka."},
        ],
        "tiers": tiers,
        "special": ({"name": special.tx("name"), "price": tzs(special.monthly_fee),
                     "items": special.benefit_list(), "colour": special.colour}
                    if special else None),
        "steps": [
            {"n": 1, "title": "Jaza Fomu", "icon": "file",
             "text": "Jaza taarifa zako binafsi na za mawasiliano mtandaoni."},
            {"n": 2, "title": "Chagua Aina", "icon": "star",
             "text": "Chagua aina ya uanachama inayokufaa: Bronze hadi Diamond."},
            {"n": 3, "title": "Lipa Ada", "icon": "wallet",
             "text": "Lipa kwa M-Pesa, Airtel Money, Tigo Pesa au benki."},
            {"n": 4, "title": "Pokea Kadi", "icon": "id-card",
             "text": "Pokea namba ya uanachama na kadi ya kidijitali yenye QR."},
        ],
        "points_rules": [{"activity": r.tx("activity"), "points": str(r.points)}
                         for r in PointRule.objects.filter(is_active=True)],
    }



#: Mandhari ya mradi (`Project.scene`) -> aina ya mchango kwenye katalogi.
#: `Project` haina mfuko; `scene` ndiyo inayoeleza mradi unahusu nini.
#: Isiyoorodheshwa hapa inarudi "maendeleo", ambayo ipo daima.
_SCENE_PURPOSE = {
    "maji": "maji",
    "afya": "afya",
    "elimu": "scholarship",
    # "ujenzi" hutumika kwa shule na misikiti sawasawa, kwa hiyo
    # "maendeleo" ni sahihi zaidi kuliko kudhani ni msikiti.
    "ujenzi": "maendeleo",
    "sadaka": "sadaqah",
    "yatima": "yatima",
    "chakula": "chakula",
    "dharura": "dharura",
}


def _project_purpose(project):
    """Aina ya mchango inayolingana na mradi, kwa `/changia/?aina=`."""
    key = _SCENE_PURPOSE.get(getattr(project, "scene", "") or "", "maendeleo")
    return key if _g.purpose(key) else "maendeleo"


def public_huduma():
    svc = Service.objects.filter(is_active=True)
    cats = OrderedDict()
    for s in svc:
        cats.setdefault(s.category, s.category.title())
    filters = [{"key": "all", "label": "Zote"}] + \
              [{"key": k, "label": v} for k, v in cats.items()]
    return {
        "hero": {"eyebrow": "Huduma Zetu", "scene": "jamii",
                 "title": "Huduma Zinazogusa Maisha",
                 #: Sentensi hii ilikuwa haipiti kwenye tafsiri — ilionekana
                 #: kwa Kiswahili hata kwenye ukurasa wa Kiingereza.
                 "text": gettext("Tunatoa huduma katika maeneo makuu yanayolenga "
                                 "kuinua hali ya maisha ya jamii kwa njia endelevu.")},
        "services": [{"title": s.tx("title"), "text": s.tx("summary"),
                      "stats": s.tx("stats_line"), "icon": s.icon, "tint": s.tint,
                      "scene": s.scene, "cat": s.category} for s in svc],
        "filters": filters,
        #: `purpose` inaunganisha mradi na aina ya mchango kwenye ukurasa
        #: wa malipo, ili mtu asichague tena kile alichokwisha kubofya.
        #: Mfuko wa mradi ndio chanzo; ukikosekana, "maendeleo".
        "projects": [{"title": p.tx("title"), "place": p.region.name if p.region else "—",
                      "pct": p.progress(), "bar": p.progress_bar(),
                      "raised": tzs(p.raised()), "goal": num(p.target_amount),
                      "purpose": _project_purpose(p),
                      "scene": p.scene, "over": p.progress() > 100}
                     for p in Project.objects.filter(status="ongoing")[:3]],
        "impact": [
            {"value": EventRegistration.objects.count(), "label": "Wanufaika kwa Mwezi"},
            {"value": Project.objects.filter(status="ongoing").count(),
             "label": "Miradi Inayoendelea"},
            {"value": Member.objects.count(), "label": "Wanachama"},
            {"value": Donor.objects.count(), "label": "Wahisani na Wadau"},
        ],
    }


def public_habari():
    qs = News.objects.filter(is_published=True)
    featured = qs.filter(is_featured=True).first() or qs.first()
    others = qs.exclude(pk=featured.pk) if featured else qs
    from content.models import NewsCategory
    filters = [{"key": "all", "label": "Zote"}] + \
              [{"key": c.slug, "label": c.tx("name")} for c in NewsCategory.objects.all()]
    return {
        "hero": {"eyebrow": "Habari", "scene": "mkutano",
                 "title": "Habari na Taarifa za MUWESTA",
                 "text": "Fuatilia shughuli, miradi, matangazo na fursa mbalimbali kutoka MUWESTA."},
        "featured": {"title": featured.tx("title"), "date": featured.published_on.strftime("%d %B %Y"),
                     "cat": featured.category.tx("name") if featured.category else "Habari",
                     "text": featured.tx("summary"), "scene": featured.scene} if featured else {},
        "filters": filters,
        "items": [{"title": n.tx("title"), "date": n.published_on.strftime("%d %B %Y"),
                   "cat": n.category.slug if n.category else "nyingine",
                   "cat_label": n.category.tx("name") if n.category else "Habari",
                   "text": n.tx("summary"), "scene": n.scene} for n in others[:9]],
        "gallery": [{"cap": a.tx("name"), "count": _("%(n)d Picha") % {"n": a.item_count()}, "scene": a.scene}
                    for a in Album.objects.filter(is_public=True)[:6]],
    }


def public_matukio():
    now = timezone.now()
    from programs.models import EventType
    filters = [{"key": "all", "label": "Zote"}] + \
              [{"key": t.slug, "label": t.tx("name")} for t in EventType.objects.all()]
    return {
        "hero": {"eyebrow": "Matukio", "scene": "tukio",
                 "title": "Matukio na Shughuli za MUWESTA",
                 "text": "Jiunge nasi kwenye semina, mikutano, mafunzo na shughuli za kijamii "
                         "zinazofanyika nchini kote."},
        "upcoming": [_pub_event(e) for e in
                     Event.objects.filter(is_public=True, start_at__gte=now).order_by("start_at")[:6]],
        "filters": filters,
        "past": [{"title": e.tx("title"), "date": e.start_at.strftime("%d %B %Y"),
                  "place": e.region.name if e.region else "—"}
                 for e in Event.objects.filter(status="done").order_by("-start_at")[:4]],
        "stats": [
            {"value": Event.objects.count(), "label": "Matukio Mwaka Huu"},
            {"value": EventRegistration.objects.count(), "label": "Washiriki Jumla"},
            {"value": Event.objects.exclude(region=None).values("region").distinct().count(),
             "label": "Mikoa Iliyofikiwa"},
            {"value": Event.objects.filter(status="done").count(), "label": "Matukio Yaliyofanyika"},
        ],
    }


def public_mawasiliano():
    """
    Ukurasa wa Mawasiliano.

    Muundo na taarifa zinatoka `core/data/pages.py` (bango rasmi la MUWESTA).
    Maswali yanayoulizwa sana bado yanatoka database ili yaweze kuhaririwa
    bila kugusa code.
    """
    from .data import pages as _pg

    ctx = _pg.mawasiliano()
    db_faqs = [{"q": f.tx("question"), "a": f.tx("answer")}
               for f in Faq.objects.filter(page="mawasiliano", is_active=True)]
    if db_faqs:
        ctx["faqs"] = db_faqs
    return ctx


def public_jiunge():
    u = public_uanachama()
    return {"hero": {"eyebrow": "Usajili", "scene": "elimu", "title": "Jiunge na MUWESTA Leo",
                     "text": "Jaza fomu hii kuanza safari yako ya uanachama. "
                             "Itachukua dakika chache tu."},
            "tiers": u["tiers"], "steps": u["steps"], "special": u["special"],
            "categories": Category.objects.filter(is_selectable=True),
            "regions_list": Region.objects.all()}


def verse(index=0):
    qs = list(Verse.objects.filter(is_active=True))
    if not qs:
        return None
    v = qs[index % len(qs)]
    return {"arabic": v.arabic, "swahili": v.tx("swahili"), "reference": v.reference}


# ===========================================================================
#  MWANACHAMA — kurasa za huduma binafsi
# ===========================================================================
def member_payments(member):
    account, _created = Account.objects.get_or_create(member=member)
    pays = member.payments.all()
    ok = confirmed(pays)
    year = timezone.localdate().year
    paid_year = ok.filter(paid_at__year=year).aggregate(s=Sum("amount"))["s"] or 0
    # Ada ya mwaka mmoja ndicho kipimo cha kulinganisha malipo ya mwaka.
    due = _g.months_price(member.category.monthly_fee, 12)
    return {
        "kpis": [
            {"label": "Ada ya Mwezi", "value": tzs(member.category.monthly_fee),
             "icon": "wallet", "tint": "green", "money": True},
            {"label": "Nimelipa Mwaka Huu", "value": tzs(paid_year), "icon": "check-circle",
             "tint": "navy", "money": True, "note": _("Mwaka %(y)d") % {"y": year}},
            {"label": "Ada ya Mwaka Mmoja", "value": tzs(due), "icon": "target", "tint": "gold",
             "money": True, "progress": min(round(float(paid_year) / float(due or 1) * 100), 100)},
            {"label": "Salio la Akaunti", "value": tzs(account.balance()), "icon": "coins",
             "tint": "teal", "money": True},
        ],
        "rows": [{
            "receipt": p.receipt_no, "amount": num(p.amount),
            "date": p.paid_at.strftime("%d/%m/%Y %I:%M %p"),
            "method": p.method_label, "month": MONTHS[p.period_month - 1] if p.period_month else "—",
            "year": p.year, "status": p.get_status_display(), "badge": p.badge,
        } for p in pays.order_by("-paid_at")[:40]],
        "total_rows": pays.count(),
        "chart": {"labels": MONTHS, "data": monthly_series(ok, "paid_at", "amount", year)},
    }


def member_contributions(member):
    cons = member.contributions.select_related("fund", "project")
    ok = confirmed(cons)
    total = ok.aggregate(s=Sum("amount"))["s"] or 0
    year = timezone.localdate().year
    by_fund = []
    fund_totals = {r["fund_id"]: r["s"] for r in ok.values("fund_id").annotate(s=Sum("amount"))}
    for f in Fund.objects.exclude(code="ada"):
        amt = fund_totals.get(f.pk, 0)
        if amt:
            by_fund.append({"label": f.name, "value": int(amt), "display": tzs(amt),
                            "pct": pct(amt, total), "color": f.colour})
    return {
        "kpis": [
            {"label": "Jumla ya Michango", "value": tzs(total), "icon": "hand-heart",
             "tint": "green", "money": True},
            {"label": "Mwaka Huu",
             "value": tzs(ok.filter(received_at__year=year).aggregate(s=Sum("amount"))["s"] or 0),
             "icon": "calendar", "tint": "navy", "money": True},
            {"label": "Idadi ya Michango", "value": num(cons.count()), "icon": "receipt",
             "tint": "gold"},
            {"label": "Inasubiri Uthibitisho",
             "value": num(cons.filter(status=PaymentStatus.PENDING).count()),
             "icon": "clock", "tint": "orange"},
        ],
        "by_fund": {"id": "chMyFunds", "title": "Michango kwa Aina",
                    "center_value": tzs(total), "center_label": "Jumla", "rows": by_fund},
        "rows": [{
            "receipt": c.receipt_no, "fund": c.fund.tx("name"), "amount": num(c.amount),
            "project": c.project.tx("title") if c.project else (c.note or "—"),
            "date": c.received_at.strftime("%d/%m/%Y"), "method": c.get_method_display(),
            "status": c.get_status_display(), "badge": c.badge,
        } for c in cons.order_by("-received_at")[:40]],
        "chart": {"labels": MONTHS, "data": monthly_series(ok, "received_at", "amount", year)},
    }


def member_points(member):
    """
    Pointi za MUWESTA kwa mwanachama mmoja.

    Kuna ngazi mbili: pointi za KIPINDI (miaka 3) zinazoamua kiwango
    chake sasa, na pointi za MAISHA ambazo hazipungui kamwe. Mtu
    aliyefanya kazi kubwa zamani anabaki na heshima yake, lakini
    kiwango chake cha leo kinaonyesha ukweli wa leo.
    """
    from programs.models import PointTransaction as PT, Reward
    from programs import points as pts

    period = PT.period(member)
    lifetime = PT.lifetime(member)
    tier = pts.tier_for(period)
    upcoming = pts.next_tier(period)
    split = PT.by_kind(member)
    money_used = PT.money_points(member)

    txns = member.point_transactions.select_related("rule")
    this_m, _unused = _month_bounds(0)

    rewards = []
    for r in Reward.objects.filter(is_active=True):
        rewards.append({
            "title": r.tx("title"), "text": r.tx("description"),
            "points": num(r.points_required),
            "pct": min(round(lifetime / r.points_required * 100), 100) if r.points_required else 100,
            "reached": lifetime >= r.points_required,
            "remaining": num(max(r.points_required - lifetime, 0)),
        })

    # Safari kuelekea kiwango kinachofuata
    floor = tier["min"]
    ceiling = upcoming["min"] if upcoming else max(period, floor + 1)
    span = max(ceiling - floor, 1)
    progress = min(round((period - floor) / span * 100), 100)

    return {
        "tier": {
            "key": tier["key"], "name": _g.tx(tier, "name"), "icon": tier["icon"],
            "note": _g.tx(tier, "note"),
        },
        "next_tier": ({"name": _g.tx(upcoming, "name"),
                       "remaining": num(upcoming["min"] - period),
                       "at": num(upcoming["min"])} if upcoming else None),
        "progress": progress,
        "period_points": num(period),
        "lifetime_points": num(lifetime),
        "period_years": pts.PERIOD_YEARS,
        #: Mgawanyo unamwonyesha mwanachama kwamba fedha si njia pekee —
        #: ushiriki una uzito wake.
        "split": [
            {"label": gettext("Michango na Ada"), "value": num(split.get("money", 0)),
             "raw": split.get("money", 0), "icon": "wallet", "tint": "gold"},
            {"label": gettext("Ushiriki"), "value": num(split.get("participation", 0)),
             "raw": split.get("participation", 0), "icon": "users", "tint": "green"},
            {"label": gettext("Bonasi"), "value": num(split.get("bonus", 0)),
             "raw": split.get("bonus", 0), "icon": "star", "tint": "navy"},
        ],
        "money_cap": {
            "used": num(money_used), "cap": num(pts.MONEY_CAP),
            "pct": min(round(money_used / pts.MONEY_CAP * 100), 100),
            "reached": money_used >= pts.MONEY_CAP,
        },
        "kpis": [
            {"label": "Pointi za MUWESTA", "value": num(period), "icon": "star",
             "tint": "gold", "note": gettext("Miaka %(y)d iliyopita") % {"y": pts.PERIOD_YEARS}},
            {"label": "Kiwango Changu", "value": _g.tx(tier, "name"),
             "icon": tier["icon"], "tint": "navy"},
            {"label": "Nilizopata Mwezi Huu",
             "value": num(txns.filter(awarded_on__gte=this_m).aggregate(s=Sum("points"))["s"] or 0),
             "icon": "trophy", "tint": "green"},
            {"label": "Pointi za Maisha", "value": num(lifetime), "icon": "shield",
             "tint": "teal", "note": gettext("Hazipungui kamwe")},
        ],
        "rows": [{
            "date": t.awarded_on.strftime("%d/%m/%Y"),
            "reason": t.rule.tx("activity") if t.rule else t.reason,
            "kind": gettext(str(pts.PointKind.LABELS.get(t.kind, ""))),
            "points": f"+{t.points}" if t.points >= 0 else str(t.points),
            "positive": t.points >= 0, "source": t.source or "\u2014",
        } for t in txns.order_by("-awarded_on", "-id")[:40]],
        "rewards": rewards,
        "tiers": [{
            "name": _g.tx(row, "name"), "icon": row["icon"], "at": num(row["min"]),
            "note": _g.tx(row, "note"),
            "current": row["key"] == tier["key"],
            "passed": period >= row["min"],
        } for row in pts.TIERS],
        "rules": [{"activity": r.tx("activity"), "points": str(r.points)}
                  for r in PointRule.objects.filter(is_active=True).order_by("order")],
        "chart": {"labels": MONTHS,
                  "data": monthly_series(txns, "awarded_on", "points",
                                         timezone.localdate().year)},
    }


def member_assistance(member):
    reqs = member.assistance_requests.select_related("assistance_type")
    badge = {"pending": "warn", "review": "info", "approved": "ok",
             "rejected": "danger", "paid": "ok"}
    return {
        "kpis": [
            {"label": "Maombi Yangu", "value": num(reqs.count()), "icon": "hand-heart",
             "tint": "green"},
            {"label": "Yaliyoidhinishwa",
             "value": num(reqs.filter(status__in=["approved", "paid"]).count()),
             "icon": "check-circle", "tint": "navy"},
            {"label": "Yanayosubiri",
             "value": num(reqs.filter(status__in=["pending", "review"]).count()),
             "icon": "clock", "tint": "gold"},
            {"label": "Kiasi Kilichopokelewa",
             "value": tzs(reqs.aggregate(s=Sum("amount_approved"))["s"] or 0),
             "icon": "wallet", "tint": "teal", "money": True},
        ],
        "rows": [{
            "ref": r.reference, "type": r.assistance_type.tx("name"),
            "requested": num(r.amount_requested), "approved": num(r.amount_approved),
            "date": r.created_at.strftime("%d/%m/%Y"),
            "status": r.get_status_display(), "badge": badge.get(r.status, "muted"),
            "description": r.description,
        } for r in reqs.order_by("-created_at")[:30]],
    }


def member_events(member):
    now = timezone.now()
    regs = member.event_registrations.select_related("event", "event__event_type",
                                                     "event__region")
    joined_ids = set(regs.values_list("event_id", flat=True))
    upcoming = Event.objects.filter(is_public=True, start_at__gte=now).order_by("start_at")
    return {
        "kpis": [
            {"label": "Nilizojiandikisha", "value": num(regs.count()), "icon": "calendar-check",
             "tint": "green"},
            {"label": "Nilizohudhuria", "value": num(regs.filter(attended=True).count()),
             "icon": "check-circle", "tint": "navy"},
            {"label": "Matukio Yanayokuja", "value": num(upcoming.count()), "icon": "clock",
             "tint": "gold"},
        ],
        "upcoming": [{
            "id": e.pk, "title": e.tx("title"), "venue": e.tx("venue"),
            "d": e.start_at.strftime("%d"), "m": MONTHS_SHORT_UP[e.start_at.month - 1],
            "time": e.start_at.strftime("%I:%M %p"),
            "place": e.region.name if e.region else "—",
            "scene": e.scene, "joined": e.pk in joined_ids,
            "days": _("Siku %(n)d") % {"n": max(e.days_until, 0)},
        } for e in upcoming[:8]],
        "mine": [{
            "title": r.event.tx("title"),
            "date": r.event.start_at.strftime("%d/%m/%Y %I:%M %p"),
            "place": r.event.region.name if r.event.region else "—",
            "attended": r.attended,
            "status": r.event.get_status_display(), "badge": r.event.badge,
        } for r in regs.order_by("-event__start_at")[:30]],
    }


def member_notices(member):
    from content.models import Notification
    return {
        "notifications": [{
            "title": n.title, "body": n.body, "icon": n.icon, "tint": n.tint,
            "url": n.url, "date": n.created_at.strftime("%d %b %Y %I:%M %p"),
        } for n in Notification.objects.filter(member=member)[:20]],
        "announcements": [{
            "title": a.tx("title"), "body": a.tx("body"), "icon": a.icon, "tint": a.tint,
            "date": a.published_on.strftime("%d %B %Y"),
        } for a in Announcement.objects.filter(is_active=True, status="approved")[:10]],
        "news": [{
            "title": n.tx("title"), "text": n.tx("summary"), "scene": n.scene,
            "date": n.published_on.strftime("%d %B %Y"),
        } for n in News.objects.filter(is_published=True)[:6]],
    }


# ===========================================================================
#  AFISA — maelezo ya mwanachama na ustawi
# ===========================================================================
def member_detail(member):
    account, _created = Account.objects.get_or_create(member=member)
    pays = member.payments.all()
    cons = member.contributions.select_related("fund")
    card = member.cards.filter(is_active=True).first()
    return {
        "m": member,
        "card": card,
        "kpis": [
            {"label": "Salio la Akaunti", "value": tzs(account.balance()), "icon": "wallet",
             "tint": "green", "money": True},
            {"label": "Ada Zilizolipwa",
             "value": tzs(confirmed(pays).aggregate(s=Sum("amount"))["s"] or 0),
             "icon": "cash", "tint": "navy", "money": True},
            {"label": "Michango",
             "value": tzs(confirmed(cons).aggregate(s=Sum("amount"))["s"] or 0),
             "icon": "hand-heart", "tint": "gold", "money": True},
            {"label": "Pointi", "value": num(PointTransaction.balance(member)),
             "icon": "star", "tint": "purple"},
        ],
        "payments": [{
            "receipt": p.receipt_no, "amount": num(p.amount),
            "date": p.paid_at.strftime("%d/%m/%Y"), "method": p.method_label,
            "status": p.get_status_display(), "badge": p.badge, "id": p.pk,
            "pending": p.status == PaymentStatus.PENDING,
        } for p in pays.order_by("-paid_at")[:15]],
        "contributions": [{
            "receipt": c.receipt_no, "fund": c.fund.tx("name"), "amount": num(c.amount),
            "date": c.received_at.strftime("%d/%m/%Y"),
            "status": c.get_status_display(), "badge": c.badge,
        } for c in cons.order_by("-received_at")[:15]],
        "family": member.family.all(),
        "beneficiaries": member.beneficiaries.all(),
        "assistance": [{
            "ref": r.reference, "type": r.assistance_type.tx("name"),
            "requested": num(r.amount_requested), "approved": num(r.amount_approved),
            "status": r.get_status_display(),
        } for r in member.assistance_requests.select_related("assistance_type")[:10]],
        "events": [{
            "title": r.event.tx("title"), "date": r.event.start_at.strftime("%d/%m/%Y"),
            "attended": r.attended,
        } for r in member.event_registrations.select_related("event")[:10]],
    }


def assistance_review(qs):
    badge = {"pending": "warn", "review": "info", "approved": "ok",
             "rejected": "danger", "paid": "ok"}
    all_r = AssistanceRequest.objects.all()
    return {
        "kpis": [
            {"label": "Maombi Yote", "value": num(all_r.count()), "icon": "hand-heart",
             "tint": "green"},
            {"label": "Yanayosubiri",
             "value": num(all_r.filter(status__in=["pending", "review"]).count()),
             "icon": "clock", "tint": "gold"},
            {"label": "Yaliyoidhinishwa",
             "value": num(all_r.filter(status__in=["approved", "paid"]).count()),
             "icon": "check-circle", "tint": "navy"},
            {"label": "Kiasi Kilichoidhinishwa",
             "value": tzs(all_r.aggregate(s=Sum("amount_approved"))["s"] or 0),
             "icon": "wallet", "tint": "teal", "money": True},
        ],
        "rows": [{
            "id": r.pk, "ref": r.reference, "member": r.member.full_name,
            "membership_no": r.member.membership_no,
            "type": r.assistance_type.tx("name"),
            "requested": num(r.amount_requested), "requested_raw": r.amount_requested,
            "approved": num(r.amount_approved),
            "date": r.created_at.strftime("%d/%m/%Y"),
            "status": r.get_status_display(), "badge": badge.get(r.status, "muted"),
            "pending": r.status in ("pending", "review"),
            "description": r.description,
        } for r in qs.order_by("-created_at")[:50]],
        "total": qs.count(),
        "statuses": AssistanceRequest.STATUS,
    }


# ===========================================================================
#  MRATIBU WA MKOA — data za mkoa wake pekee
# ===========================================================================
def coordinator(region, year=None):
    """
    Dashibodi ya mratibu. Kila kitu kimefungwa kwenye mkoa wake mmoja.

    `region` ikiwa None (mratibu hajapangiwa mkoa), inarudisha muundo tupu
    badala ya kuvunjika.
    """
    from geo.models import District
    year = year or timezone.localdate().year
    this_m, _unused = _month_bounds(0)
    prev_m, _unused2 = _month_bounds(1)

    if region is None:
        return {"region_name": "—", "no_region": True, "kpis": [], "districts": [],
                "members_month": {"labels": MONTHS, "data": [0] * 12},
                "revenue_month": {"labels": MONTHS, "data": [0] * 12},
                "by_category": {"id": "chCoCat", "title": "Aina za Wanachama",
                                "center_value": "0", "center_label": "Jumla", "rows": []},
                "recent_members": [], "applications": [], "events": [],
                "payments": [], "activities": [], "actions": []}

    members = Member.objects.filter(region=region)
    total = members.count()
    new_this = members.filter(joined_on__gte=this_m).count()
    new_prev = members.filter(joined_on__gte=prev_m, joined_on__lt=this_m).count()
    apps = Application.objects.filter(region=region)
    pending = apps.filter(status__in=[ApplicationStatus.PENDING,
                                      ApplicationStatus.REVIEW]).count()

    pay = confirmed(Payment.objects.filter(member__region=region))
    fees_month = pay.filter(paid_at__date__gte=this_m).aggregate(s=Sum("amount"))["s"] or 0
    fees_prev = pay.filter(paid_at__date__gte=prev_m,
                           paid_at__date__lt=this_m).aggregate(s=Sum("amount"))["s"] or 0
    cons = confirmed(Contribution.objects.filter(member__region=region))
    cons_year = cons.filter(received_at__year=year).aggregate(s=Sum("amount"))["s"] or 0

    d1, dir1 = delta(new_this, new_prev or 1)
    d2, dir2 = delta(fees_month, fees_prev)

    # -- Mgawanyo kwa wilaya --
    counts = {r["district_id"]: r["n"]
              for r in members.values("district_id").annotate(n=Count("id"))}
    pay_by_d = {r["member__district_id"]: r["s"]
                for r in pay.values("member__district_id").annotate(s=Sum("amount"))}
    dmax = max(counts.values()) if counts else 1
    districts = [{
        "name": d.name, "members": num(counts.get(d.pk, 0)),
        "value": counts.get(d.pk, 0),
        "fees": tzs(pay_by_d.get(d.pk, 0)),
        "pct": round(counts.get(d.pk, 0) / dmax * 100) if dmax else 0,
    } for d in District.objects.filter(region=region)]
    districts.sort(key=lambda x: -x["value"])

    # -- Kategoria --
    cat_counts = {r["category_id"]: r["n"]
                  for r in members.values("category_id").annotate(n=Count("id"))}
    cat_rows = []
    for c in Category.objects.all():
        n = cat_counts.get(c.pk, 0)
        if n:
            cat_rows.append({"label": c.name, "value": n, "display": num(n),
                             "pct": pct(n, total or 1),
                             "color": cat_colour(c)})
    cat_rows.sort(key=lambda r: -r["value"])

    events = Event.objects.filter(region=region)
    return {
        "region_name": region.name,
        "no_region": False,
        "kpis": [
            {"label": "Wanachama Mkoani", "value": num(total), "icon": "users",
             "tint": "green", "note": region.name},
            {"label": "Wanachama Wapya", "value": num(new_this), "icon": "user-plus",
             "tint": "navy", "delta": d1, "dir": dir1, "note": "Mwezi Huu"},
            {"label": "Maombi Yanayosubiri", "value": num(pending), "icon": "clock",
             "tint": "orange", "note": "Inasubiri idhini"},
            {"label": "Ada Zilizokusanywa (Mwezi Huu)", "value": tzs(fees_month),
             "icon": "wallet", "tint": "green", "money": True,
             "delta": d2, "dir": dir2, "note": "Ikilinganishwa na mwezi jana"},
            {"label": "Michango (Mwaka Huu)", "value": tzs(cons_year), "icon": "hand-heart",
             "tint": "gold", "money": True, "note": _("Mwaka %(y)d") % {"y": year}},
            {"label": "Wilaya Zinazohusika", "value": num(len(districts)),
             "icon": "map-pin", "tint": "teal", "note": region.name},
        ],
        "districts": districts,
        "members_month": {"labels": MONTHS,
                          "data": _cumulative(monthly_series(members, "joined_on", year=year),
                                              total)},
        "revenue_month": {"labels": MONTHS,
                          "data": monthly_series(pay, "paid_at", "amount", year)},
        "by_category": {"id": "chCoCat", "title": "Aina za Wanachama",
                        "center_value": num(total), "center_label": "Jumla",
                        "rows": cat_rows},
        "recent_members": [{
            "name": m.full_name, "initials": m.initials, "no": m.membership_no,
            "category": m.category.name, "district": m.district.name if m.district else "—",
            "joined": m.joined_on.strftime("%d %b %Y"), "id": m.pk,
        } for m in members.select_related("category", "district").order_by("-created_at")[:6]],
        "applications": [{
            "ref": a.reference, "name": a.full_name,
            "district": a.district.name if a.district else "—",
            "date": a.created_at.strftime("%d/%m/%Y"),
            "status": a.get_status_display(), "badge": a.badge,
        } for a in apps.select_related("district").order_by("-created_at")[:6]],
        "events": [{
            "title": e.tx("title"), "venue": e.tx("venue"),
            "d": e.start_at.strftime("%d"), "m": MONTHS_SHORT_UP[e.start_at.month - 1],
            "time": e.start_at.strftime("%I:%M %p"),
            "status": e.get_status_display(), "badge": e.badge,
            "participants": num(e.participant_count()),
        } for e in events.order_by("-start_at")[:5]],
        "payments": [{
            "receipt": p.receipt_no, "name": p.member.full_name,
            "amount": num(p.amount), "date": p.paid_at.strftime("%d/%m/%Y"),
            "status": p.get_status_display(), "badge": p.badge,
        } for p in Payment.objects.filter(member__region=region)
                                  .select_related("member").order_by("-paid_at")[:6]],
        "activities": [
            {"title": "Wanachama wapya mwezi huu", "sub": f"{new_this} {region.name}",
             "time": "Mwezi Huu", "icon": "user-plus", "tint": "green"},
            {"title": "Maombi yanayosubiri", "sub": f"{pending} maombi",
             "time": "Sasa", "icon": "clock", "tint": "orange"},
            {"title": "Matukio ya mkoa", "sub": f"{events.count()} matukio",
             "time": str(year), "icon": "calendar", "tint": "navy"},
        ],
        "actions": [
            {"label": "Sajili Mwanachama", "icon": "user-plus", "tint": "green", "url": "/usajili/"},
            {"label": "Maombi ya Mkoa", "icon": "file", "tint": "navy", "url": "/maombi/"},
            {"label": "Wanachama wa Mkoa", "icon": "users", "tint": "purple", "url": "/wanachama/"},
            {"label": "Matukio ya Mkoa", "icon": "calendar", "tint": "gold", "url": "/matukio/"},
            {"label": "Pakua Ripoti ya Mkoa", "icon": "download", "tint": "teal",
             "url": "/pakua/wanachama/"},
            {"label": "Malipo ya Mkoa", "icon": "wallet", "tint": "orange", "url": "/malipo/"},
        ],
    }


# ===========================================================================
#  MRATIBU — takwimu za kanda moja
# ===========================================================================
def zone_dashboard(zone, year=None):
    """Dashibodi ya kanda: mikoa yake tu."""
    year = year or timezone.localdate().year
    region_ids = list(zone.regions.values_list("pk", flat=True))
    this_m, _unused = _month_bounds(0)
    prev_m, _unused = _month_bounds(1)

    members = Member.objects.filter(region_id__in=region_ids)
    total = members.count()
    new_this = members.filter(joined_on__gte=this_m).count()
    new_prev = members.filter(joined_on__gte=prev_m, joined_on__lt=this_m).count()
    apps = Application.objects.filter(region_id__in=region_ids)
    pending = apps.filter(status__in=[ApplicationStatus.PENDING,
                                      ApplicationStatus.REVIEW]).count()

    pay = confirmed(Payment.objects.filter(member__region_id__in=region_ids))
    fees_month = pay.filter(paid_at__date__gte=this_m).aggregate(s=Sum("amount"))["s"] or 0
    fees_prev = pay.filter(paid_at__date__gte=prev_m,
                           paid_at__date__lt=this_m).aggregate(s=Sum("amount"))["s"] or 0
    cons = confirmed(Contribution.objects.filter(member__region_id__in=region_ids))
    cons_year = cons.filter(received_at__year=year).aggregate(s=Sum("amount"))["s"] or 0
    events = Event.objects.filter(region_id__in=region_ids)

    d2, dir2 = delta(new_this, new_prev or 1)
    d4, dir4 = delta(fees_month, fees_prev)

    # -- Mikoa ya kanda --
    counts = {r["region_id"]: r["n"]
              for r in members.values("region_id").annotate(n=Count("id"))}
    fee_by_region = {r["member__region_id"]: r["s"] for r in
                     pay.values("member__region_id").annotate(s=Sum("amount"))}
    regions_qs = zone.regions.all()
    rmax = max(counts.values()) if counts else 1
    region_rows = [{
        "name": r.name, "value": counts.get(r.pk, 0), "display": num(counts.get(r.pk, 0)),
        "pct": round(counts.get(r.pk, 0) / (rmax or 1) * 100),
        "fees": tzs(fee_by_region.get(r.pk, 0)),
        "districts": r.districts.count(),
    } for r in regions_qs]
    region_rows.sort(key=lambda x: -x["value"])

    # Ramani inaonyesha mikoa ya kanda pekee
    regions_map = [{"name": r.name, "members": counts.get(r.pk, 0),
                    "x": r.map_x, "y": r.map_y} for r in regions_qs]

    # -- Kategoria --
    cat_counts = {r["category_id"]: r["n"]
                  for r in members.values("category_id").annotate(n=Count("id"))}
    cat_rows = []
    for c in Category.objects.all():
        n = cat_counts.get(c.pk, 0)
        if n:
            cat_rows.append({"label": c.name, "value": n, "display": num(n),
                             "pct": pct(n, total or 1),
                             "color": cat_colour(c)})
    cat_rows.sort(key=lambda r: -r["value"])

    from geo.models import District
    return {
        "kpis": [
            {"label": "Wanachama wa Kanda", "value": num(total), "icon": "users",
             "tint": "green", "note": zone.tx("name")},
            {"label": "Wanachama Wapya", "value": num(new_this), "icon": "user-plus",
             "tint": "navy", "delta": d2, "dir": dir2, "note": "Mwezi Huu"},
            {"label": "Maombi Yanayosubiri", "value": num(pending), "icon": "clock",
             "tint": "orange", "note": "Inasubiri idhini"},
            {"label": "Ada Zilizokusanywa (Mwezi Huu)", "value": tzs(fees_month),
             "icon": "wallet", "tint": "green", "money": True,
             "delta": d4, "dir": dir4, "note": "Ikilinganishwa na mwezi jana"},
            {"label": "Michango ya Mwaka", "value": tzs(cons_year), "icon": "hand-heart",
             "tint": "gold", "money": True, "note": _("Mwaka %(y)d") % {"y": year}},
            {"label": "Matukio ya Kanda", "value": num(events.count()), "icon": "calendar",
             "tint": "purple", "note": zone.tx("name")},
        ],
        "summary": [
            {"label": "Mikoa", "value": num(regions_qs.count()), "icon": "map"},
            {"label": "Halmashauri",
             "value": num(District.objects.filter(region_id__in=region_ids).count()),
             "icon": "map-pin"},
            {"label": "Wanachama Hai",
             "value": num(members.filter(status=MemberStatus.ACTIVE).count()), "icon": "users"},
            {"label": "Matawi",
             "value": num(Branch.objects.filter(region_id__in=region_ids).count()),
             "icon": "briefcase"},
            {"label": "Ofisi ya Kanda", "value": zone.office or "—", "icon": "map-pin"},
        ],
        "members_month": {"labels": MONTHS,
                          "data": _cumulative(monthly_series(members, "joined_on", year=year), total)},
        "revenue_month": {"labels": MONTHS,
                          "data": monthly_series(pay, "paid_at", "amount", year)},
        "by_category": {"id": "chZoneCat", "title": "Aina za Wanachama",
                        "center_value": num(total), "center_label": "Jumla", "rows": cat_rows},
        "region_rows": region_rows,
        "regions": regions_map,
        "events": [{"title": e.tx("title"), "date": e.start_at.strftime("%d/%m/%Y"),
                    "place": e.region.name if e.region else "—",
                    "status": e.get_status_display(), "badge": e.badge}
                   for e in events.order_by("-start_at")[:6]],
        "recent": [{"initials": m.initials, "name": m.full_name,
                    "place": m.region.name if m.region else "—",
                    "category": m.category.name,
                    "joined": m.joined_on.strftime("%d %b %Y")}
                   for m in members.order_by("-created_at")[:6]],
        "applications": [{"ref": a.reference, "name": a.full_name,
                          "place": a.region.name if a.region else "—",
                          "status": a.get_status_display(), "badge": a.badge}
                         for a in apps.order_by("-created_at")[:6]],
        "actions": [
            {"label": "Wanachama wa Kanda", "icon": "users", "tint": "green",
             "url": "/kanda/wanachama/"},
            {"label": "Mikoa na Halmashauri", "icon": "map", "tint": "navy",
             "url": "/kanda/mikoa/"},
            {"label": "Maombi", "icon": "file", "tint": "purple", "url": "/maombi/"},
            {"label": "Matukio", "icon": "calendar", "tint": "gold", "url": "/matukio/"},
            {"label": "Pakua Ripoti", "icon": "download", "tint": "teal",
             "url": "/pakua/wanachama/"},
        ],
    }


def zone_regions(zone):
    """Mikoa yote ya kanda pamoja na halmashauri na kata zake."""
    from geo.models import District, Ward
    region_ids = list(zone.regions.values_list("pk", flat=True))
    member_counts = {r["region_id"]: r["n"] for r in
                     Member.objects.filter(region_id__in=region_ids)
                     .values("region_id").annotate(n=Count("id"))}
    rows = []
    for r in zone.regions.prefetch_related("districts"):
        districts = list(r.districts.all())
        rows.append({
            "name": r.name,
            "members": num(member_counts.get(r.pk, 0)),
            "districts": [{"name": d.name, "kind": d.get_kind_display(),
                           "code": d.kind, "wards": d.wards.count()}
                          for d in districts],
            "district_count": len(districts),
            "ward_count": Ward.objects.filter(district__region=r).count(),
        })
    return {
        "rows": rows,
        "totals": {
            "regions": len(rows),
            "districts": District.objects.filter(region_id__in=region_ids).count(),
            "wards": Ward.objects.filter(district__region_id__in=region_ids).count(),
            "members": num(sum(member_counts.values())),
        },
    }


def broadcast_page(region_ids=None):
    """Takwimu za ukurasa wa kutuma ujumbe."""
    from content.models import MessageLog
    from members.models import MemberStatus
    members = Member.objects.all()
    if region_ids is not None:
        members = members.filter(region_id__in=region_ids)
    active = members.filter(status=MemberStatus.ACTIVE)
    with_email = active.exclude(email="").count()
    with_phone = active.exclude(phone="").count()
    logs = MessageLog.objects.all()[:15]
    return {
        "kpis": [
            {"label": "Wanachama Hai", "value": num(active.count()), "icon": "users",
             "tint": "green"},
            {"label": "Wenye Barua Pepe", "value": num(with_email), "icon": "mail",
             "tint": "navy"},
            {"label": "Wenye Namba ya Simu", "value": num(with_phone), "icon": "phone",
             "tint": "gold"},
            {"label": "Ujumbe Uliotumwa", "value": num(MessageLog.objects.count()),
             "icon": "message", "tint": "teal"},
        ],
        "logs": [{
            "channel": l.get_channel_display(), "subject": l.subject,
            "recipients": num(l.recipients), "status": l.get_status_display(),
            "badge": {"sent": "ok", "delivered": "ok", "queued": "warn",
                      "failed": "danger"}.get(l.status, "muted"),
            "by": l.sent_by.get_full_name() if l.sent_by else "—",
            "date": l.created_at.strftime("%d/%m/%Y %I:%M %p"),
        } for l in logs],
    }


def public_gallery(album_slug=None, page=1, per_page=24):
    """Maktaba ya picha na video kwa umma."""
    albums = Album.objects.filter(is_public=True)
    items = MediaItem.objects.filter(album__is_public=True).select_related("album")
    active = None
    if album_slug:
        active = albums.filter(pk=album_slug).first() if str(album_slug).isdigit() else None
        if active:
            items = items.filter(album=active)

    total = items.count()
    pages = max((total + per_page - 1) // per_page, 1)
    page = min(max(page, 1), pages)
    rows = items.order_by("-uploaded_on", "-id")[(page - 1) * per_page: page * per_page]

    return {
        "hero": {"eyebrow": "Picha na Video", "scene": "sadaka",
                 "title": "Maktaba ya Picha na Video",
                 "text": "Shughuli, miradi na matukio ya MUWESTA katika picha."},
        "albums": [{"id": a.pk, "name": a.tx("name"), "count": a.item_count(),
                    "scene": a.scene, "active": bool(active and active.pk == a.pk)}
                   for a in albums],
        "active_album": {"id": active.pk, "name": active.tx("name")} if active else None,
        "items": [{"title": m.tx("title"), "kind": m.kind, "scene": m.scene,
                   "album": m.album.tx("name") if m.album else "",
                   "date": m.uploaded_on.strftime("%d %B %Y"),
                   "duration": m.duration, "url": m.file.url if m.file else ""}
                  for m in rows],
        "total": total, "page": page, "pages": pages,
        **page_meta(page, pages, per_page, total),
    }


# ===========================================================================
#  VIFURUSHI VYA UANACHAMA
# ===========================================================================
def public_vifurushi():
    """
    Mpangilio rasmi wa vifurushi. Data yote inatoka `members.Category`
    ili bango na tovuti visitofautiane.
    """
    from members.models import Category

    # Kigezo ni ada ya usajili: madaraja ya urithi (mfano Founder) na
    # yaliyostaafishwa yana 0, kwa hiyo hayaonekani hapa.
    tiers = list(Category.objects.filter(is_special=False, registration_fee__gt=0)
                 .order_by("order", "registration_fee"))

    #: Kila safu ya jedwali. `kind` inaamua jinsi seli inavyochorwa.
    rows = [
        {"label": "Kadi ya Uanachama", "icon": "id-card", "kind": "bool", "attr": "has_card"},
        {"label": "Ada ya Usajili (Mara moja)", "icon": "coins", "kind": "money",
         "attr": "registration_fee"},
        {"label": "Ada ya Mwezi (TSh)", "icon": "wallet", "kind": "money", "attr": "monthly_fee"},
        {"label": "Ada ya Mwaka (TSh)", "icon": "calendar-check", "kind": "money",
         "attr": "annual_fee", "hide_if_zero": True},
        {"label": "Muda wa Uanachama", "icon": "calendar", "kind": "years",
         "attr": "duration_years"},
        {"label": "Matukio na Mafunzo", "icon": "users", "kind": "bool", "attr": "has_events"},
        {"label": "Ripoti na Taarifa", "icon": "file", "kind": "bool", "attr": "has_reports"},
        {"label": "Huduma za Kipaumbele", "icon": "headset", "kind": "bool",
         "attr": "has_priority"},
        {"label": "Cheti cha Shukrani", "icon": "receipt", "kind": "bool",
         "attr": "has_certificate"},
        {"label": "Fursa za Uongozi", "icon": "user-check", "kind": "bool",
         "attr": "has_leadership"},
        {"label": "Alama za Utambuzi / Poini", "icon": "star", "kind": "points",
         "attr": "recognition_points"},
    ]

    table = []
    for row in rows:
        # Safu inayoruhusiwa kufichwa haionekani kama kila daraja lina 0.
        if row.get("hide_if_zero") and not any(getattr(t, row["attr"]) for t in tiers):
            continue
        cells = []
        for tier in tiers:
            value = getattr(tier, row["attr"])
            if row["kind"] == "bool":
                cells.append({"bool": bool(value)})
            elif row["kind"] == "money":
                cells.append({"text": f"{value:,.0f}"})
            elif row["kind"] == "years":
                cells.append({"text": gettext("Mwaka %(n)d") % {"n": value}
                              if value == 1 else gettext("Miaka %(n)d") % {"n": value}})
            else:  # points
                cells.append({"text": f"{value:,.0f}" + ("+" if tier.points_plus else "")})
        table.append({"label": row["label"], "icon": row["icon"], "cells": cells})

    return {
        "hero": {"eyebrow": "Vifurushi na Ada", "scene": "sadaka",
                 "title": "Mpangilio wa Kifurushi cha Malipo ya Mwanachama",
                 "text": "Chagua kifurushi kinachokufaa. Ada ya usajili hulipwa "
                         "mara moja tu; ada ya mwaka hulipwa kila mwaka."},
        "tiers": [{"obj": t, "name": t.tx("name"), "colour": t.colour,
                   "featured": t.is_featured, "benefits": t.benefit_list()}
                  for t in tiers],
        "table": table,
        "benefits": [
            {"icon": "users", "text": "Kushiriki katika miradi ya kijamii"},
            {"icon": "mail", "text": "Kupata taarifa za kila mwezi"},
            {"icon": "target", "text": "Kipaumbele katika huduma na programu"},
            {"icon": "hand-heart", "text": "Kuchangia maendeleo ya jamii"},
            {"icon": "user-check", "text": "Kujenga uhusiano na wanachama wengine"},
        ],
        "notes": [
            "Ada ya usajili hulipwa mara moja tu.",
            "Ada ya mwaka hulipwa kila mwaka.",
            "Mwanachama ana haki zote kulingana na kifurushi alichochagua.",
            "Malipo yote ni kwa shilingi za Kitanzania (TSh).",
        ],
        "methods": [
            {"icon": "building", "label": "Benki"},
            {"icon": "phone", "label": "M-Pesa"},
            {"icon": "phone", "label": "Airtel Money"},
            {"icon": "phone", "label": "Tigo Pesa"},
            {"icon": "phone", "label": "HaloPesa"},
        ],
        "special": [{"name": c.tx("name"), "colour": c.colour,
                     "benefits": c.benefit_list()}
                    for c in Category.objects.filter(is_special=True)],
    }


#: Hero ya ukurasa wa kuchangia — hakuna data ya database inayohitajika.
CHANGIA_HERO = {
    "eyebrow": "Changia",
    "scene": "sadaka",
    "title": "Changia Sasa — Bila Hata Kufungua Akaunti",
    "text": "Mchango wako unaenda moja kwa moja kwenye elimu, afya, maji "
            "safi na msaada wa dharura. Jaza fomu hii kwa dakika moja.",
}


# ===========================================================================
#  LIPA ADA YA UANACHAMA
# ===========================================================================
def public_lipa(lang="sw"):
    """
    Data ya ukurasa wa kulipa ada. Bei zote zinatokana na
    `Category.monthly_fee` ili kusiwe na namba zilizoandikwa mkononi.
    """
    from members.models import Category

    tiers = list(Category.objects.filter(is_special=False, registration_fee__gt=0)
                 .order_by("order", "registration_fee"))

    packages = []
    for t in tiers:
        packages.append({
            "code": t.code, "name": t.tx("name"), "colour": t.colour,
            "featured": t.is_featured,
            "monthly": t.monthly_fee,
            "registration": t.registration_fee,
            "benefits": t.benefit_list()[:4],
            # Bei kwa vifungo vya haraka. Miezi mingine huhesabiwa
            # papo hapo na JavaScript kutoka `monthly`.
            "prices": {str(m): _g.months_price(t.monthly_fee, m)
                       for m in _g.MONTH_SHORTCUTS},
        })

    return {
        "packages": packages,
        "month_shortcuts": [
            {"months": m, "label": _g.months_label(m, lang),
             "discount": _g.discount_for(m)}
            for m in _g.MONTH_SHORTCUTS
        ],
        "pay_kinds": _g.localise(_g.PAY_KINDS, lang),
        "term_years": _g.TERM_YEARS,
        "min_months": _g.MIN_MONTHS,
        "max_months": _g.MAX_MONTHS,
        "payer_types": _g.localise(_g.PAYER_TYPES, lang),
        "purposes": _g.localise(_g.PURPOSES, lang),
        "providers": _g.localise(_g.PROVIDERS, lang),
        "provider_groups": _g.localise(_g.PROVIDER_GROUPS, lang),
        "currencies": _g.CURRENCIES,
        "steps": [
            {"n": 1, "name": "Chagua",    "name_en": "Select"},
            {"n": 2, "name": "Taarifa",   "name_en": "Details"},
            {"n": 3, "name": "Malipo",    "name_en": "Payment"},
            {"n": 4, "name": "Thibitisha", "name_en": "Confirm"},
        ] if not str(lang).startswith("en") else [
            {"n": 1, "name": "Select"}, {"n": 2, "name": "Details"},
            {"n": 3, "name": "Payment"}, {"n": 4, "name": "Confirm"},
        ],
        "trust": [
            {"icon": "shield",      "title": "Salama na Kuaminika", "text": "Usimbaji wa SSL"},
            {"icon": "receipt",     "title": "Risiti ya Papo Hapo", "text": "Uthibitisho kwa barua pepe"},
            {"icon": "chart-line",  "title": "Uwazi",               "text": "Ripoti za matumizi"},
            {"icon": "headset",     "title": "Msaada",              "text": "+255 769 600 102"},
        ],
    }


# ===========================================================================
#  MATANGAZO YA UMMA
# ===========================================================================
def live_announcements(limit=6):
    """Matangazo yaliyoidhinishwa pekee. Ya dharura yanatangulia."""
    return list(Announcement.objects
                .filter(is_active=True, status="approved", audience__in=["all", "members"])
                .order_by("-is_urgent", "-published_on", "-id")[:limit])


# ===========================================================================
#  MHISANI — shughuli za kuchangia na mwaliko wa uanachama
# ===========================================================================
def donor_causes(limit=4):
    """
    Shughuli ambazo mhisani anaweza kuzichangia sasa hivi.

    Kampeni hai zinatangulia kwa sababu zina muda wa mwisho; miradi
    inayoendelea inajaza nafasi zilizobaki. Zilizofikia lengo zinaachwa —
    hakuna maana ya kumwomba mtu achangie kilichokamilika.
    """
    today = timezone.localdate()
    rows = []

    for c in (Campaign.objects.filter(is_active=True, end_date__gte=today)
              .select_related("fund")[:limit]):
        rows.append({
            "kind": "campaign", "id": c.pk,
            "title": c.tx("title"), "summary": c.tx("summary"),
            "target": tzs(c.target_amount), "progress": c.progress_bar(),
            "days_left": c.days_left(),
            "colour": (c.fund.colour if c.fund else "") or "#12864a",
            "url": f"/changia/?aina=jumla",
        })

    if len(rows) < limit:
        for p in (Project.objects.filter(status="ongoing")
                  .order_by("-created_at")[:limit - len(rows)]):
            if p.progress() >= 100:
                continue
            rows.append({
                "kind": "project", "id": p.pk,
                "title": p.tx("title"), "summary": p.tx("summary"),
                "target": tzs(p.target_amount), "progress": p.progress_bar(),
                "days_left": None, "colour": "#12864a",
                "url": f"/changia/?aina=maendeleo",
            })

    return rows


def membership_invite(lang="sw"):
    """
    Maelezo ya kumshawishi mhisani kujiunga — bila kumlazimisha.

    Bei inatoka kwenye database (`Category`), si kwenye maandishi
    yaliyoandikwa mkononi, ili isipitwe na wakati ada zikibadilika.
    """
    from members.models import Category

    cat = (Category.objects.filter(is_special=False, is_selectable=True)
           .order_by("monthly_fee").first())
    if cat is None:
        return None

    term_price = _g.months_price(cat.monthly_fee, 12)
    return {
        "cheapest": cat.tx("name"),
        "price": tzs(term_price),
        "registration": tzs(cat.registration_fee),
        "years": 1,
        "points": [
            _("Kadi ya uanachama yenye QR — utambulisho rasmi wa MUWESTA."),
            _("Haki ya kupiga kura kwenye Mkutano Mkuu."),
            _("Huduma za ustawi kwako na familia yako."),
            _("Pointi za utambuzi kwa kila mchango unaotoa."),
            _("Ripoti za ndani na mialiko ya matukio ya wanachama."),
        ],
    }
