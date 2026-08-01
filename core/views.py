"""
Views za frontend prototype.

Kila view inachukua data kutoka `core.data` (mock) na kuipeleka kwenye template.
Kubadilisha kwenda backend: badilisha `data.xxx()` kuwa ORM queries.
Muundo wa context hautabadilika, kwa hiyo templates hazitaguswa.
"""
from django.shortcuts import render

from . import data
from .data import dashboards as dash, outreach as out, navs, pages as pg


def _shell(**kw):
    """Vitu vinavyorudia kwenye kila dashboard."""
    base = {
        "verse": data.verse(0),
        "notif_count": 8,
        "msg_count": 3,
        "show_search": False,
    }
    base.update(kw)
    return base


# ---------------------------------------------------------------------------
#  TOVUTI YA UMMA
# ---------------------------------------------------------------------------
def _pub(key, extra=None):
    ctx = {"site_menu": pg.menu(), "page_key": key, "roles": data.ROLES}
    if extra:
        ctx.update(extra)
    return ctx


def home(request):
    return render(request, "public/home.html", _pub("home", out.public_site()))


def kuhusu(request):
    return render(request, "public/kuhusu.html", _pub("kuhusu", pg.kuhusu()))


def uanachama(request):
    return render(request, "public/uanachama.html", _pub("uanachama", pg.uanachama()))


def huduma(request):
    return render(request, "public/huduma.html", _pub("huduma", pg.huduma()))


def habari(request):
    return render(request, "public/habari.html", _pub("habari", pg.habari()))


def matukio_umma(request):
    return render(request, "public/matukio.html", _pub("matukio", pg.matukio_umma()))


def mawasiliano(request):
    return render(request, "public/mawasiliano.html", _pub("mawasiliano", pg.mawasiliano()))


def jiunge(request):
    return render(request, "public/jiunge.html", _pub("uanachama", pg.jiunge()))


def login(request):
    return render(request, "public/login.html", _pub("", {}))


# ---------------------------------------------------------------------------
#  MSIMAMIZI MKUU — TAIFA
# ---------------------------------------------------------------------------
def national(request):
    ctx = dash.national()
    ctx.update(_shell(
        nav=navs.national("dashboard"),
        topbar_title="MWST Membership Management System",
        topbar_sub="Dashboard - Msimamizi Mkuu (Mikoa Yote za Tanzania)",
        user_name="Ali H. Suleiman", user_role="Msimamizi Mkuu", user_initials="AS",
        notif_count=12,
        map_regions=data.tz_map(ctx["regions"]),
        map_legend=data.MAP_LEGEND,
    ))
    return render(request, "admin_panel/national.html", ctx)


# ---------------------------------------------------------------------------
#  AFISA USAJILI
# ---------------------------------------------------------------------------
def usajili(request):
    ctx = dash.usajili()
    ctx.update(_shell(
        nav=navs.usajili("usajili"),
        topbar_title="MWST Membership Management System",
        topbar_sub="Dashboard > Usajili wa Mwanachama",
        user_name="Ali H. Suleiman", user_role="Afisa Usajili", user_initials="AS",
        notif_count=5,
    ))
    return render(request, "admin_panel/usajili.html", ctx)


# ---------------------------------------------------------------------------
#  AFISA MALIPO YA ADA
# ---------------------------------------------------------------------------
def malipo(request):
    ctx = dash.malipo()
    ctx.update(_shell(
        nav=navs.malipo("malipo-muhtasari"),
        topbar_title="MWST Membership Management System",
        topbar_sub="Dashboard / Malipo ya Ada",
        user_name="Ali H. Suleiman", user_role="Afisa Malipo ya Ada", user_initials="AS",
        notif_count=6,
    ))
    return render(request, "admin_panel/malipo.html", ctx)


# ---------------------------------------------------------------------------
#  AFISA MICHANGO
# ---------------------------------------------------------------------------
def michango(request):
    ctx = dash.michango()
    ctx.update(_shell(
        nav=navs.michango("michango-muhtasari"),
        topbar_title="MWST Membership Management System",
        topbar_sub="Dashboard / Michango",
        user_name="Ali H. Suleiman", user_role="Afisa Michango", user_initials="AS",
        notif_count=6,
    ))
    return render(request, "admin_panel/michango.html", ctx)


# ---------------------------------------------------------------------------
#  WADAU NA WAHISANI
# ---------------------------------------------------------------------------
def wadau(request):
    ctx = out.wadau()
    ctx.update(_shell(
        nav=navs.outreach("dashboard"),
        verse=data.verse(1),
        show_search=True, search_placeholder="Tafuta...",
        user_name="Admin MWST", user_role="Msimamizi Mkuu", user_initials="AM",
        notif_count=7, msg_count=3,
        map_regions=data.tz_map(ctx["regions"]),
    ))
    return render(request, "admin_panel/wadau.html", ctx)


# ---------------------------------------------------------------------------
#  MATUKIO
# ---------------------------------------------------------------------------
def matukio(request):
    ctx = out.matukio()
    ctx.update(_shell(
        nav=navs.outreach("matukio"),
        user_name="Admin MWST", user_role="Msimamizi Mkuu", user_initials="AM",
        notif_count=6, msg_count=3,
    ))
    return render(request, "admin_panel/matukio.html", ctx)


# ---------------------------------------------------------------------------
#  PICHA NA VIDEO
# ---------------------------------------------------------------------------
def media(request):
    ctx = out.media()
    ctx.update(_shell(
        nav=navs.outreach("media"),
        user_name="Admin MWST", user_role="Msimamizi Mkuu", user_initials="AM",
        notif_count=6,
    ))
    return render(request, "admin_panel/media.html", ctx)


# ---------------------------------------------------------------------------
#  DASHIBODI KUU + MWANACHAMA (za awali)
# ---------------------------------------------------------------------------
def dashboard(request):
    from . import mockdata as mock
    ctx = mock.superadmin_dashboard()
    ctx.update(_shell(
        nav=navs.superadmin("dashboard"),
        show_search=True, search_placeholder="Tafuta hapa...",
        user_name="Mohammed Omari", user_role="Super Admin", user_initials="MO",
    ))
    return render(request, "admin_panel/dashboard.html", ctx)


def member_dashboard(request):
    from . import mockdata as mock
    ctx = mock.member_dashboard()
    ctx.update(_shell(
        nav=navs.member("dashboard"),
        verse=data.verse(1),
        notif_count=4, msg_count=0,
        user_name="Mohammed Kapera",
        user_role=ctx["member"]["category_label"],
        user_initials=ctx["member"]["initials"],
    ))
    return render(request, "member/dashboard.html", ctx)
