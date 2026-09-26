"""
Views za MUWESTA MMS.

Data zote zinatoka database kupitia `core.queries`.
"""
import json
import logging
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.translation import get_language, gettext, gettext as _
from django.views.decorators.http import require_POST

from accounts.models import AuditLog, Role
from content.models import MessageLog, Notification, SiteSetting
from geo.models import District, Region, Ward, Zone
from finance.models import Contribution, Donor, Payment, PaymentStatus
from members.models import (Application, ApplicationStatus, Card, Category,
                            Member, MemberStatus)
from programs.models import AssistanceRequest, Event, EventRegistration

from . import queries as q
from . import registry
from . import refdata
from .data import (about as about_data, giving, legal, membership as mem_data,
                   verses as verses_data,
                   navs, pages as pg, tz_map, tz_legend)
from .forms import (ApplicationForm, AssistanceForm, BeneficiaryForm,
                    BootstrapMixin, BroadcastForm,
                    ContactForm,
                    ContributionForm, DonorSignupForm, EventRegistrationForm,
                    FamilyMemberForm,
                    MediaUploadForm, MemberContributionForm, MemberEditForm,
                    MemberPaymentForm,
                    MembershipPaymentForm, PaymentForm, ProfileForm,
                    PublicDonationForm)

log = logging.getLogger(__name__)

STAFF_ONLY = [r.value for r in Role if r not in (Role.MEMBER, Role.DONOR)]

# ===========================================================================
#  Msaada
# ===========================================================================
def _active_year(request):
    """Mwaka uliochaguliwa kwenye ?year=, au mwaka huu."""
    this_year = timezone.localdate().year
    try:
        y = int(request.GET.get("year", this_year))
    except (TypeError, ValueError):
        return this_year
    return y if 2000 <= y <= this_year + 1 else this_year


def _view_roles(url):
    """
    Majukumu yanayoruhusiwa kufungua URL hii, au `None` isipokuwa na
    kizuizi.

    Orodha inasomwa kutoka kwa `role_required` yenyewe (inaiweka kwenye
    `mwst_roles`), si kutoka kwenye nakala ya pili hapa. Nakala ya pili
    ingetofautiana na ukweli siku ya kwanza mtu atakapobadilisha
    kizuizi kimoja tu.
    """
    from django.urls import Resolver404, resolve

    try:
        match = resolve(url.split("?")[0])
    except (Resolver404, Exception):
        return None
    return getattr(match.func, "mwst_roles", None)


def _gate_actions(ctx, user):
    """
    Ondoa "Vitendo vya Haraka" ambavyo mtumiaji hana ruhusa navyo.

    Menyu ilichujwa (`_filter_nav`) lakini gridi ya vitendo kwenye
    dashibodi haikuchujwa. Afisa wa ustawi alikuwa akiona "Rekodi
    Malipo" na "Tuma Ujumbe kwa Wote" kama vitufe vikubwa vya rangi —
    hatua ya kwanza anayoiona akiingia — na kila kimoja kilimwambia
    hana ruhusa. Kitufe kisichobonyezwa ni ahadi ya bure.
    """
    qa = ctx.get("quick_actions")
    if not qa or not user.is_authenticated:
        return ctx
    items = []
    for it in qa.get("items", []):
        url = it.get("url") or ""
        if url.startswith("/mfumo/"):
            parts = url.strip("/").split("/")
            entry = registry.get_entry(parts[1]) if len(parts) > 1 else None
            if entry is not None and not registry.allowed(entry, user):
                continue
        else:
            roles = _view_roles(url)
            if roles is not None and getattr(user, "role", "") not in roles:
                continue
        items.append(it)
    ctx["quick_actions"] = {**qa, "items": items}
    return ctx


def _filter_nav(nav, user):
    """
    Ondoa viungo ambavyo mtumiaji hana ruhusa navyo.

    Awali ilikuwa inaangalia `/mfumo/` pekee. Baada ya kurudisha kila
    ukurasa wa watumishi kwenye jukumu lake, menyu ilibaki ikionyesha
    "Malipo", "Michango", "Wadau" na "Ujumbe kwa Wanachama" kwa afisa
    wa ustawi — akibofya, anaambiwa hana ruhusa. Menyu isiyoaminika ni
    mbaya kuliko menyu fupi.
    """
    def ok(item):
        url = item.get("url") or ""
        if not url.startswith("/"):
            return True
        if url.startswith("/mfumo/"):
            slug = url.strip("/").split("/")[1] if url.count("/") > 2 else None
            if slug is None:
                return True
            entry = registry.get_entry(slug)
            return entry is None or registry.allowed(entry, user)
        roles = _view_roles(url)
        return roles is None or getattr(user, "role", "") in roles

    out = []
    for item in nav:
        children = item.get("children")
        if children is not None:
            kept = [c for c in children if ok(c)]
            if not kept and not ok(item):
                continue
            item = {**item, "children": kept}
        elif not ok(item):
            continue
        out.append(item)
    return out


def _msg_count(user, is_member):
    """
    Ujumbe ambao haujasomwa — kwa beji ya bahasha kwenye topbar.

    Mwanachama: majibu ya viongozi kwenye mazungumzo yake.
    Afisa: ujumbe wa fomu ya mawasiliano ambao haujasomwa.
    """
    if not user.is_authenticated:
        return None
    try:
        if is_member:
            member = getattr(user, "member", None)
            if member is None:
                return None
            from programs.models import Message
            n = Message.objects.filter(thread__member=member, from_leader=True,
                                       read_at__isnull=True).count()
        else:
            from content.models import ContactMessage
            n = ContactMessage.objects.filter(is_read=False).count()
    except Exception:           # jedwali bado halipo (kabla ya migrate)
        return None
    return n or None


def _nav_badges(user):
    """
    Namba zinazoonekana pembeni mwa viungo vya menyu.

    Zilikuwa maandishi tu ndani ya `core/data/navs.py`: kila msimamizi
    aliona "128" karibu na *Maombi ya Uanachama* na kila afisa aliona
    "18" — milele, bila kujali kilichopo. Mtu aliyefungua ukurasa
    akakuta maombi matatu alijua kwamba namba hizo ni za urembo, na
    kuanzia hapo hakuamini namba nyingine yoyote kwenye mfumo.

    Sasa ni hesabu halisi, ndani ya eneo la mtumiaji, na `None`
    ikiwa hakuna kitu kinachosubiri — beji tupu ni kelele.
    """
    from members.models import Application, ApplicationStatus

    apps = Application.objects.filter(
        status__in=[ApplicationStatus.PENDING, ApplicationStatus.REVIEW])
    regions = scope_regions(user)
    if regions is not None:
        apps = apps.filter(region_id__in=regions)
    return {"maombi": apps.count() or None}


def _apply_badges(nav, user):
    """Bandika namba halisi kwenye viungo vinavyozitaka."""
    badges = _nav_badges(user)
    out = []
    for item in nav:
        children = item.get("children")
        if children is not None:
            item = {**item, "children": _apply_badges(children, user)}
        key = item.get("key")
        if key in badges:
            item = {**item, "badge": badges[key]}
        out.append(item)
    return out


def _role_key(user):
    """
    Ufunguo wa rangi ya jukumu — unatumika kwenye `<body class="app-...">`.

    Makundi manne yenye rangi tofauti: uongozi (kijani), fedha
    (dhahabu), usimamizi (bluu), mwanachama (kijani laini). Si mapambo
    tu — afisa akifungua akaunti isiyo yake anaigundua kwa rangi kabla
    hajasoma menyu.
    """
    if not getattr(user, "is_authenticated", False):
        return "member"
    role = getattr(user, "role", "") or ""
    if role in ("finance", "contributions"):
        return "fedha"
    if role in ("super_admin", "admin", "management"):
        return "taifa"
    try:
        from geo.scope import active_posts
        if active_posts(user):
            return "uongozi"
    except Exception:
        pass
    if role in ("registration", "welfare", "outreach"):
        return "afisa"
    return "member"


def _leader_nav(user, nav):
    """
    Badilisha menyu ya mwanachama kuwa ya uongozi kwa aliye kiongozi.

    Menyu ya mwanachama inatambulika kwa kiungo chake cha kwanza
    (`/mwanachama/`). Nyingine zote — usajili, malipo, taifa — hazibadilishwi.
    """
    if not nav or not getattr(user, "is_authenticated", False):
        return nav
    try:
        first = nav[0].get("url", "")
    except (IndexError, AttributeError, TypeError):
        return nav
    if first != "/mwanachama/":
        return nav

    from geo.scope import active_posts, sees_everyone
    if not (active_posts(user) or sees_everyone(user)):
        return nav

    active = next((i.get("key") for i in nav if i.get("active")), "dashboard")
    from geo.models import LeaderLevel
    from geo.scope import top_level
    return navs.uongozi("yangu-dash" if active == "dashboard"
                        else f"yangu-{active}", is_member=True,
                        is_field=top_level(user) == LeaderLevel.WARD)


def _chrome(request, **kw):
    user = request.user

    # KIONGOZI NI MWANACHAMA PIA. Akifungua ukurasa wake wa uanachama
    # (kadi, malipo, pointi), menyu isibadilike kumtoa kwenye uongozi —
    # angepoteza njia ya kurudi kwenye kazi zake.
    #
    # Inafanyika hapa, si kwenye kila view, kwa sababu kurasa za
    # mwanachama ni nyingi na kusahau moja kungeleta menyu isiyolingana.
    kw["nav"] = _leader_nav(user, kw.get("nav"))
    kw.setdefault("role_key", _role_key(user))

    kw.setdefault("year", timezone.localdate().year)
    this_year = timezone.localdate().year
    kw.setdefault("active_year", _active_year(request))
    kw.setdefault("year_options", list(range(this_year, this_year - 6, -1)))
    unread = 0
    if user.is_authenticated:
        unread = Notification.objects.filter(user=user, is_read=False).count()
    is_member = getattr(user, "role", None) == Role.MEMBER
    base = {
        "verse": q.verse(0),
        "notif_count": unread or None,
        #: Ilikuwa `None` daima — beji ya barua haikuweza kuonekana
        #: kamwe, hata ujumbe ukiwepo. Mtumiaji aliisoma kama "huna
        #: ujumbe", si kama "kipengele hiki hakijakamilika". Beji ya
        #: arifa iliyo pembeni yake ilikuwa halisi, jambo lililofanya
        #: udanganyifu uwe mkubwa zaidi.
        "msg_count": _msg_count(user, is_member),
        # Mwanachama anaenda kwenye ukurasa wake; mtumishi anaenda kwenye usimamizi
        "notif_url": ("/mwanachama/taarifa/" if is_member
                      else "/mfumo/arifa/"),
        "msg_url": ("/mawasiliano/" if is_member
                    else "/mfumo/ujumbe-mawasiliano/"),
        "show_search": False,
        "user_name": (user.get_full_name() or user.username) if user.is_authenticated else "",
        "user_role": user.get_role_display() if user.is_authenticated else "",
        "user_initials": user.initials if user.is_authenticated else "??",
    }
    base.update(kw)
    if base.get("nav") and user.is_authenticated:
        base["nav"] = _apply_badges(_filter_nav(base["nav"], user), user)
    return base


def _login_forms():
    """
    Fomu mbili za kuingia kwenye ukurasa wa mbele.

    Milango ni MIWILI tofauti (`login` na `leader_login`), kwa hiyo kila
    fomu ina `action` yake. Tofauti si ya mapambo: mwanachama huingia
    kwa NAMBA YA UANACHAMA, kiongozi kwa JINA LA MTUMIAJI. Fomu moja
    yenye "Namba / Barua pepe / Jina" iliwachanganya wote wawili.

    Kitufe cha kiongozi ni pana kwa makusudi — kinajumuisha viongozi wa
    ngazi zote, maafisa wa makao makuu na waratibu. Wote hawa hupitia
    mlango mmoja, kwa hiyo kuwagawa zaidi kungeongeza hatua bila faida.
    """
    return [
        {
            "key": "mwanachama",
            "action": reverse("core:login"),
            "icon": "user",
            "tint": "green",
            "title": _("Karibu, Mwanachama"),
            "lead": _("Ingia kuona kadi, malipo na pointi zako"),
            "placeholder": _("Namba ya Uanachama au Barua pepe"),
            "hint": _("Mfano: MUWESTA/B/000123/2026"),
        },
        {
            "key": "kiongozi",
            "action": reverse("core:leader_login"),
            "icon": "user-check",
            "tint": "gold",
            "title": _("Karibu, Kiongozi"),
            "lead": _("Viongozi wa ngazi zote, maafisa na waratibu"),
            "placeholder": _("Jina la mtumiaji au Barua pepe"),
            "hint": _("Tumia jina ulilopewa na ofisi, si namba ya uanachama."),
        },
    ]


def _roles():
    """
    Kadi za "wewe ni nani?" kwenye ukurasa wa mbele.

    Kila moja inaelekeza MLANGO WAKE. Awali zote zilielekeza `/ingia/`;
    baada ya kutenganisha milango, kadi ya "Afisa" ingemtupa mtu kwenye
    fomu ya wanachama, ambapo akaunti yake inakataliwa.
    """
    member = reverse("core:login")
    leader = reverse("core:leader_login")
    return [
        {"label": "Mwanachama", "icon": "user", "url": member + "?as=member",
         "tint": "green", "desc": "Kadi, malipo, pointi na maombi yako"},
        {"label": "Kiongozi", "icon": "shield", "url": leader + "?as=leader",
         "tint": "green", "desc": "Kata, wilaya, mkoa, kanda na taifa"},
        {"label": "Afisa", "icon": "briefcase", "url": leader + "?as=officer",
         "tint": "navy", "desc": "Usajili, malipo na michango"},
        {"label": "Mratibu", "icon": "map", "url": leader + "?as=coordinator",
         "tint": "purple", "desc": "Wadau, wahisani na kampeni"},
        {"label": "Msimamizi", "icon": "shield", "url": leader + "?as=admin",
         "tint": "red", "desc": "Mfumo mzima na mikoa yote"},
    ]


def _pub(request, key, extra=None):
    ctx = {"site_menu": pg.menu(), "footer_menu": pg.footer_menu(),
           "page_key": key, "roles": _roles(),
           "login_forms": _login_forms()}
    if extra:
        ctx.update(extra)
    return ctx


def _page(request):
    """Soma ?page= kwa usalama. Herufi, sufuri au hasi zote zinarudi 1."""
    try:
        return max(int(request.GET.get("page", 1)), 1)
    except (TypeError, ValueError):
        return 1


def staff_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            #: Mlango wa viongozi, si wa wanachama. Ukurasa huu ni wa
            #: watumishi — kumpeleka mtu kwenye fomu ya wanachama ni
            #: kumtuma mahali ambapo akaunti yake inakataliwa.
            return redirect(f"{reverse('core:leader_login')}?next={request.path}")
        if request.user.role not in STAFF_ONLY:
            messages.warning(request, _("Huna ruhusa ya kufikia ukurasa huu."))
            return redirect("core:member_dashboard")
        return view(request, *args, **kwargs)
    wrapper.__name__ = view.__name__
    wrapper.__doc__ = view.__doc__
    return wrapper


#: Majukumu yanayoruhusiwa kugusa fedha. `staff_required` inakubali KILA
#: jukumu lisilo la mwanachama, kwa hiyo afisa wa wadau alikuwa na uwezo
#: wa kuthibitisha malipo — na kuthibitisha malipo ya `ada` kunazalisha
#: mwanachama, kadi na akaunti ya kuingia. Yaani afisa asiyehusika na
#: fedha kabisa angeweza kutengeneza uanachama bila senti kuingia.
MONEY_ROLES = [Role.SUPER_ADMIN, Role.ADMIN, Role.MANAGEMENT,
               Role.FINANCE, Role.CONTRIBUTIONS]

#: Majukumu yanayoweza kubadilisha akaunti ya mtu (kurejesha nenosiri).
ACCOUNT_ROLES = [Role.SUPER_ADMIN, Role.ADMIN]

#: Majukumu ya kila eneo la kazi. Yanalingana na yale ya
#: `core/registry.py` kwa makusudi — jukumu moja lisiwe na maana mbili
#: tofauti kwenye sehemu mbili za mfumo mmoja.
#:
#: `staff_required` inakubali KILA jukumu lisilo la mwanachama. Ukaguzi
#: ulionyesha kwamba KILA ukurasa wa watumishi — malipo, michango,
#: wadau, ustawi, kutuma ujumbe kwa wanachama wote, na kupakua CSV za
#: wanachama, wahisani na michango — ulikuwa wazi kwa maafisa wote
#: wanane. Afisa wa wadau angeweza kupakua daftari lote la wanachama;
#: afisa wa usajili angeweza kupakua orodha ya wahisani; yeyote
#: angeweza kutuma SMS kwa wanachama WOTE.
ADMINS_ONLY = [Role.SUPER_ADMIN, Role.ADMIN]
ADMINS_PLUS = ADMINS_ONLY + [Role.MANAGEMENT]
REG_ROLES = ADMINS_PLUS + [Role.REGISTRATION]
OUTREACH_ROLES = ADMINS_PLUS + [Role.OUTREACH, Role.CONTRIBUTIONS]
WELFARE_ROLES = ADMINS_PLUS + [Role.WELFARE]
ZONE_ROLES = ADMINS_PLUS + [Role.COORDINATOR]

#: Kubadilisha hali ya uanachama (kusitisha / kufufua) ni uamuzi wa
#: kinidhamu, si kazi ya kila siku ya usajili.
MEMBER_STATUS_ROLES = ADMINS_PLUS


def role_required(*roles):
    """Kizuizi cha jukumu, juu ya `staff_required`."""
    allowed = [r.value if hasattr(r, "value") else r for r in roles]

    def outer(view):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"{reverse('core:leader_login')}?next={request.path}")
            if request.user.role not in allowed:
                messages.warning(request, _("Huna ruhusa ya kufanya kitendo hiki."))
                return redirect(_back(request, reverse("core:dashboard")))
            return view(request, *args, **kwargs)
        wrapper.__name__ = view.__name__
        wrapper.__doc__ = view.__doc__
        #: Menyu (`_filter_nav`) inasoma hii ili isionyeshe kiungo
        #: ambacho mtu atakataliwa akibofya. Ni orodha moja — ya hapa —
        #: si nakala ya pili inayoweza kutofautiana.
        wrapper.mwst_roles = allowed
        return wrapper
    return outer


def _in_scope(user, member):
    """
    Je, mwanachama huyu yuko ndani ya eneo la mtumiaji?

    Orodha (`wanachama`, `maombi`, `malipo`) zilikuwa zikichuja kwa
    mkoa, lakini VITENDO havikuchuja — mratibu wa Kanda ya Kaskazini
    angeweza kuthibitisha malipo ya mwanachama wa Mtwara kwa kutuma POST
    yenye `pk` yake. Ukaguzi ulikuwa upande wa uongozi
    (`can_touch_payment`) lakini haukuwa upande wa watumishi.

    Ukaguzi unatoka `geo.scope.can_see_member`, si kwa mkoa. Kwa
    mwenyekiti wa KATA, mkoa ni eneo kubwa mno: angeweza kugusa malipo
    ya mtu wa kata nyingine ya mkoa wake. Ngazi inayotumika ni ile ya
    wadhifa wake halisi.
    """
    from geo.scope import can_see_member, sees_everyone

    if sees_everyone(user):
        return True
    if member is None:
        return False
    return can_see_member(user, member)


# ===========================================================================
#  UTHIBITISHO
# ===========================================================================
#: Majaribio ya juu ya kuingia kwa dakika 15 kutoka IP moja
LOGIN_MAX_ATTEMPTS = 8
LOGIN_LOCKOUT_SECONDS = 15 * 60


#: Siku ambazo kifaa cha MWANACHAMA kinakumbukwa. Maafisa hawakumbukwi —
#: paneli ina taarifa binafsi za wanachama wote, kwa hiyo wanaulizwa code
#: kila mara.
DEVICE_COOKIE = "mwst_dev"
DEVICE_TRUST_DAYS = 30


def _client_ip(request):
    """
    Anwani ya IP ya mteja.

    ONYO LILILOREKEBISHWA: awali tulichukua thamani ya KWANZA ya
    `X-Forwarded-For`. Header hiyo inatumwa na KIVINJARI; proxy ya Render
    inaongeza IP halisi MWISHONI. Kwa hiyo mtu angeweza kubandika IP ya
    uongo mwanzoni na kupita kizuizi cha majaribio kwa kuibadilisha kila
    ombi. Sasa tunachukua ya mwisho — ndiyo pekee anayoiandika proxy.
    """
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        parts = [p.strip() for p in forwarded.split(",") if p.strip()]
        if parts:
            return parts[-1]
    return request.META.get("REMOTE_ADDR", "") or "?"


def _safe_next(request, fallback):
    """
    Zuia open redirect. `?next=https://tovuti-mbaya.com` ingemtoa mtumiaji
    nje ya tovuti baada ya kuingia — njia rahisi ya ulaghai.
    """
    from django.utils.http import url_has_allowed_host_and_scheme
    nxt = request.POST.get("next") or request.GET.get("next") or ""
    if nxt and url_has_allowed_host_and_scheme(
            nxt, allowed_hosts={request.get_host()},
            require_https=request.is_secure()):
        return nxt
    return fallback


def _back(request, fallback):
    """
    Rudi ulikotoka, lakini ndani ya tovuti hii tu.

    Vitendo vya POST vilikuwa vikirudisha `HTTP_REFERER` moja kwa moja.
    `_safe_next` ilikuwepo kwa ajili hii hasa — haikuwa ikitumika hapa.
    """
    from django.utils.http import url_has_allowed_host_and_scheme

    ref = request.META.get("HTTP_REFERER") or ""
    if ref and url_has_allowed_host_and_scheme(
            ref, allowed_hosts={request.get_host()},
            require_https=request.is_secure()):
        return ref
    return fallback


def _find_user(identifier, password, request):
    """
    Tafuta mtumiaji kwa jina, namba ya uanachama au barua pepe.
    Zote hazijali herufi kubwa au ndogo.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    user = authenticate(request, username=identifier, password=password)
    if user is not None:
        return user

    # Jina la mtumiaji bila kujali herufi kubwa/ndogo
    match = User.objects.filter(username__iexact=identifier).first()
    if match:
        user = authenticate(request, username=match.username, password=password)
        if user is not None:
            return user

    # Namba ya uanachama au barua pepe
    member = Member.objects.filter(
        Q(membership_no__iexact=identifier) | Q(email__iexact=identifier)
    ).select_related("user").first()
    if member and member.user:
        return authenticate(request, username=member.user.username, password=password)
    return None


#: `staff: True` inamaanisha jukumu hili huingia kwa JINA LA MTUMIAJI
#: (admin, usajili, mratibu_kaskazini...). Majukumu ya nje ya ofisi
#: huingia kwa namba ya uanachama au barua pepe. Uwanja wa kwanza kwenye
#: fomu hubadilika kufuata hili — mtu asiulizwe kitu asichokuwa nacho.
#:
#: `door` inaamua fomu ipi inaonyesha jukumu hili. Milango ni MIWILI na
#: imetenganishwa kabisa:
#:
#:   `/ingia/`           -> wanachama, wahisani na wajitoleaji
#:   `/ingia/viongozi/`  -> viongozi wa aina zote
#:
#: "Viongozi wa aina zote" ni pande mbili za mfumo huu, ambazo ni tofauti
#: kabisa: nyadhifa za kuchaguliwa (`geo.Leadership` — mwenyekiti au
#: katibu wa kata, wilaya, mkoa, kanda, taifa; jukumu lao mara nyingi ni
#: `member`) na maafisa wa ofisi (`Role` — usajili, fedha, michango,
#: ustawi, wadau, mratibu, usimamizi). Wote wanaingia kwenye mlango wa
#: viongozi.
LOGIN_ROLES = [
    {"key": "donor", "label": "Mhisani", "icon": "hand-heart", "tint": "green",
     "staff": False, "door": "member",
     "hint": "Ingia ili kuona kumbukumbu za michango yako yote."},
    {"key": "volunteer", "label": "Kujitolea", "icon": "users", "tint": "green",
     "staff": False, "door": "member",
     "hint": "Wajitoleaji hutumia akaunti ile ile ya mwanachama."},
    {"key": "member", "label": "Mwanachama", "icon": "user", "tint": "green",
     "staff": False, "door": "member",
     "hint": "Kadi yako, malipo, pointi na maombi yako."},
    #: Kiongozi wa kuchaguliwa huingia kwa NAMBA YA UANACHAMA — ana rekodi
    #: ya uanachama, hana jina la mtumiaji la ofisi.
    {"key": "leader", "label": "Kiongozi", "icon": "shield", "tint": "green",
     "staff": False, "door": "leader",
     "hint": "Mwenyekiti au katibu wa kata, wilaya, mkoa, kanda au taifa."},
    {"key": "officer", "label": "Afisa", "icon": "briefcase", "tint": "gold",
     "staff": True, "door": "leader",
     "hint": "Usajili, malipo, michango na ustawi."},
    {"key": "coordinator", "label": "Mratibu", "icon": "map", "tint": "navy",
     "staff": True, "door": "leader",
     "hint": "Mikoa, wadau na kampeni za kanda yako."},
    {"key": "admin", "label": "Msimamizi", "icon": "shield", "tint": "purple",
     "staff": True, "door": "leader",
     "hint": "Mfumo mzima na mikoa yote."},
]

#: Mlango wa kila jukumu, na jukumu la kwanza la kila mlango.
DOOR_DEFAULT = {"member": "member", "leader": "officer"}


def _door_roles(door):
    return [r for r in LOGIN_ROLES if r["door"] == door]


def _user_by_identifier(identifier):
    """
    Mtumiaji anayelingana na kitambulisho hiki, au `None`.

    Hutafuta kwa jina la mtumiaji, barua pepe, au namba ya uanachama —
    njia zote tatu ambazo `_find_user` hukubali. HAITHIBITISHI nenosiri;
    inatumika kuamua MLANGO tu.
    """
    if not identifier:
        return None
    from django.contrib.auth import get_user_model
    User = get_user_model()

    user = User.objects.filter(
        Q(username__iexact=identifier) | Q(email__iexact=identifier)).first()
    if user is not None:
        return user
    member = Member.objects.filter(
        Q(membership_no__iexact=identifier) | Q(email__iexact=identifier)
    ).select_related("user").first()
    return member.user if member else None


def _is_leader_account(user):
    """
    Je, akaunti hii ni ya kiongozi wa aina yoyote?

    Pande mbili: jukumu la ofisi (`is_staff_role`) au wadhifa wa
    kuchaguliwa unaotumika leo (`geo.Leadership`). Msimamizi mkuu wa
    Django hahesabiwi hapa — hana mlango wa umma kabisa.
    """
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_staff", False) or getattr(user, "is_staff_role", False):
        return True
    from geo.scope import active_posts
    return bool(active_posts(user))


def _door_of(user):
    """Mlango unaomhusu mtumiaji huyu."""
    return "leader" if _is_leader_account(user) else "member"

#: Maneno ya uwanja wa kwanza kwa kila aina ya jukumu. Yapo hapa —
#: si kwenye JavaScript — ili yapite kwenye tafsiri kama maandishi mengine.
IDENTIFIER_COPY = {
    True: {
        "label": "Jina la Mtumiaji",
        "placeholder": "mfano: admin, usajili, mratibu_kaskazini",
        "hint": "Jina ulilopewa na ofisi, si barua pepe yako.",
        "icon": "user",
        "autocomplete": "username",
    },
    False: {
        "label": "Barua Pepe / Namba ya Uanachama",
        "placeholder": "MUWESTA/B/000123/2026 au barua pepe yako",
        "hint": "Namba iliyo kwenye kadi yako, au barua pepe uliyojisajili nayo.",
        "icon": "mail",
        "autocomplete": "username",
    },
}


def _login_ctx(request, door="member", extra=None):
    """
    Muktadha wa ukurasa wa kuingia wa mlango mmoja.

    ONYO: jukumu lililochaguliwa ni MWONGOZO wa maonyesho tu. Jukumu halisi
    linatoka kwenye akaunti yenyewe (`user.role`) — mtu hawezi kupata ruhusa
    za msimamizi kwa kubofya kitufe cha "Msimamizi". Vivyo hivyo mlango:
    kufungua `/ingia/viongozi/` hakumfanyi mtu kuwa kiongozi.
    """
    roles = _door_roles(door)
    keys = [r["key"] for r in roles]
    picked = (request.POST.get("as") or request.GET.get("as") or "").lower()
    if picked not in keys:
        picked = DOOR_DEFAULT.get(door, keys[0])
    spec = next(r for r in roles if r["key"] == picked)

    def copy(is_staff):
        row = IDENTIFIER_COPY[is_staff]
        return {k: (gettext(v) if k in ("label", "placeholder", "hint") else v)
                for k, v in row.items()}

    # Vikundi vya kuonyesha kwenye fomu.
    #
    # MLANGO WA WANACHAMA hauna kikundi: mwanachama, mhisani na
    # mjitoleaji wote huingia kwa namba ya uanachama au barua pepe.
    # Kuwaonyesha vitufe vitatu vinavyobadilisha dokezo pekee ni hatua
    # ya ziada isiyobadilisha chochote — na iliwachanganya watu.
    #
    # MLANGO WA VIONGOZI una vikundi viwili halisi: kiongozi wa
    # kuchaguliwa ana namba ya uanachama, afisa wa ofisi ana jina la
    # mtumiaji. Hapo kuchagua kunabadilisha sehemu ya kujaza kweli.
    groups = []
    if door == "leader":
        groups = [
            {"key": "leader", "label": gettext("Kiongozi wa Kuchaguliwa"),
             "icon": "shield", "staff": False,
             "desc": gettext("Mwenyekiti au katibu wa kata, wilaya, "
                             "mkoa, kanda au taifa")},
            {"key": "officer", "label": gettext("Afisa wa Ofisi"),
             "icon": "briefcase", "staff": True,
             "desc": gettext("Usajili, malipo, michango, ustawi, "
                             "wadau, mratibu na usimamizi")},
        ]

    ctx = {
        "login_roles": roles,
        "login_groups": groups,
        "door": door,
        "active_role": picked,
        "role_hint": gettext(spec["hint"]),
        #: Maneno ya sasa (yanayotolewa na seva) na yale ya upande wa pili
        #: (yanayotumiwa na JavaScript pale mtu anapobadilisha jukumu).
        "ident": copy(spec["staff"]),
        "ident_staff": copy(True),
        "ident_public": copy(False),
        "username_value": (request.POST.get("username") or "").strip(),
        "next": request.GET.get("next", "") or request.POST.get("next", ""),
    }
    if extra:
        ctx.update(extra)
    return _pub(request, "ingia", ctx)


def _suspended_reason(user):
    """
    Sababu ya kumzuia kuingia, au `""` akiwa huru kuingia.

    Afisa anapobofya "Sitisha" kwenye ukurasa wa mwanachama, hali ya
    `Member` inakuwa `suspended` — LAKINI `user.is_active` haiguswi, na
    hakuna mahali pengine hali hiyo ilikuwa ikiangaliwa. Kwa hiyo
    mwanachama aliyesitishwa aliendelea kuingia, kuona kadi yake, kuomba
    msaada na kutuma malalamiko kama kawaida. Uamuzi wa afisa haukuwa na
    athari yoyote kwenye mfumo.

    Muda ukiisha (`expired`) HAKUZUII — mtu anapaswa kuingia ndio aweze
    kuhuisha uanachama wake. Ni kusitishwa pekee kunakofunga mlango.
    """
    member = getattr(user, "member", None)
    if member is not None and member.status == MemberStatus.SUSPENDED:
        return str(_("Uanachama wako umesitishwa. Wasiliana na ofisi ya "
                     "MUWESTA kwa maelezo zaidi."))
    return ""


def _needs_code(user, request):
    """
    Je, mtu huyu anatakiwa kuthibitisha kwa code?

    Maafisa: KILA MARA. Paneli ya usimamizi ina majina, namba za simu,
    namba za vitambulisho na anwani za wanachama wote — nenosiri pekee
    halitoshi kulinda hiyo.

    Wanachama: kifaa kipya tu, kisha siku 30. Wanaoingia mara kwa mara
    wasipokee SMS kila siku; usalama ungegeuka kero, na kero husababisha
    watu kutafuta njia za kuzunguka.
    """
    from django.conf import settings as _s

    if not getattr(_s, "LOGIN_OTP_ENABLED", True):
        return False
    # Bila namba ya simu hakuna pa kupeleka code. Tunamruhusu aingie
    # badala ya kumfungia nje milele — angalia `_start_login_code`.
    if not _phone_for(user):
        return False
    #: Ulikuwa `user.is_staff` — bendera ya Django inayowekwa na amri za
    #: `ruhusa`/`watumishi` pekee. Afisa aliyeundwa kupitia
    #: `/mfumo/watumiaji/` hapati bendera hiyo, kwa hiyo alikuwa
    #: anapitia njia ya kifaa kinachoaminika cha siku 30 na hakuulizwa
    #: code tena kamwe. Maafisa wawili wenye jukumu moja walikuwa na
    #: ulinzi tofauti kabisa. `is_staff_role` inaangalia JUKUMU, ambalo
    #: ndilo linaloamua anachoona.
    if user.is_staff or user.is_staff_role:
        return True
    #: Kiongozi wa kuchaguliwa (jukumu `member`) anaingia hapa. Anapata
    #: code kwenye kifaa kipya, kisha kifaa kinaaminika siku 30 — sawa na
    #: mwanachama. Hii ni kwa makusudi: hana ofisi, anatumia simu yake
    #: uwanjani, na code kila mara ingekuwa kero inayomfanya atafute njia
    #: ya kuzunguka. Paneli yake inaonyesha eneo lake pekee, si nchi nzima.
    return not _device_trusted(request, user)


def _phone_for(user):
    """Namba ya simu ya mtumiaji — yake mwenyewe au ya rekodi ya uanachama."""
    phone = (getattr(user, "phone", "") or "").strip()
    if not phone:
        member = getattr(user, "member", None)
        phone = (getattr(member, "phone", "") or "").strip() if member else ""
    return phone


def _device_trusted(request, user):
    from django.core import signing
    raw = request.COOKIES.get(DEVICE_COOKIE, "")
    if not raw:
        return False
    try:
        data = signing.loads(raw, salt="mwst-device",
                             max_age=DEVICE_TRUST_DAYS * 24 * 3600)
    except signing.BadSignature:
        return False
    return data.get("u") == user.pk


def _remember_device(response, user):
    from django.conf import settings as _s
    from django.core import signing
    response.set_cookie(
        DEVICE_COOKIE, signing.dumps({"u": user.pk}, salt="mwst-device"),
        max_age=DEVICE_TRUST_DAYS * 24 * 3600,
        secure=not _s.DEBUG, httponly=True, samesite="Lax")
    return response


def _alert_login(user, request, ok=True):
    """
    Mjulishe mtu kwa SMS na barua pepe kwamba akaunti yake imeguswa.

    Arifa za kushindwa zina kikomo cha moja kwa saa. Bila kikomo, mtu
    angeweza kujaza simu ya mwanachama kwa SMS kwa kubandika nenosiri
    lisilo sahihi mara elfu — kinga ingegeuka silaha, na kila SMS
    ingelipiwa na MUWESTA.
    """
    from django.core.cache import cache
    from . import mailer, sms

    phone = _phone_for(user)
    email = (user.email or "").strip()
    if not (phone or email):
        return
    if not ok:
        key = f"alert-fail:{user.pk}"
        if cache.get(key):
            return
        cache.set(key, 1, 3600)
    if phone:
        sms.send_login_alert(phone, user.get_full_name() or user.username, ok=ok)
    #: Kulikuwa na `_alert_login` MBILI kwenye faili hii. Ya pili
    #: ilififisha ya kwanza, kwa hiyo arifa ya barua pepe
    #: (`mailer.send_login_alert`) haikuwahi kutumwa hata mara moja —
    #: na aliyesoma ufafanuzi wa ya kwanza aliamini inatumwa.
    #: Sasa ni moja, na inatumia njia zote mbili.
    if email:
        mailer.send_login_alert(
            email, user.get_full_name() or user.username,
            _client_ip(request), request.META.get("HTTP_USER_AGENT", ""), ok=ok)


def _mask_phone(phone):
    """
    255 7** *** 102 — inamsaidia mtu kutambua namba bila kuifichua kwa
    aliyeiba nenosiri lake.
    """
    from . import sms
    # `effective` — SMS ikielekezwa kwa msanidi (SMS_REDIRECT_TO),
    # ukurasa uonyeshe namba itakayopokea kweli. Vinginevyo mtu
    # angesubiri SMS kwenye namba isiyopokea chochote.
    digits = sms.effective(phone)
    if len(digits) < 7:
        return digits
    # `digits[:4]` ilitoa "2557 *** *** 102" — inasomeka kama kosa la
    # kuandika. Msimbo wa nchi peke yake ni wazi zaidi.
    return f"+{digits[:3]} *** *** {digits[-3:]}"


def _finish_login(request, user, trust_device=False):
    """Kamilisha kuingia: session, kumbukumbu, arifa."""
    auth_login(request, user)
    # "Kumbuka mimi": bila hiyo, kipindi kinaisha kivinjari kikifungwa.
    if not request.session.pop("mwst_remember", False):
        request.session.set_expiry(0)
    AuditLog.record(request, "login")
    _alert_login(user, request, ok=True)
    messages.success(request, _("Karibu, %(name)s!") % {
        "name": user.get_full_name() or user.username})

    #: Aliyeingia kwenye mlango wa viongozi anaenda kwenye eneo la
    #: uongozi, si kwenye dashibodi ya mwanachama.
    #:
    #: Kiongozi wa kata ana jukumu `member` na rekodi ya uanachama, kwa
    #: hiyo `home_url_name()` ilimpeleka `/mwanachama/` — hata pale
    #: alipobofya "Kiongozi" na kuingia kwa nia ya kufanya kazi ya
    #: wadhifa wake. Mlango anaouchagua ni maelezo ya anachotaka.
    door = request.session.pop("mwst_door", "")
    home = reverse(user.home_url_name())
    if door == "leader" and not (user.is_staff or user.is_staff_role):
        from core import leadership as _L
        if _L.is_leader(user):
            home = reverse("core:leader_dashboard")
    target = request.session.pop("mwst_next", "") or home
    response = redirect(_safe_next(request, target))
    if trust_device and not (user.is_staff or user.is_staff_role):
        _remember_device(response, user)
    return response


def _start_login_code(request, user):
    """Tuma code na mpeleke mtu kwenye ukurasa wa kuithibitisha."""
    from accounts.models import CodePurpose, VerificationCode
    from . import sms

    phone = _phone_for(user)
    if VerificationCode.too_many(sms.msisdn(phone)):
        messages.error(request, _(
            "Umeomba code nyingi mno kwa saa moja. Subiri kidogo kisha "
            "ujaribu tena."))
        return redirect(_door_name(request))

    row, code = VerificationCode.issue(
        sms.msisdn(phone), CodePurpose.LOGIN, user=user, ip=_client_ip(request))
    sent = sms.send_code(phone, code, "login", VerificationCode.TTL_MINUTES)

    if not sent:
        # SMS imeshindwa. Kumfungia nje mtu mwenye nenosiri sahihi kwa
        # sababu ya hitilafu ya mtandao au salio lililoisha ni kumuadhibu
        # kwa kosa letu — kwa hiyo mwanachama anaruhusiwa kuendelea.
        #
        # LAKINI: NextSMS isipokuwa imewekwa kabisa, `send_code`
        # inarudisha `False` KILA MARA. Hiyo si hitilafu ya muda — ni
        # hitilafu ya usanidi, na ilikuwa inazima uthibitisho wa hatua
        # mbili kwa maafisa wote kimya kimya, huku dashibodi ikiendelea
        # kusema OTP imewashwa. Mtu mwenye nenosiri lililoibiwa la afisa
        # aliingia moja kwa moja. Kwa maafisa, mlango unafungwa.
        from . import sms as _sms

        misconfigured = not _sms.is_configured()
        if user.is_staff or user.is_staff_role:
            log.error("Code ya kuingia haikutumwa kwa afisa %s — "
                      "ameKATALIWA (usanidi: %s)",
                      user.username, "haupo" if misconfigured else "upo")
            AuditLog.record(
                request,
                "login_code_unconfigured" if misconfigured else "login_code_undelivered",
                detail=user.username)
            messages.error(request, _(
                "Hatukuweza kutuma code ya usalama kwenye simu yako. Kwa "
                "usalama wa taarifa za wanachama, hatuwezi kukuruhusu "
                "kuingia bila code. Wasiliana na msimamizi wa mfumo."))
            if misconfigured:
                #: Msimamizi anayeweka mfumo mara ya kwanza anastahili
                #: kuambiwa nini hasa cha kufanya, si kubaki amefungiwa
                #: nje bila maelezo. Kuzima OTP ni uamuzi — si kitu
                #: kinachopaswa kutokea chenyewe kimya kimya.
                messages.info(request, _(
                    "Kwa msimamizi: NEXTSMS haijawekwa. Weka funguo zake "
                    "kwenye environment, au — ukikubali hatari yake — "
                    "weka LOGIN_OTP_ENABLED=False kwa muda."))
            return redirect(_door_name(request))

        log.error("Code ya kuingia haikutumwa kwa %s — ameruhusiwa kuingia",
                  user.username)
        AuditLog.record(request, "login_code_undelivered", detail=user.username)
        messages.warning(request, _(
            "Hatukuweza kutuma code kwenye simu yako, kwa hiyo tumekuruhusu "
            "kuingia. Tafadhali mjulishe msimamizi."))
        return _finish_login(request, user)

    request.session["mwst_pending_user"] = user.pk
    request.session["mwst_pending_at"] = timezone.now().isoformat()
    request.session["mwst_remember"] = bool(request.POST.get("remember"))
    request.session["mwst_next"] = _safe_next(request, "")
    AuditLog.record(request, "login_code_sent", detail=user.username)
    return redirect("core:login_code")


def _door_name(request):
    """
    Jina la URL ya mlango aliotoka mtu huyu.

    Hatua ya code ni ombi lingine; bila hii, afisa aliyeshindwa
    kuthibitisha alikuwa akirudishwa `/ingia/` — fomu ya wanachama,
    ambapo akaunti yake inakataliwa. Alikuwa akizungushwa.
    """
    return ("core:leader_login"
            if request.session.get("mwst_door") == "leader" else "core:login")


#: Vitufe vya session vya hatua ya code. `PENDING` ni "ni nani anasubiri";
#: `INTENT` ni "alitaka nini" — kifaa kikumbukwe, aende wapi, alitoka
#: mlango upi. `_finish_login` ndiye anayesoma `INTENT`.
PENDING_KEYS = ("mwst_pending_user", "mwst_pending_at")
INTENT_KEYS = ("mwst_remember", "mwst_next", "mwst_door")


def _clear_pending(request, keep_intent=False):
    """
    Safisha hatua ya code.

    `keep_intent=True` huacha nia yake — inatumika pale code ILIPOKUBALIWA,
    kwa sababu `_finish_login` bado anahitaji kujua aende wapi.

    HITILAFU ILIYOKUWA HAPA: kazi hii ilikuwa inafuta `mwst_next` pamoja
    na kila kitu kingine, na iliitwa MSTARI MMOJA kabla ya
    `_finish_login`. Kwa hiyo mtu aliyebofya kiungo cha ndani
    (`?next=/malipo/`), akaulizwa code, alipelekwa ukurasa wake wa
    kawaida badala ya pale alipotaka kwenda. Kiungo alichobofya
    kilipotea kimya kimya kila mara OTP ilipowashwa.
    """
    keys = PENDING_KEYS if keep_intent else PENDING_KEYS + INTENT_KEYS
    for k in keys:
        request.session.pop(k, None)


def login_code_view(request):
    """
    Hatua ya pili ya kuingia: code iliyotumwa kwa SMS.

    Mtu bado HAJAINGIA hapa. Nia yake ipo kwenye session pekee — si
    kwenye URL wala fomu, ambako angeweza kuibadilisha na kuwa mtu
    mwingine — na inaisha baada ya dakika 15.
    """
    from accounts.models import CodePurpose, VerificationCode
    from datetime import timedelta
    from . import sms

    pk = request.session.get("mwst_pending_user")
    started = request.session.get("mwst_pending_at")
    mlango = _door_name(request)
    if not pk or not started:
        return redirect(mlango)

    if timezone.now() - timezone.datetime.fromisoformat(started) > timedelta(minutes=15):
        _clear_pending(request)
        messages.error(request, _("Muda umeisha. Tafadhali ingia tena."))
        return redirect(mlango)

    from django.contrib.auth import get_user_model
    user = get_user_model().objects.filter(pk=pk).first()
    if user is None:
        _clear_pending(request)
        return redirect(mlango)

    phone = _phone_for(user)
    if request.method == "POST":
        if request.POST.get("resend"):
            if VerificationCode.too_many(sms.msisdn(phone)):
                messages.error(request, _("Umeomba code nyingi mno. Subiri kidogo."))
            else:
                row, code = VerificationCode.issue(
                    sms.msisdn(phone), CodePurpose.LOGIN, user=user,
                    ip=_client_ip(request))
                sms.send_code(phone, code, "login", VerificationCode.TTL_MINUTES)
                messages.info(request, _("Tumekutumia code nyingine."))
            return redirect("core:login_code")

        row, err = VerificationCode.verify(
            sms.msisdn(phone), CodePurpose.LOGIN, request.POST.get("code", ""))
        if err is None:
            _clear_pending(request, keep_intent=True)
            return _finish_login(request, user, trust_device=True)

        AuditLog.record(request, "login_code_failed", detail=user.username)
        messages.error(request, {
            "none": _("Hakuna code inayosubiri. Tafadhali ingia tena."),
            "expired": _("Code hii imeisha muda. Omba nyingine."),
            "attempts": _("Umejaribu mara nyingi mno. Omba code nyingine."),
        }.get(err, _("Code si sahihi. Jaribu tena.")))

    return render(request, "public/otp.html", {
        "page_title": _("Thibitisha ni wewe"),
        "page_lead": _("Tumekutumia code ya tarakimu sita kwenye simu yako."),
        "submit_label": _("Ingia"),
        "back_url": reverse(mlango),
        "back_label": _("Rudi kuingia"),
        "target": _mask_phone(phone),
        "minutes": VerificationCode.TTL_MINUTES,
    })


def _safe_detail(identifier):
    """
    Kitambulisho cha kuhifadhi kwenye kumbukumbu ya jaribio lililoshindwa.

    Watu HUANDIKA nenosiri lao kwenye sehemu ya jina kwa bahati mbaya —
    ni kosa la kawaida sana. Likihifadhiwa wazi, nenosiri halisi la mtu
    linakaa kwenye database milele. Tunahifadhi mwanzo tu.
    """
    ident = (identifier or "").strip()
    if len(ident) <= 4:
        return ident
    return f"{ident[:4]}\u2026({len(ident)})"


def _alert_failed(identifier, request):
    """Tafuta mwenye akaunti hii na umjulishe kuhusu jaribio."""
    user = _user_by_identifier(identifier)
    if user is not None:
        _alert_login(user, request, ok=False)


#: Kiolezo cha kila mlango. Vyote viwili vinatumia `public/_login_form.html`
#: kwa fomu yenyewe — ulinzi, uwanja na hatua ni vile vile; kinachotofautiana
#: ni nembo, maneno na viungo.
DOOR_TEMPLATE = {
    "member": "public/login.html",
    "leader": "public/login_uongozi.html",
}


def _wrong_door(request, user, door):
    """
    Ujumbe wa kumwelekeza mtu kwenye mlango wake, au `""` akiwa mahali sahihi.

    Ukaguzi unafanyika KWA KITAMBULISHO, kabla nenosiri kuthibitishwa.
    Sababu: kama tungeangalia baada ya kuthibitisha, afisa aliyefika
    mlango wa wanachama akiwa na nenosiri sahihi angeambiwa "nenda
    mlango mwingine", na akiwa na nenosiri lisilo sahihi angeambiwa
    "nenosiri si sahihi" — tofauti hiyo yenyewe ingekuwa ikithibitisha
    nenosiri. Kuangalia kabla huondoa tofauti hiyo kabisa.
    """
    if user is None:
        return ""
    mine = _door_of(user)
    if mine == door:
        return ""
    if door == "member":
        return str(_("Akaunti hii ni ya kiongozi. Tumia ukurasa wa "
                     "kuingia wa viongozi."))
    return str(_("Akaunti hii ni ya mwanachama. Tumia ukurasa wa kuingia "
                 "wa wanachama."))


def _login_door(request, door):
    """
    Hatua za kuingia kwa mlango mmoja.

    Milango miwili, mwili mmoja: kikomo cha majaribio, kuzuia msimamizi
    mkuu, ukaguzi wa kusitishwa, code ya SMS na arifa ni vile vile pande
    zote mbili. Kuyaandika mara mbili ni kuhakikisha kwamba siku moja
    moja itasahihishwa na nyingine itabaki na hitilafu.
    """
    if request.user.is_authenticated:
        return redirect(request.user.home_url_name())

    from django.core.cache import cache
    cache_key = f"login-fail:{_client_ip(request)}"
    template = DOOR_TEMPLATE[door]

    if request.method == "POST":
        attempts = cache.get(cache_key, 0)
        if attempts >= LOGIN_MAX_ATTEMPTS:
            messages.error(request, _(
                "Umejaribu mara nyingi mno. Subiri dakika 15 kisha ujaribu tena, "
                "au tumia \"Umesahau nenosiri?\"."))
            return render(request, template, _login_ctx(request, door))

        identifier = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""

        #: Mlango kwanza, nenosiri baadaye — angalia `_wrong_door`.
        known = _user_by_identifier(identifier) if identifier else None
        if known is not None and not known.is_superuser:
            elsewhere = _wrong_door(request, known, door)
            if elsewhere:
                AuditLog.record(request, "login_wrong_door",
                                detail=f"{known.username} -> {door}")
                messages.info(request, elsewhere)
                other = ("core:leader_login" if door == "member"
                         else "core:login")
                return redirect(f"{reverse(other)}"
                                f"?next={_safe_next(request, '')}")

        user = _find_user(identifier, password, request) if identifier else None

        if user is not None and user.is_superuser:
            # Msimamizi mkuu hatumii ukurasa huu. Akaunti yake ni ya
            # Django admin pekee, kwenye njia yake ya siri — kwa hiyo
            # hata mtu aliyeiba nenosiri lake hawezi kuitumia hapa,
            # wala hawezi kujua kama nenosiri ni sahihi.
            cache.set(cache_key, attempts + 1, LOGIN_LOCKOUT_SECONDS)
            AuditLog.record(request, "superuser_public_login_blocked",
                            detail=user.username)
            messages.error(request, _("Jina la mtumiaji au nenosiri si sahihi."))
            return render(request, template, _login_ctx(request, door))

        if user is not None:
            blocked = _suspended_reason(user)
            if blocked:
                cache.delete(cache_key)
                AuditLog.record(request, "login_blocked_suspended",
                                detail=user.username)
                messages.error(request, blocked)
                return render(request, template, _login_ctx(request, door))

        if user is not None:
            cache.delete(cache_key)
            #: Mlango unahifadhiwa kwa sababu hatua ya code ni ombi
            #: lingine kabisa — `_finish_login` haiwezi kujua alitoka wapi.
            request.session["mwst_door"] = door
            if _needs_code(user, request):
                # Nenosiri ni sahihi, lakini bado hajaingia.
                return _start_login_code(request, user)
            return _finish_login(request, user)

        cache.set(cache_key, attempts + 1, LOGIN_LOCKOUT_SECONDS)
        AuditLog.record(request, "login_failed", detail=_safe_detail(identifier))
        # Mwambie mwenye akaunti kwamba mtu anajaribu nenosiri lake.
        _alert_failed(identifier, request)
        remaining = LOGIN_MAX_ATTEMPTS - attempts - 1
        if 0 < remaining <= 3:
            messages.warning(request, _(
                "Umebakiwa na majaribio %(n)d kabla ya kuzuiliwa.") % {"n": remaining})
        # Wakati wa maendeleo, database ikiwa tupu ni chanzo cha kawaida cha
        # "nenosiri si sahihi". Onyesha dokezo — lakini DEBUG pekee.
        from django.conf import settings as _s
        from django.contrib.auth import get_user_model
        if _s.DEBUG and not get_user_model().objects.exists():
            messages.error(request, _(
                "Hakuna mtumiaji yeyote kwenye database. "
                "Endesha: python manage.py seed"))
        else:
            messages.error(request, _("Jina la mtumiaji au nenosiri si sahihi."))

    return render(request, template, _login_ctx(request, door))


def login_view(request):
    """Kuingia kwa wanachama, wahisani na wajitoleaji."""
    return _login_door(request, "member")


def leader_login(request):
    """
    Kuingia kwa viongozi wa aina zote.

    Mlango tofauti kwa makusudi: nyadhifa za kuchaguliwa (kata, wilaya,
    mkoa, kanda, taifa) na maafisa wa ofisi wote wanapitia hapa. Ukurasa
    wa wanachama haumwomba mtu jina la mtumiaji la ofisi, na huu
    haumwalike mtu kujiunga — kila mmoja unauliza kinachomhusu.
    """
    return _login_door(request, "leader")


def logout_view(request):
    if request.user.is_authenticated:
        AuditLog.record(request, "logout")
    auth_logout(request)
    messages.info(request, _("Umetoka kwenye mfumo."))
    return redirect("core:home")


def weka_nenosiri(request):
    """
    Mwanachama mpya anaweka nenosiri lake mara ya kwanza.

    HII ILIKUWA HAIPO, na bila yake safari yote ya kujiunga ilikwama
    hatua ya mwisho. `Application.activate()` huitwa na signal ya malipo
    — yaani ndani ya callback ya Pesapal, pasipo afisa mbele ya skrini.
    Nenosiri la muda lililotengenezwa hapo lilibaki kwenye kumbukumbu ya
    request ile: halikuhifadhiwa, halikupelekwa kwa SMS, na ukurasa wa
    asante ukisoma tena kutoka database ulipata `None`. Kila mwanachama
    aliyejiunga kwa njia ya mtandao alikuwa na akaunti yenye nenosiri
    ambalo hakuna mtu — wala yeye, wala afisa — anayelijua.

    Saini kwenye kiungo ina alama ya nenosiri la sasa, kwa hiyo kiungo
    hufa chenyewe mara nenosiri linapowekwa. Kiungo kilichotumwa mara
    mbili hakiwezi kutumiwa mara ya pili.
    """
    from django.contrib.auth.forms import SetPasswordForm

    no = (request.GET.get("no") or request.POST.get("no") or "").strip()
    token = (request.GET.get("k") or request.POST.get("k") or "").strip()
    member = Member.by_setup_token(no, token)
    if member is None:
        messages.error(request, _(
            "Kiungo hiki hakifanyi kazi tena. Huenda nenosiri lako "
            "lilikwisha wekwa — jaribu kuingia, au tumia \"Nimesahau "
            "nenosiri\"."))
        return redirect("core:login")

    if request.method == "POST":
        form = SetPasswordForm(member.user, request.POST)
        if form.is_valid():
            form.save()
            AuditLog.record(request, "member_password_set", member)
            messages.success(request, _(
                "Nenosiri lako limewekwa. Sasa ingia kwa namba yako ya "
                "uanachama %(no)s.") % {"no": member.membership_no})
            return redirect("core:login")
        messages.error(request, _("Tafadhali sahihisha makosa hapa chini."))
    else:
        form = SetPasswordForm(member.user)

    return render(request, "public/weka_nenosiri.html", _pub(request, "ingia", {
        "form": form, "member": member, "no": no, "k": token,
    }))


# ===========================================================================
#  TOVUTI YA UMMA
# ===========================================================================
def home(request):
    return render(request, "public/home.html", _pub(request, "home",
                            {**q.public_home(),
                             "verses": verses_data.verses(get_language()),
                             "alerts": q.live_announcements(limit=6)}))


def kuhusu(request):
    return render(request, "public/kuhusu.html", _pub(request, "kuhusu", {**q.public_kuhusu(),
                                          "about": about_data.about(get_language())}))


def uanachama(request):
    return render(request, "public/uanachama.html",
                  _pub(request, "uanachama",
                            {**q.public_uanachama(),
                             "mem": mem_data.membership(get_language())}))


def huduma(request):
    return render(request, "public/huduma.html", _pub(request, "huduma", q.public_huduma()))


def habari(request):
    return render(request, "public/habari.html", _pub(request, "habari", q.public_habari()))


def habari_moja(request, pk):
    """
    Habari moja kamili.

    Ukurasa huu haukuwepo. `News.body` — maudhui halisi ya habari —
    ilihifadhiwa, ilihaririwa kwenye `/mfumo/habari/`, lakini haikuwa na
    njia ya kuonekana: kila kitufe cha "Soma Zaidi" kilirudi kwenye
    orodha ile ile.
    """
    from content.models import News

    item = get_object_or_404(News, pk=pk, is_published=True)
    others = (News.objects.filter(is_published=True).exclude(pk=item.pk)
              .select_related("category")[:3])
    return render(request, "public/habari_moja.html", _pub(request, "habari", {
        "item": item,
        "others": [{"id": n.pk, "title": n.tx("title"), "scene": n.scene,
                    "date": n.published_on.strftime("%d %B %Y")} for n in others],
    }))


def matukio_umma(request):
    return render(request, "public/matukio.html", _pub(request, "matukio", q.public_matukio()))


def picha(request):
    """Maktaba ya picha na video kwa umma."""
    ctx = q.public_gallery(album_slug=request.GET.get("albamu"), page=_page(request))
    return render(request, "public/picha.html", _pub(request, "picha", ctx))


# ===========================================================================
#  PESAPAL
# ===========================================================================
def _pesapal_ready():
    """Pesapal iko tayari ikiwa funguo NA namba ya IPN zimewekwa."""
    from django.conf import settings as st
    from finance.gateways import pesapal
    return pesapal.is_configured() and bool(getattr(st, "PESAPAL_IPN_ID", ""))


def _selcom_ready():
    from finance.gateways import selcom
    return selcom.is_configured()


def _selcom_start(request, gift, description):
    """
    Anzisha malipo ya Selcom na tuma kidokezo kwenye simu ya mtu.

    Tofauti na Pesapal, mtu HABAKI kuondoka kwenye tovuti. Anaacha
    ukurasa ukisubiri, anaingiza PIN kwenye simu yake, na ukurasa
    unajisasisha wenyewe malipo yakikamilika.

    Hatua mbili zinahitajika: kuunda order, kisha kutuma kidokezo.
    Ikigoma kwenye hatua ya pili, order tayari ipo Selcom — kwa hiyo
    tunahifadhi `gateway_ref` kabla ya kutuma kidokezo, ili tuweze
    kuuliza hali yake baadaye hata kama kidokezo hakikufika.
    """
    from django.conf import settings as st
    from finance.gateways import selcom

    #: `contact_phone` inasoma `donor_phone` kwanza. Awali hapa
    #: palikuwa `gift.donor.phone` pekee, na `/lipa/` HAIWEKI `donor`
    #: kabisa — kwa hiyo kila malipo ya ada kwa Selcom yalisimama hapa
    #: kabla hayajaanza, huku mtu akiambiwa "mchango wako umehifadhiwa"
    #: bila njia yoyote ya kulipa.
    phone = gift.contact_phone
    if not phone:
        messages.error(request, _(
            "Namba ya simu inahitajika kwa malipo ya simu. Mchango wako "
            "umehifadhiwa kwa namba %(risiti)s."
        ) % {"risiti": gift.receipt_no})
        return redirect("core:changia_asante", receipt=gift.receipt_no)

    try:
        selcom.create_order(
            order_id=gift.receipt_no,
            amount=gift.amount,
            buyer_name=gift.donor_name or "Mchangiaji",
            buyer_phone=phone,
            buyer_email=gift.contact_email,
            webhook_url=f"{st.SITE_URL}{reverse('core:selcom_webhook')}",
            #: `gift.amount` IMESHABADILISHWA kwenda TZS na `to_tzs()`.
            #: Kutuma namba hiyo pamoja na alama ya fedha ya asili
            #: kulimaanisha mtu aliyechangia $100 aliombwa $261,500.
            currency="TZS",
        )
        # Hifadhi KABLA ya kutuma kidokezo: kidokezo kikigoma, bado
        # tunaweza kuuliza Selcom hali ya order hii.
        gift.gateway = "selcom"
        gift.gateway_ref = gift.receipt_no
        gift.save(update_fields=["gateway", "gateway_ref"])

        selcom.push_ussd(order_id=gift.receipt_no, phone=phone)
    except selcom.SelcomError as exc:
        messages.error(request, _(
            "Hatukuweza kuanzisha malipo kwa sasa: %(sababu)s. "
            "Mchango wako umehifadhiwa — jaribu tena au wasiliana nasi."
        ) % {"sababu": exc})
        return redirect("core:changia_asante", receipt=gift.receipt_no)

    request.session["mwst_last_gift"] = gift.receipt_no
    return redirect("core:selcom_subiri", receipt=gift.receipt_no)


def _may_see_gift(request, gift):
    """
    Je, huyu anaruhusiwa kuona risiti hii?

    Ukaguzi wa awali ulikuwa `... and not request.user.is_authenticated`,
    yaani MTU YEYOTE aliyeingia — hata mhisani aliyejisajili mwenyewe
    dakika iliyopita — aliweza kusoma risiti zote. Namba za risiti
    zinafuatana (MUWESTA-M-000001, -000002...), kwa hiyo daftari lote la
    michango lilikuwa linasomeka kwa loop moja: jina la mtoaji, kiasi,
    mfuko na hali.

    Sasa ni tatu tu: aliyechangia kwenye kipindi hiki, mwenye rekodi
    hiyo, au afisa.
    """
    if request.session.get("mwst_last_gift") == gift.receipt_no:
        return True
    user = request.user
    if not user.is_authenticated:
        return False
    if user.is_staff or getattr(user, "is_staff_role", False):
        return True
    if gift.donor_id and gift.donor.user_id == user.pk:
        return True
    member = getattr(user, "member", None)
    return bool(member and gift.member_id == member.pk)


def _selcom_sync(gift):
    """
    Thibitisha hali halisi ya malipo kwa Selcom.

    Kama ilivyo kwa Pesapal: webhook ni ishara tu. Hali halisi
    inachukuliwa hapa, si kutoka kwenye kile kilichotumwa kwetu.
    """
    from finance.gateways import selcom
    from finance.models import Contribution

    if not gift.gateway_ref:
        return gift
    try:
        body = selcom.order_status(gift.gateway_ref)
    except selcom.SelcomError:
        return gift

    #: `Contribution.settle` inashika kufuli la safu kabla ya kubadilisha
    #: hali. Bila hilo, webhook ya Selcom na kipima-hali cha ukurasa wa
    #: kusubiri (kinachouliza kila sekunde chache) vilikuwa vinaweza
    #: kubadilisha mchango ule ule kwa wakati mmoja.
    gift, _changed = Contribution.settle(gift.pk, selcom.payment_status(body))
    return gift


def selcom_subiri(request, receipt):
    """
    Ukurasa wa kusubiri wakati mtu anaingiza PIN kwenye simu yake.

    Unajisasisha kila sekunde chache. Mtu akikamilisha, unampeleka
    kwenye risiti; akighairi, unamwambia na kumpa nafasi ya kujaribu tena.
    """
    from finance.models import Contribution, PaymentStatus

    gift = get_object_or_404(Contribution, receipt_no=receipt)
    if not _may_see_gift(request, gift):
        raise Http404

    _selcom_sync(gift)
    if gift.status != PaymentStatus.PENDING:
        return redirect("core:changia_asante", receipt=gift.receipt_no)

    return render(request, "public/selcom_subiri.html",
                  _pub(request, "changia", {
                      "gift": gift,
                      "phone": gift.contact_phone,
                  }))


def selcom_hali(request, receipt):
    """
    Hali ya malipo kwa JSON — inaulizwa na ukurasa wa kusubiri.

    Inarudisha hali pekee, si taarifa za mtu — kwa hiyo hata mtu
    akikisia namba ya risiti, hapati chochote cha thamani.
    """
    from django.http import JsonResponse
    from finance.models import Contribution

    gift = get_object_or_404(Contribution, receipt_no=receipt)
    #: Ukaguzi huu haukuwepo. Kila ombi hapa linapiga simu ya nje kwa
    #: Selcom (`order_status`, sekunde 20 za kusubiri), kwa hiyo mtu
    #: yeyote aliyejua muundo wa namba ya risiti angeweza kumaliza
    #: kiwango chetu cha Selcom kwa loop rahisi.
    if not _may_see_gift(request, gift):
        raise Http404
    _selcom_sync(gift)
    gift.refresh_from_db()
    return JsonResponse({"status": gift.status})


@csrf_exempt
def selcom_webhook(request):
    """
    Selcom inapiga hapa malipo yanapokamilika.

    Haiaminiki yenyewe — inatuambia tu "kuna mabadiliko". Hali halisi
    inachukuliwa kwa `order_status`, sawa na tunavyofanya kwa Pesapal.
    """
    from finance.models import Contribution

    try:
        data = json.loads(request.body.decode() or "{}")
    except ValueError:
        data = request.POST

    order_id = data.get("order_id") or data.get("transid") or ""
    gift = Contribution.objects.filter(receipt_no=order_id).first()
    if gift is None:
        gift = Contribution.objects.filter(gateway_ref=order_id).first()
    if gift is not None:
        _selcom_sync(gift)
    else:
        log.warning("Selcom webhook: order %r haijulikani", order_id)

    return HttpResponse("OK")


def _pesapal_start(request, gift, description):
    """
    Peleka mtumiaji kwenye ukurasa wa malipo wa Pesapal.

    Ikishindikana kwa sababu yoyote, mchango unabaki `pending` na mtumiaji
    anapelekwa kwenye ukurasa wa shukrani na maelezo — hatupotezi rekodi
    kwa sababu tu gateway imegoma.
    """
    from django.conf import settings as st
    from finance.gateways import pesapal

    names = (gift.donor_name or "").split(None, 1)
    try:
        tracking, redirect_url = pesapal.submit_order(
            merchant_reference=gift.receipt_no,
            amount=gift.amount,
            description=description,
            callback_url=f"{st.SITE_URL}{reverse('core:pesapal_callback')}",
            #: TZS DAIMA. `gift.amount` tayari imepitishwa kwenye
            #: `to_tzs()`, kwa hiyo kutuma alama ya fedha ya asili
            #: kulikuwa kunaomba kiasi cha TZS kwa fedha hiyo: $100
            #: kilikuwa $261,500, €100 kikawa €284,000.
            currency="TZS",
            first_name=names[0] if names else "",
            last_name=names[1] if len(names) > 1 else "",
            #: `/lipa/` haiweki `donor`, kwa hiyo kusoma `donor.email`
            #: pekee kulipeleka Pesapal ombi lisilo na njia yoyote ya
            #: mawasiliano — jambo ambalo `SubmitOrderRequest` inakataa.
            email=gift.contact_email,
            phone=gift.contact_phone,
        )
    except pesapal.PesapalError as exc:
        messages.error(request, _(
            "Hatukuweza kuanzisha malipo kwa sasa: %(sababu)s. "
            "Mchango wako umehifadhiwa — jaribu tena au wasiliana nasi."
        ) % {"sababu": exc})
        return redirect("core:changia_asante", receipt=gift.receipt_no)

    gift.gateway = "pesapal"
    gift.gateway_ref = tracking
    gift.save(update_fields=["gateway", "gateway_ref"])
    return redirect(redirect_url)


def _finish_payment(request, gift, provider_key, description):
    """
    Peleka mtu mahali panapostahili baada ya rekodi kuundwa.

    Njia inayopitia Pesapal humpeleka Pesapal. Uhamisho wa benki humwacha
    kwenye risiti ikiwa `pending`, na ujumbe unasema wazi kwamba malipo
    bado hayajakamilika — hakuna mahali mfumo unapodai pesa imeingia
    wakati haijaingia.
    """
    from core.data import giving

    gateway = giving.gateway_for(provider_key)

    if gateway == "selcom":
        if not _selcom_ready():
            log.error("Selcom haijakamilika kusanidiwa; ombi %s limebaki pending",
                      gift.receipt_no)
            messages.error(request, _(
                "Malipo ya simu hayapatikani kwa sasa. Ombi lako "
                "limehifadhiwa kwa namba %(risiti)s — tafadhali wasiliana "
                "nasi ili likamilishwe."
            ) % {"risiti": gift.receipt_no})
            return redirect("core:changia_asante", receipt=gift.receipt_no)
        return _selcom_start(request, gift, description)

    if gateway == "pesapal":
        if not _pesapal_ready():
            log.error("Pesapal haijakamilika kusanidiwa; ombi %s limebaki pending",
                      gift.receipt_no)
            messages.error(request, _(
                "Malipo ya mtandaoni hayapatikani kwa sasa. Ombi lako "
                "limehifadhiwa kwa namba %(risiti)s — tafadhali wasiliana "
                "nasi ili likamilishwe."
            ) % {"risiti": gift.receipt_no})
            return redirect("core:changia_asante", receipt=gift.receipt_no)
        return _pesapal_start(request, gift, description)

    if gateway == "manual":
        messages.info(request, _(
            "Ombi lako limehifadhiwa kwa namba %(risiti)s. Tumia namba hiyo "
            "kama kumbukumbu unapotuma pesa benki; risiti itathibitishwa "
            "mara malipo yatakapopokelewa."
        ) % {"risiti": gift.receipt_no})
        return redirect("core:changia_asante", receipt=gift.receipt_no)

    # Njia isiyotambulika — haifai kuendelea kimya kimya.
    log.error("Njia ya malipo isiyotambulika: %r (risiti %s)",
              provider_key, gift.receipt_no)
    messages.error(request, _(
        "Njia ya malipo uliyochagua haipatikani. Ombi lako limehifadhiwa "
        "kwa namba %(risiti)s."
    ) % {"risiti": gift.receipt_no})
    return redirect("core:changia_asante", receipt=gift.receipt_no)


def _pesapal_sync(gift):
    """
    Thibitisha hali halisi ya malipo kwa Pesapal.

    Callback PEKEE haiaminiki — mtu anaweza kuiita mwenyewe kwenye
    kivinjari. Hali inathibitishwa hapa, si kutoka kwenye URL.
    """
    from finance.gateways import pesapal
    from finance.models import Contribution

    if not gift.gateway_ref:
        return gift
    try:
        body = pesapal.transaction_status(gift.gateway_ref)
    except pesapal.PesapalError:
        return gift

    #: Angalia `Contribution.settle` kwa sababu ya kufuli. Hapa kuna
    #: jambo la ziada: hapo awali tawi la `failed` halikuwa na ukaguzi
    #: wa hali, kwa hiyo mchango ULIOKWISHA thibitishwa na kuingia
    #: leja ungeweza kugeuzwa `failed` na kidokezo kutoka nje.
    gift, _changed = Contribution.settle(gift.pk, pesapal.map_status(body))
    return gift


def pesapal_callback(request):
    """
    Mtumiaji anarudishwa hapa baada ya kulipa.

    Mchango unatafutwa kwa `OrderTrackingId` PEKEE. Awali ilikuwa
    ikikubali pia `OrderMerchantReference`, ambayo ni namba ya risiti
    yetu inayofuatana (MUWESTA-M-000001, -000002...). Mtu yeyote
    angeweza kuomba URL hii kwa namba yoyote, session yake ikapewa
    ruhusa ya risiti hiyo, na daftari lote la michango likasomeka kwa
    `for` loop. `OrderTrackingId` ni UUID inayotolewa na Pesapal —
    haikisiwi.
    """
    from finance.models import Contribution, PaymentStatus

    tracking = (request.GET.get("OrderTrackingId") or "").strip()
    gift = (Contribution.objects.filter(gateway_ref=tracking).first()
            if tracking else None)
    if gift is None:
        raise Http404

    _pesapal_sync(gift)
    gift.refresh_from_db()
    request.session["mwst_last_gift"] = gift.receipt_no
    if gift.status == PaymentStatus.CONFIRMED:
        messages.success(request, _("Malipo yako yamekamilika. Asante!"))
    elif gift.status == PaymentStatus.FAILED:
        messages.error(request, _("Malipo hayakukamilika. Unaweza kujaribu tena."))
    else:
        messages.info(request, _(
            "Malipo yako yanashughulikiwa. Utapata uthibitisho hivi punde."))
    return redirect("core:changia_asante", receipt=gift.receipt_no)


@csrf_exempt
def pesapal_ipn(request):
    """
    Pesapal inapiga hapa hali inapobadilika.

    Haiaminiki yenyewe — inatuambia tu "kuna mabadiliko". Hali halisi
    inachukuliwa kwa GetTransactionStatus.
    """
    from finance.models import Contribution

    data = request.POST if request.method == "POST" else request.GET
    tracking = data.get("OrderTrackingId", "")
    reference = data.get("OrderMerchantReference", "")

    gift = (Contribution.objects.filter(gateway_ref=tracking).first()
            or Contribution.objects.filter(receipt_no=reference).first())
    if gift is not None:
        _pesapal_sync(gift)

    # Pesapal inatarajia jibu hili hasa.
    return JsonResponse({
        "orderNotificationType": data.get("OrderNotificationType", "IPNCHANGE"),
        "orderTrackingId": tracking,
        "orderMerchantReference": reference,
        "status": 200,
    })


def matangazo(request):
    """Orodha ya matangazo yote yaliyoidhinishwa."""
    return render(request, "public/matangazo.html",
                  _pub(request, "matangazo",
                       {"items": q.live_announcements(limit=50)}))


def tangazo(request, pk):
    """Maelezo kamili ya tangazo moja."""
    from content.models import Announcement

    item = get_object_or_404(Announcement, pk=pk, is_active=True, status="approved")
    others = [a for a in q.live_announcements(limit=5) if a.pk != item.pk][:3]
    return render(request, "public/tangazo.html",
                  _pub(request, "matangazo", {"item": item, "others": others}))


def vifurushi(request):
    """Mpangilio wa vifurushi vya uanachama — bango la MUWESTA kwa mtandao."""
    return render(request, "public/vifurushi.html",
                  _pub(request, "vifurushi", q.public_vifurushi()))


# ===========================================================================
#  KUCHANGIA BILA AKAUNTI + AKAUNTI YA MHISANI
# ===========================================================================
def changia(request):
    """
    Fomu ya michango ya umma.

    Hakuna akaunti inayohitajika. Mchango unaingia kama `pending`, kisha
    `_finish_payment` inaupeleka Pesapal au inauacha usubiri uthibitisho
    wa afisa, kutegemea njia iliyochaguliwa. Hali haibadiliki kuwa
    `confirmed` mpaka Pesapal au afisa athibitishe.
    """
    from finance.models import Donor, Project

    # --- Mradi alioufuata, kama amefika kupitia kadi ya mradi -------------
    # `?mradi=` ilikuwa inapitishwa kama KICHWA cha mradi na haikusomwa
    # kamwe, kwa hiyo mchango haukuunganishwa na mradi wowote. Sasa ni
    # namba, na inasomwa hapa.
    project = None
    suggested = []
    raw = (request.GET.get("mradi") or "").strip()
    if raw.isdigit():
        project = Project.objects.filter(pk=int(raw), status="ongoing").first()
        if project is not None and project.is_full():
            # Lengo limetimia — usimwache atume fedha zisizohitajika.
            messages.info(request, _(
                "Lengo la mradi wa \"%(m)s\" limetimia — asante kwa wote "
                "waliochangia. Hapa kuna miradi mingine inayohitaji msaada."
            ) % {"m": project.tx("title")})
            suggested = Project.suggest_other(exclude_pk=project.pk)
            project = suggested[0] if suggested else None

    lang = get_language()
    catalogue = {
        "project": project,
        "suggested": suggested,
        "purposes": giving.localise(giving.PURPOSES, lang),
        "purpose_groups": giving.localise(giving.PURPOSE_GROUPS, lang),
        "recurrences": giving.localise(giving.RECURRENCES, lang),
        "providers": giving.localise(giving.PROVIDERS, lang),
        "provider_groups": giving.localise(giving.PROVIDER_GROUPS, lang),
        #: Njia ya malipo haionyeshwi tena; inawekwa kama sehemu iliyofichwa.
        "default_provider": giving.DEFAULT_PROVIDER,
        "currencies": giving.currencies(),
        "presets": giving.PRESETS,
    }

    if request.method == "POST":
        form = PublicDonationForm(request.POST)
        if form.is_valid():
            gift = form.save()
            data = form.cleaned_data

            donor = None
            if request.user.is_authenticated:
                donor = Donor.objects.filter(user=request.user).first()
            if donor is None:
                lookup = Q()
                if data.get("email"):
                    lookup |= Q(email__iexact=data["email"])
                if data.get("phone"):
                    lookup |= Q(phone=data["phone"])
                if lookup:
                    donor = Donor.objects.filter(lookup).first()
            if donor is None:
                donor = Donor.objects.create(
                    name=data["full_name"], phone=data["phone"],
                    email=data.get("email", ""), donor_type="individual")
            gift.donor = donor
            gift.save()

            AuditLog.record(request, "public_donation", gift)
            request.session["mwst_last_gift"] = gift.receipt_no
            spec = giving.purpose(data["purpose"])
            return _finish_payment(request, gift, data.get("provider", ""),
                                   spec["name"] if spec else str(_("Mchango")))
        messages.error(request, _("Tafadhali sahihisha makosa hapa chini."))
    else:
        initial = {"purpose": request.GET.get("aina", "sadaqah"),
                   "currency": "TZS", "recurrence": "once", "provider": "pesapal",
                   "amount": 20000}
        initial["project"] = project
        if request.user.is_authenticated:
            donor = Donor.objects.filter(user=request.user).first()
            initial.update({
                "full_name": donor.name if donor else request.user.get_full_name(),
                "email": donor.email if donor else request.user.email,
                "phone": donor.phone if donor else "",
            })
        form = PublicDonationForm(initial=initial)

    return render(request, "public/changia.html",
                  _pub(request, "changia",
                       {"form": form, "hero": q.CHANGIA_HERO, **catalogue}))


def lipa(request):
    """
    Lipa ada ya uanachama.

    Kiasi kinahesabiwa upya kwenye seva kutoka `Category.monthly_fee`;
    hakichukuliwi kutoka kwenye fomu, hivyo mtu hawezi kubadilisha bei
    kwenye kivinjari akalipa kidogo. Malipo yanakamilishwa na
    `_finish_payment` kama ilivyo kwenye michango.
    """
    from finance.models import Contribution, Fund, PaymentStatus

    lang = get_language()
    ctx = q.public_lipa(lang)

    if request.method == "POST":
        form = MembershipPaymentForm(request.POST)
        if form.is_valid():
            totals = form.totals()
            data = form.cleaned_data
            fund = (Fund.objects.filter(code="ada").first()
                    or Fund.objects.order_by("order").first())
            gift = Contribution.objects.create(
                fund=fund,
                #: Malipo yanaunganishwa na ombi au mwanachama hapa. Bila
                #: hii, pesa ingeingia lakini rekodi ya mtu isingesogea.
                application=form.application,
                member=form.member,
                amount=totals["total"],
                entered_amount=totals["total"],
                currency="TZS",
                #: "ada" = mchango wa mwezi (hauguzi muda wa uanachama),
                #: "uhuisho" = kipindi kingine cha miaka mitatu.
                purpose=totals["kind"],
                recurrence="",
                months=totals["months"],
                method=data["provider"][:12],
                note=(data.get("note") or "")[:200],
                status=PaymentStatus.PENDING,
                donor_name=data["full_name"],
                donor_phone=data.get("phone", ""),
                donor_email=data.get("email", ""))
            AuditLog.record(request, "membership_payment", gift)
            request.session["mwst_last_gift"] = gift.receipt_no
            return _finish_payment(
                request, gift, data.get("provider", ""),
                (f"{_('Kuhuisha uanachama')} - {totals['category'].name}"
                 if totals["kind"] == "uhuisho"
                 else f"{_('Mchango wa mwanachama')} - {totals['category'].name}"))
        messages.error(request, _("Tafadhali sahihisha makosa hapa chini."))
    else:
        initial = {"months": 12, "payer_type": "new", "provider": "pesapal",
                   "pay_kind": "ada"}
        featured = next((p for p in ctx["packages"] if p["featured"]), None)
        initial["package"] = (featured or ctx["packages"][0])["code"] if ctx["packages"] else ""

        # Namba ya ombi inaweza kuja kwenye kiungo alichopewa na afisa:
        #   /lipa/?ombi=APP/MUWESTA/2026/0001
        ref = request.GET.get("ombi", "").strip()
        if ref:
            #: Taarifa binafsi hujazwa tu ikiwa kiungo kina saini
            #: iliyotoka kwenye SMS yetu, AU ikiwa afisa ndiye
            #: aliyefungua. Bila hivyo mwombaji anaweza kuendelea
            #: mwenyewe, lakini fomu haimwambii mtu yeyote taarifa za
            #: mtu mwingine.
            app = Application.by_pay_token(ref, request.GET.get("k", "").strip())
            if app is None and request.user.is_authenticated \
                    and request.user.role in STAFF_ONLY:
                app = Application.objects.filter(reference__iexact=ref).first()
            if app and not app.member_id:
                initial.update({"payer_type": "new", "membership_no": app.reference,
                                "full_name": app.full_name, "phone": app.phone,
                                "email": app.email, "package": app.category.code,
                                "include_registration": True})
            elif app is None:
                messages.info(request, _(
                    "Ili taarifa zako zijazwe zenyewe, tumia kiungo "
                    "kilichokuja kwenye ujumbe wa simu."))

        # Arifa ya muda kuisha inampeleka mtu hapa: /lipa/?huisha=1
        if request.GET.get("huisha"):
            initial["pay_kind"] = "uhuisho"

        if request.user.is_authenticated:
            member = getattr(request.user, "member", None)
            if member:
                initial.update({"payer_type": "member",
                                "full_name": member.full_name,
                                "membership_no": member.membership_no,
                                "package": member.category.code,
                                "phone": member.phone, "email": member.email})
        form = MembershipPaymentForm(initial=initial)

    ctx["form"] = form
    return render(request, "public/lipa.html", _pub(request, "lipa", ctx))


def changia_asante(request, receipt):
    """Ukurasa wa shukrani + mwaliko wa kufungua akaunti ya mhisani."""
    from finance.models import Contribution

    gift = get_object_or_404(Contribution, receipt_no=receipt)
    # Risiti si siri kubwa, lakini haipaswi kuvinjariwa na mtu yeyote.
    # Tunaonyesha tu kama ndiyo mchango uliotolewa kwenye kipindi hiki.
    if not _may_see_gift(request, gift):
        raise Http404

    has_account = bool(gift.donor and gift.donor.user_id)
    # Ada ya uanachama si mchango wa kawaida — mlipaji anakuwa mwanachama,
    # kwa hiyo hafai kualikwa kufungua akaunti ya mhisani. Badala yake
    # anaonyeshwa taarifa zake za uanachama.
    is_fee = gift.purpose == "ada"
    member = gift.member if is_fee else None

    #: Kiungo cha kuweka nenosiri. Awali ukurasa huu ulikuwa ukijaribu
    #: kuonyesha `member.temp_password` — sifa iliyowekwa kwenye
    #: kumbukumbu ya request ya callback ya Pesapal, si kwenye database.
    #: Ilikuwa `None` KILA MARA hapa, kwa sababu `gift` inasomwa upya
    #: kutoka database. Sasa tunaonyesha kiungo chenye saini, na
    #: MLIPAJI PEKEE ndiye anayekiona: si afisa, si mtu mwingine
    #: anayeruhusiwa kuiona risiti. Kiungo kinaweka nenosiri, kwa hiyo
    #: si cha kupita kwa mtu wa tatu.
    setup_url = None
    if member is not None and member.user_id \
            and request.session.get("mwst_last_gift") == gift.receipt_no:
        setup_url = member.setup_path()

    return render(request, "public/changia_asante.html",
                  _pub(request, "changia", {
                      "gift": gift,
                      "is_fee": is_fee,
                      "member": member,
                      "setup_url": setup_url,
                      "has_account": has_account,
                      "show_invite": (not is_fee and not has_account
                                      and not request.user.is_authenticated),
                  }))


def donor_register(request):
    """
    Kufungua akaunti ya mhisani. Inafanywa baada ya kuchangia ili
    michango iliyopita iunganishwe na akaunti mpya.
    """
    from django.contrib.auth import get_user_model
    from finance.models import Contribution, Donor

    if request.user.is_authenticated:
        return redirect(request.user.home_url_name())

    receipt = request.GET.get("risiti") or request.POST.get("receipt") or ""
    gift = Contribution.objects.filter(receipt_no=receipt).first() if receipt else None

    if request.method == "POST":
        form = DonorSignupForm(request.POST)
        if form.is_valid():
            User = get_user_model()
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data["email"], email=data["email"],
                password=data["password1"], role=Role.DONOR)
            parts = data["full_name"].split(None, 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ""
            user.save(update_fields=["first_name", "last_name"])

            donor = (gift.donor if gift and gift.donor else None) or \
                Donor.objects.filter(Q(email__iexact=data["email"]) |
                                     Q(phone=data["phone"])).first()
            if donor is None:
                donor = Donor.objects.create(name=data["full_name"],
                                             donor_type="individual")
            donor.user = user
            donor.name = data["full_name"]
            donor.email = data["email"]
            donor.phone = data["phone"]
            donor.save()

            # Unganisha michango ya nyuma iliyotolewa kwa simu/barua pepe hiyo.
            #
            # Ukaguzi ulikuwa wa JINA PEKEE. Jina si siri — linaonekana
            # kwenye ukurasa wa shukrani na kwenye orodha ya wahisani.
            # Mtu angeweza kujisajili kwa jina la mwingine na michango
            # yote ya mtu huyo ikahamia kwake: akaiona, na mwenyewe
            # akaipoteza. Sasa lazima simu au barua pepe ilingane, na
            # jina liendelee kutumika kama kiungo cha ziada tu.
            phone = (data["phone"] or "").strip()
            match = Q(donor_email__iexact=data["email"])
            if phone:
                match |= Q(donor_phone=phone)
            claimed = Contribution.objects.filter(donor__isnull=True).filter(match)
            #: Risiti aliyoitumia kufungua akaunti inahesabika yenyewe —
            #: ndiyo uthibitisho wa moja kwa moja kwamba ni wake.
            if gift is not None and gift.donor_id is None:
                claimed = claimed | Contribution.objects.filter(pk=gift.pk)
            claimed.update(donor=donor)

            auth_login(request, user)
            AuditLog.record(request, "donor_signup", donor)
            messages.success(request, _(
                "Akaunti yako ya mhisani iko tayari. Michango yako yote "
                "itaonekana hapa."))
            return redirect("core:donor_dashboard")
        messages.error(request, _("Tafadhali sahihisha makosa hapa chini."))
    else:
        initial = {}
        if gift:
            initial = {"full_name": gift.donor.name if gift.donor else gift.donor_name,
                       "email": gift.donor.email if gift.donor else "",
                       "phone": gift.donor.phone if gift.donor else ""}
        form = DonorSignupForm(initial=initial)

    return render(request, "public/donor_register.html",
                  _pub(request, "changia", {"form": form, "gift": gift,
                                            "receipt": receipt}))


@login_required
def donor_dashboard(request):
    """Kumbukumbu za michango ya mhisani mmoja."""
    from django.db.models import Sum
    from finance.models import Contribution, Donor, PaymentStatus

    donor = Donor.objects.filter(user=request.user).first()
    gifts = (Contribution.objects.filter(donor=donor).select_related("fund", "project")
             if donor else Contribution.objects.none())

    confirmed = gifts.filter(status=PaymentStatus.CONFIRMED)
    by_fund = (confirmed.values("fund__name", "fund__colour")
               .annotate(total=Sum("amount")).order_by("-total"))

    # Mhisani tayari ni mwanachama? Kama ndiyo, mwaliko wa kujiunga
    # hauna maana — badala yake tunamwonyesha kiungo cha dashibodi yake.
    member = getattr(request.user, "member", None)

    return render(request, "public/donor_dashboard.html",
                  _pub(request, "changia", {
                      "donor": donor,
                      "gifts": gifts[:50],
                      "total": confirmed.aggregate(s=Sum("amount"))["s"] or 0,
                      "count": confirmed.count(),
                      "pending": gifts.filter(status=PaymentStatus.PENDING).count(),
                      "by_fund": by_fund,
                      "member": member,
                      "causes": q.donor_causes(limit=4),
                      "membership": q.membership_invite(get_language()),
                  }))


def faragha(request):
    """Sera ya Faragha — maudhui kamili kwa lugha ya mtumiaji."""
    doc = legal.privacy(get_language())
    return render(request, "public/legal.html",
                  _pub(request, "faragha", {"doc": doc}))


def masharti(request):
    """Masharti ya Huduma — maudhui kamili kwa lugha ya mtumiaji."""
    doc = legal.terms(get_language())
    return render(request, "public/legal.html",
                  _pub(request, "masharti", {"doc": doc}))


def vidakuzi(request):
    """Sera ya Vidakuzi."""
    doc = legal.cookies(get_language())
    return render(request, "public/legal.html",
                  _pub(request, "vidakuzi", {"doc": doc}))


def mawasiliano(request):
    ctx = q.public_mawasiliano()
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            msg = form.save()
            AuditLog.record(request, "contact_message", msg)
            messages.success(request, _("Asante. Ujumbe wako umepokelewa; "
                                        "tutakujibu ndani ya saa 24 za kazi."))
            return redirect("core:mawasiliano")
        messages.error(request, _("Tafadhali sahihisha makosa hapa chini."))
    else:
        # Mgeni akitoka kwenye ukurasa wa mradi, tumjazie mada na mradi
        initial = {}
        subject = request.GET.get("mada")
        if subject in ContactForm.SUBJECTS:
            initial["subject"] = subject
        project = request.GET.get("mradi")
        if project:
            initial["body"] = _("Nataka kuchangia mradi wa %(p)s. Tafadhali "
                                "nielekeze jinsi ya kulipa.") % {"p": project[:120]}
        form = ContactForm(initial=initial)
    ctx["form"] = form
    return render(request, "public/mawasiliano.html", _pub(request, "mawasiliano", ctx))


def jiunge(request):
    ctx = q.public_jiunge()
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            from . import sms

            app = form.save()
            AuditLog.record(request, "application_submitted", app)
            #: Awali ujumbe huu ulisema mtu "utapigiwa simu na kupewa
            #: namba yako ya uanachama pamoja na nenosiri". Hakuna hatua
            #: ya mfumo inayofanya hivyo: baada ya kuhakikiwa, hatua
            #: inayofuata ni KULIPA, na namba ya uanachama hutolewa
            #: malipo yakithibitishwa. Ahadi isiyo ya kweli inamfanya
            #: mtu asubiri simu isiyokuja.
            messages.success(request, _(
                "Ombi lako limepokelewa. Namba ya kumbukumbu ni %(ref)s — "
                "iandike. Afisa wa usajili atahakiki taarifa zako, kisha "
                "utapata ujumbe wenye kiungo cha kulipia ada. Namba yako ya "
                "uanachama, kadi na akaunti hutolewa malipo yakithibitishwa."
            ) % {"ref": app.reference})

            # Hongera kwanza — inampa namba ya kumbukumbu na kumweleza
            # hatua inayofuata. Kisha code ya kuthibitisha namba.
            sms.send_application_received(app.phone, app.reference)

            # Namba ya simu inathibitishwa sasa hivi — ndipo mtu bado
            # yupo mbele ya skrini. Ikisubiri hadi afisa amhakiki, namba
            # yenye kosa inagundulika baada ya siku, na afisa anapiga
            # simu isiyopatikana.
            return _start_phone_check(request, app)
        messages.error(request, _("Tafadhali sahihisha makosa hapa chini."))
    else:
        form = ApplicationForm()
    ctx["form"] = form
    return render(request, "public/jiunge.html", _pub(request, "uanachama", ctx))




def _start_phone_check(request, app):
    """Tuma code ya kuthibitisha namba ya ombi jipya."""
    from accounts.models import CodePurpose, VerificationCode
    from . import sms

    to = sms.msisdn(app.phone)
    if VerificationCode.too_many(to):
        return redirect("core:jiunge")

    row, code = VerificationCode.issue(to, CodePurpose.PHONE,
                                       reference=app.reference,
                                       ip=_client_ip(request))
    if not sms.send_code(app.phone, code, "phone", VerificationCode.TTL_MINUTES):
        log.error("Code ya kuthibitisha haikutumwa kwa %s", to)
        #: Mstari ulikuwa umeandikwa kama escape ya Python (`\\u2014`).
        #: Python inaibadilisha kuwa herufi moja wakati wa kuendesha,
        #: lakini `xgettext` huihifadhi kama herufi sita za escape. Kwa
        #: hiyo msgid kwenye `.po` haikulingana na maandishi halisi
        #: yanayoombwa, na sentensi hii haikuwa na njia ya kutafsiriwa
        #: kabisa. Herufi halisi hapa inaondoa tofauti hiyo.
        messages.info(request, _(
            "Hatukuweza kutuma code kwenye simu yako sasa hivi. Ombi lako "
            "limehifadhiwa — afisa atawasiliana nawe."))
        return redirect("core:jiunge")

    request.session["mwst_verify_ref"] = app.reference
    return redirect("core:thibitisha_simu")


def thibitisha_simu(request):
    """
    Kuthibitisha namba ya simu ya mwombaji.

    Kukosa kuthibitisha HAKUZUII ombi. Ombi tayari limehifadhiwa; hii
    inaongeza uhakika tu kwamba namba ni sahihi na inapatikana. Mtu
    asiye na simu mkononi sasa hivi asizuiwe kujiunga.
    """
    from accounts.models import CodePurpose, VerificationCode
    from . import sms

    ref = request.session.get("mwst_verify_ref")
    if not ref:
        return redirect("core:jiunge")
    app = Application.objects.filter(reference=ref).first()
    if app is None:
        request.session.pop("mwst_verify_ref", None)
        return redirect("core:jiunge")

    to = sms.msisdn(app.phone)
    if request.method == "POST":
        if request.POST.get("resend"):
            if VerificationCode.too_many(to):
                messages.error(request, _("Umeomba code nyingi mno. Subiri kidogo."))
            else:
                row, code = VerificationCode.issue(
                    to, CodePurpose.PHONE, reference=app.reference,
                    ip=_client_ip(request))
                sms.send_code(app.phone, code, "phone", VerificationCode.TTL_MINUTES)
                messages.info(request, _("Tumekutumia code nyingine."))
            return redirect("core:thibitisha_simu")

        row, err = VerificationCode.verify(to, CodePurpose.PHONE,
                                           request.POST.get("code", ""))
        if err is None:
            app.phone_verified = True
            app.save(update_fields=["phone_verified", "updated_at"])
            AuditLog.record(request, "phone_verified", app)
            request.session.pop("mwst_verify_ref", None)
            messages.success(request, _("Namba yako imethibitishwa. Asante!"))
            return redirect("core:jiunge")

        messages.error(request, {
            "none": _("Hakuna code inayosubiri. Omba nyingine."),
            "expired": _("Code hii imeisha muda. Omba nyingine."),
            "attempts": _("Umejaribu mara nyingi mno. Omba code nyingine."),
        }.get(err, _("Code si sahihi. Jaribu tena.")))

    return render(request, "public/otp.html", {
        "page_title": _("Thibitisha namba yako"),
        "page_lead": _("Tumekutumia code ya tarakimu sita. Iweke hapa "
                       "kuthibitisha kuwa namba hii ni yako."),
        "submit_label": _("Thibitisha"),
        "back_url": reverse("core:jiunge"),
        "back_label": _("Nitafanya baadaye"),
        "target": _mask_phone(app.phone),
        "minutes": VerificationCode.TTL_MINUTES,
    })


@require_POST
def event_register(request, pk):
    event = get_object_or_404(Event, pk=pk, is_public=True)
    member = getattr(request.user, "member", None) if request.user.is_authenticated else None
    if member:
        EventRegistration.objects.get_or_create(
            event=event, member=member,
            defaults={"full_name": member.full_name, "phone": member.phone,
                      "email": member.email})
        messages.success(request, _("Umejiandikisha kwenye %(title)s.") % {"title": event.title})
    else:
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            reg = form.save(commit=False)
            reg.event = event
            reg.save()
            messages.success(request, _("Umejiandikisha kwenye %(title)s.") % {"title": event.title})
        else:
            messages.error(request, _("Tafadhali jaza jina na namba ya simu."))
    return redirect(_back(request, reverse("core:matukio_umma")))


def api_districts(request):
    #: `?region=abc` ilikuwa inatoa `ValueError` isiyoshikwa — yaani 500
    #: kwa kila mtu aliyeandika kitu kisicho namba, na njia rahisi ya
    #: kujaza log ya makosa.
    region = (request.GET.get("region") or "").strip()
    rows = (District.objects.filter(region_id=int(region)).values("id", "name")
            if region.isdigit() else [])
    return JsonResponse({"results": list(rows)})


def api_wards(request):
    district = (request.GET.get("district") or "").strip()
    rows = (Ward.objects.filter(district_id=int(district)).values("id", "name")
            if district.isdigit() else [])
    return JsonResponse({"results": list(rows)})


def card_verify(request, serial):
    """
    Uhakiki wa kadi kwa QR. Ni ukurasa wa umma — hauhitaji kuingia.

    Unaonyesha taarifa za msingi pekee (jina, daraja, uhalali). Simu,
    barua pepe, kitambulisho na anuani havionyeshwi hadharani.
    """
    real = serial.replace("-", "/")
    card = (Card.objects
            .select_related("member", "member__category", "member__region")
            .filter(serial=real).first())
    today = timezone.localdate()
    return render(request, "public/verify.html", _pub(request, "", {
        "card": card,
        "m": card.member if card else None,
        "serial": real,
        "checked_at": timezone.localtime(),
        "expired": bool(card and card.expires_on and card.expires_on < today),
        "settings_obj": SiteSetting.get(),
    }))


# ===========================================================================
#  DASHBOARDS
# ===========================================================================
@role_required(*ADMINS_PLUS)
def national(request):
    ctx = _gate_actions(q.national(year=_active_year(request),
                                   region_ids=scope_regions(request.user)),
                        request.user)
    nav = (navs.coordinator("taifa") if user_zone(request.user)
           else navs.national("dashboard"))
    ctx.update(_chrome(request, nav=nav,
                       topbar_title="MUWESTA Membership Management System",
                       topbar_sub="Dashboard - Msimamizi Mkuu (Mikoa Yote za Tanzania)",
                       map_regions=tz_map(ctx["regions"]),
                       map_legend=tz_legend(ctx["regions"])))
    return render(request, "admin_panel/national.html", ctx)


@role_required(*REG_ROLES)
def usajili(request):
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save()
            AuditLog.record(request, "application_created", app)
            messages.success(request, _("Ombi %(ref)s limehifadhiwa.") % {"ref": app.reference})
            return redirect("core:usajili")
        messages.error(request, _("Tafadhali sahihisha makosa hapa chini."))
    else:
        form = ApplicationForm()
    ctx = q.usajili(year=_active_year(request),
                    region_ids=scope_regions(request.user))
    ctx["form"] = form
    ctx.update(_chrome(request, nav=navs.usajili("usajili"),
                       topbar_title="MUWESTA Membership Management System",
                       topbar_sub="Dashboard > Usajili wa Mwanachama"))
    return render(request, "admin_panel/usajili.html", ctx)


@role_required(*MONEY_ROLES)
def malipo(request):
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.recorded_by = request.user
            payment.save()
            payment.post_to_ledger()
            AuditLog.record(request, "payment_recorded", payment)
            messages.success(request, _("Malipo yamerekodiwa. Risiti: %(no)s") % {
                "no": payment.receipt_no})
            return redirect("core:malipo")
        messages.error(request, _("Tafadhali sahihisha makosa hapa chini."))
    else:
        form = PaymentForm()
    f = {k: (request.GET.get(k) or "") for k in ("q", "status", "method", "from", "to")}
    ctx = q.malipo(page=_page(request), filters=f, year=_active_year(request),
                   region_ids=scope_regions(request.user))
    ctx["filters"] = f
    ctx["form"] = form
    ctx.update(_chrome(request, nav=navs.malipo("malipo-muhtasari"),
                       topbar_title="MUWESTA Membership Management System",
                       topbar_sub="Dashboard / Malipo ya Ada"))
    return render(request, "admin_panel/malipo.html", ctx)


@role_required(*MONEY_ROLES)
def michango(request):
    if request.method == "POST":
        form = ContributionForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.recorded_by = request.user
            c.save()
            c.post_to_ledger()
            AuditLog.record(request, "contribution_recorded", c)
            messages.success(request, _("Mchango umerekodiwa. Risiti: %(no)s") % {
                "no": c.receipt_no})
            return redirect("core:michango")
        messages.error(request, _("Tafadhali sahihisha makosa hapa chini."))
    else:
        form = ContributionForm()
    f = {k: (request.GET.get(k) or "") for k in ("q", "fund", "status", "from", "to")}
    ctx = q.michango(page=_page(request), filters=f, year=_active_year(request),
                     region_ids=scope_regions(request.user))
    ctx["filters"] = f
    ctx["form"] = form
    ctx.update(_chrome(request, nav=navs.michango("michango-muhtasari"),
                       topbar_title="MUWESTA Membership Management System",
                       topbar_sub="Dashboard / Michango"))
    return render(request, "admin_panel/michango.html", ctx)


@role_required(*OUTREACH_ROLES)
def wadau(request):
    ctx = q.wadau(year=_active_year(request))
    ctx["can_see_contributions"] = request.user.role in [
        r.value for r in MONEY_ROLES]
    ctx.update(_chrome(request, nav=navs.outreach("dashboard"), verse=q.verse(1),
                       show_search=True, search_placeholder="Tafuta...",
                       map_regions=tz_map(ctx["regions"]),
                       map_legend=tz_legend(ctx["regions"])))
    return render(request, "admin_panel/wadau.html", ctx)


@role_required(*OUTREACH_ROLES)
def matukio(request):
    allowed = scope_regions(request.user)
    ctx = q.matukio(month_key=request.GET.get("month"), year=_active_year(request),
                    region_ids=allowed)
    nav = navs.coordinator("matukio") if allowed is not None else navs.outreach("matukio")
    ctx.update(_chrome(request, nav=nav))
    return render(request, "admin_panel/matukio.html", ctx)


@role_required(*OUTREACH_ROLES)
def media(request):
    ctx = q.media(year=_active_year(request))
    nav = (navs.coordinator("media") if user_zone(request.user)
           else navs.outreach("media"))
    ctx.update(_chrome(request, nav=nav))
    return render(request, "admin_panel/media.html", ctx)


@staff_required
def dashboard(request):
    ctx = _gate_actions(q.superadmin(year=_active_year(request)), request.user)
    ctx.update(_chrome(request, nav=navs.superadmin("dashboard"),
                       show_search=True, search_placeholder="Tafuta hapa..."))
    return render(request, "admin_panel/dashboard.html", ctx)


#: Mratibu wa kanda anaona maombi ya kanda yake, KAMA `/uongozi/maombi/`
#: inavyofanya: kuona tu. Kuhakiki na kuhariri (`maombi_action`,
#: `application_edit`) yanabaki kwa usajili. Bila hii, menyu yake
#: ilimwelekeza kwenye ukurasa aliokataliwa.
@role_required(*(REG_ROLES + [Role.COORDINATOR]))
def maombi(request):
    qs = Application.objects.select_related("category", "region", "district")
    # Mratibu anaona maombi ya kanda yake pekee
    allowed = scope_regions(request.user)
    if allowed is not None:
        qs = qs.filter(region_id__in=allowed)
    f = {k: (request.GET.get(k) or "") for k in
         ("q", "status", "category", "region", "from", "to")}
    if f["q"]:
        qs = qs.filter(Q(full_name__icontains=f["q"]) | Q(phone__icontains=f["q"]) |
                       Q(email__icontains=f["q"]) | Q(reference__icontains=f["q"]))
    if f["status"]:
        qs = qs.filter(status=f["status"])
    if f["category"]:
        qs = qs.filter(category_id=f["category"])
    if f["region"]:
        qs = qs.filter(region_id=f["region"])
    if f["from"]:
        qs = qs.filter(created_at__date__gte=f["from"])
    if f["to"]:
        qs = qs.filter(created_at__date__lte=f["to"])

    from django.conf import settings as _s

    rows = [{
        "id": a.pk, "ref": a.reference, "name": a.full_name, "category": a.category.name,
        "region": a.region.name if a.region else "—",
        "district": a.district.name if a.district else "—",
        "place": f"{a.region.name if a.region else '—'} / {a.district.name if a.district else '—'}",
        "date": a.created_at.strftime("%d/%m/%Y"), "phone": a.phone, "email": a.email,
        "status": a.get_status_display(), "badge": a.badge,
        "initials": q._initials(a.full_name),
        "pending": a.status in ("pending", "review"),
        #: Ombi lililohakikiwa linasubiri malipo. Afisa anahitaji kiungo
        #: cha kumpa mwombaji, na kiasi anachotakiwa kulipa.
        "awaiting": a.status == ApplicationStatus.AWAITING_PAYMENT,
        "pay_url": f"{_s.SITE_URL}{reverse('core:lipa')}?ombi={a.reference}&k={a.pay_token}",
        "due": a.amount_due() if a.status == ApplicationStatus.AWAITING_PAYMENT else 0,
        "phone_verified": a.phone_verified,
    } for a in qs[:50]]

    # Ombi linalochaguliwa kwa `?ombi=<id>`. Awali `detail` ilikuwa
    # `rows[0]` daima — maandishi yalisema "chagua ombi" lakini hakukuwa
    # na cha kubofya.
    picked = request.GET.get("ombi", "")
    detail = next((r for r in rows if str(r["id"]) == picked), None)

    ctx = {
        "rows": rows, "filters": f, "total": qs.count(),
        "statuses": ApplicationStatus.choices,
        "categories": refdata.categories(),
        "regions_list": refdata.regions(),
        "detail": detail or (rows[0] if rows else None),
        "picked": picked,
        #: KPI hizi zilikuwa za nchi nzima juu ya ukurasa
        #: uliochujwa kwa kanda — namba zilizo juu ya jedwali
        #: hazikulingana na safu zilizo chini yake.
        "kpis": q.usajili(region_ids=scope_regions(request.user))["kpis"],
        #: Mratibu anaona maombi lakini hahakiki. Bila bendera hii
        #: angeona vitufe "Hakiki", "Kataa" na "Hariri" ambavyo
        #: vinamkatalia akibofya.
        "can_review": request.user.role in [r.value for r in REG_ROLES],
    }
    ctx.update(_chrome(request, nav=navs.usajili("maombi"),
                       topbar_title="MUWESTA Membership Management System",
                       topbar_sub="Maombi ya Uanachama"))
    return render(request, "admin_panel/maombi.html", ctx)


@role_required(*REG_ROLES)
@require_POST
def maombi_action(request, pk, action):
    """
    Kuhakiki au kukataa ombi la uanachama.

    Ilikuwa `@staff_required` pekee, yaani KILA jukumu la afisa. Afisa wa
    michango, wa wadau na wa ustawi wote wangeweza kuhakiki ombi —
    hatua inayoruhusu mtu kulipa na kuwa mwanachama kamili. Usajili ni
    kazi ya afisa wa usajili.
    """
    app = get_object_or_404(Application, pk=pk)
    #: Orodha ya maombi ilikuwa ikichuja kwa mkoa, lakini kitendo cha
    #: kuidhinisha hakikuchuja. Mratibu wa kanda moja angeweza
    #: kuidhinisha ombi la kanda nyingine kwa POST moja, SMS ya malipo
    #: ikatoka, na `reviewed_by` ikaandika afisa wa kanda isiyohusika.
    regions = scope_regions(request.user)
    if regions is not None and app.region_id not in regions:
        raise Http404
    if app.status in (ApplicationStatus.APPROVED, ApplicationStatus.REJECTED,
                      ApplicationStatus.AWAITING_PAYMENT):
        messages.info(request, _("Ombi %(ref)s tayari limeshughulikiwa.") % {
            "ref": app.reference})
        return redirect("core:maombi")
    if action == "approve":
        from django.conf import settings

        app.approve(request.user)
        AuditLog.record(request, "application_approved", app)
        pay_url = (f"{settings.SITE_URL}{reverse('core:lipa')}"
                   f"?ombi={app.reference}&k={app.pay_token}")
        messages.success(request, _(
            "Ombi %(ref)s limehakikiwa. Sasa linasubiri malipo ya ada."
        ) % {"ref": app.reference})
        # Namba ya uanachama, kadi na nenosiri hutolewa malipo
        # yakithibitishwa — si hapa.
        # Mwombaji naye ajulishwe. Awali afisa pekee ndiye aliyekuwa
        # anapata kiungo — mwombaji alibaki akisubiri simu ambayo huenda
        # isipigwe.
        from . import sms

        due = app.amount_due()
        told = sms.send_application_approved(app.phone, app.reference, due, pay_url)

        messages.info(request, _(
            "Mpe mwombaji kiungo hiki cha kulipia: %(url)s — kiasi "
            "kinachotakiwa ni TZS %(amount)s. Atapata namba ya uanachama, "
            "kadi na nenosiri la kuingia mara malipo yatakapothibitishwa."
        ) % {"url": pay_url, "amount": f"{due:,}"})
        if told:
            messages.info(request, _(
                "Tumemtumia mwombaji SMS yenye kiungo hicho."))
        else:
            messages.warning(request, _(
                "SMS haikumfikia mwombaji. Mpigie simu."))
    elif action == "reject":
        from . import sms

        app.status = ApplicationStatus.REJECTED
        app.reviewed_by = request.user
        app.reviewed_at = timezone.now()
        # Mwombaji ajulishwe. Kumwacha akisubiri milele ni mbaya kuliko
        # kumwambia hakukubaliwa.
        sms.send_application_rejected(app.phone, app.reference)
        app.save(update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"])
        AuditLog.record(request, "application_rejected", app)
        messages.info(request, _("Ombi limekataliwa."))
    else:
        raise Http404
    return redirect("core:maombi")


@staff_required
def wanachama(request):
    # Mratibu akifungua URL hii moja kwa moja, bado anaona kanda yake tu
    allowed = scope_regions(request.user)
    zone = user_zone(request.user)
    nav = navs.coordinator("wanachama") if zone else navs.superadmin("wanachama")
    return _member_list(request, region_ids=allowed, nav=nav, zone=zone)


def _member_list(request, region_ids=None, nav=None, zone=None):
    """Orodha ya wanachama. `region_ids` ikitolewa, inabana kwa mikoa hiyo."""
    from geo.scope import scope_members

    #: Ufinyu halisi unatoka `geo.scope` — ndiyo inayojua ngazi zote
    #: tano. `region_ids` ni kwa kichujio cha mikoa kwenye fomu pekee:
    #: kwa mwenyekiti wa KATA, mkoa ni mkubwa sana. Bila mstari huu
    #: angeona wanachama wote wa mkoa wake badala ya kata yake.
    qs = scope_members(request.user,
                       Member.objects.select_related("category", "region", "district"))
    if region_ids is not None:
        qs = qs.filter(region_id__in=region_ids)
    f = {k: (request.GET.get(k) or "") for k in ("q", "status", "category", "region")}
    if f["q"]:
        qs = qs.filter(Q(full_name__icontains=f["q"]) | Q(membership_no__icontains=f["q"]) |
                       Q(account_no__icontains=f["q"]) | Q(phone__icontains=f["q"]))
    if f["status"]:
        qs = qs.filter(status=f["status"])
    if f["category"]:
        qs = qs.filter(category_id=f["category"])
    if f["region"]:
        qs = qs.filter(region_id=f["region"])

    ctx = {
        "rows": [{
            "id": m.pk, "no": m.membership_no, "account": m.account_no, "name": m.full_name,
            "initials": m.initials, "category": m.category.name, "phone": m.phone,
            "place": m.region.name if m.region else "—",
            "joined": m.joined_on.strftime("%d %b %Y"), "status": m.get_status_display(),
            "badge": {"active": "ok", "suspended": "warn",
                      "expired": "danger"}.get(m.status, "muted"),
        } for m in qs[:50]],
        "total": qs.count(), "filters": f,
        "statuses": MemberStatus.choices,
        "categories": refdata.categories(),
        "regions_list": (Region.objects.filter(pk__in=region_ids)
                         if region_ids is not None else refdata.regions()),
        "zone": zone,
        #: Kitufe cha "Sajili Mwanachama" ni cha usajili pekee.
        "can_register": request.user.role in [r.value for r in REG_ROLES],
    }
    ctx.update(_chrome(request, nav=nav or navs.superadmin("wanachama"),
                       topbar_title=zone.tx("name") if zone else "MUWESTA Membership Management System",
                       topbar_sub=str(_("Orodha ya Wanachama"))))
    return render(request, "admin_panel/wanachama.html", ctx)


# ===========================================================================
#  MWANACHAMA
# ===========================================================================
@login_required
def member_dashboard(request):
    member = getattr(request.user, "member", None)
    if member is None:
        messages.warning(request, _("Akaunti yako haijaunganishwa na mwanachama yeyote."))
        return redirect("core:home")
    ctx = q.member_dashboard(member)
    ctx.update(_chrome(request, nav=navs.member("dashboard"), verse=q.verse(1),
                       user_role=ctx["member"]["category_label"],
                       user_initials=member.initials))
    return render(request, "member/dashboard.html", ctx)


@login_required
def member_profile(request):
    member = getattr(request.user, "member", None)
    if member is None:
        # Watumishi hawana wasifu wa mwanachama — waelekeze badala ya 404
        messages.info(request, _("Akaunti yako si ya mwanachama, kwa hiyo "
                                 "huna wasifu wa uanachama."))
        return redirect("core:home")
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            AuditLog.record(request, "profile_updated", member)
            messages.success(request, _("Wasifu wako umesasishwa."))
            return redirect("core:member_profile")
    else:
        form = ProfileForm(instance=member)
    ctx = {"form": form, "member": member}
    ctx.update(_chrome(request, nav=navs.member("wasifu"), verse=q.verse(1),
                       topbar_title="Wasifu Wangu"))
    return render(request, "member/profile.html", ctx)


# ===========================================================================
#  ENEO LA MWANACHAMA — huduma binafsi
# ===========================================================================
def _member_or_redirect(request):
    """Rudisha mwanachama, au None kama mtumiaji si mwanachama."""
    member = getattr(request.user, "member", None)
    if member is None:
        messages.info(request, _("Akaunti yako si ya mwanachama."))
    return member


def _member_ctx(request, member, active, title, **kw):
    ctx = {"member_obj": member}
    ctx.update(_chrome(request, nav=navs.member(active), verse=q.verse(1),
                       topbar_title=title, user_role=f"{member.category.name} Member",
                       user_initials=member.initials, **kw))
    return ctx


@login_required
def member_payments(request):
    """Historia ya malipo yangu + kulipa ada."""
    member = _member_or_redirect(request)
    if member is None:
        return redirect("core:home")

    if request.method == "POST":
        form = MemberPaymentForm(request.POST, member=member)
        if form.is_valid():
            payment = form.save(member)
            AuditLog.record(request, "member_payment_submitted", payment)
            messages.success(request, _(
                "Malipo yamewasilishwa. Namba ya risiti: %(no)s. "
                "Yatathibitishwa na afisa wa fedha.") % {"no": payment.receipt_no})
            return redirect("core:member_payments")
        messages.error(request, _("Tafadhali sahihisha makosa hapa chini."))
    else:
        form = MemberPaymentForm(member=member)

    ctx = _member_ctx(request, member, "malipo", str(_("Malipo Yangu")))
    ctx.update(q.member_payments(member))
    ctx["form"] = form
    return render(request, "member/malipo.html", ctx)


@login_required
def member_contributions(request):
    """Michango yangu + kutoa mchango."""
    member = _member_or_redirect(request)
    if member is None:
        return redirect("core:home")

    if request.method == "POST":
        form = MemberContributionForm(request.POST)
        if form.is_valid():
            c = form.save(member)
            AuditLog.record(request, "member_contribution_submitted", c)
            messages.success(request, _(
                "Asante kwa mchango wako. Namba ya risiti: %(no)s.") % {"no": c.receipt_no})
            return redirect("core:member_contributions")
        messages.error(request, _("Tafadhali sahihisha makosa hapa chini."))
    else:
        form = MemberContributionForm()

    ctx = _member_ctx(request, member, "michango", str(_("Michango Yangu")))
    ctx.update(q.member_contributions(member))
    ctx["form"] = form
    return render(request, "member/michango.html", ctx)


@login_required
def member_points(request):
    """Pointi zangu na tuzo."""
    member = _member_or_redirect(request)
    if member is None:
        return redirect("core:home")
    ctx = _member_ctx(request, member, "pointi", str(_("Pointi na Faida")))
    ctx.update(q.member_points(member))
    return render(request, "member/pointi.html", ctx)


@login_required
def member_assistance(request):
    """Maombi yangu ya msaada."""
    member = _member_or_redirect(request)
    if member is None:
        return redirect("core:home")

    if request.method == "POST":
        form = AssistanceForm(request.POST)
        if form.is_valid():
            req = AssistanceRequest.objects.create(
                member=member,
                assistance_type=form.cleaned_data["assistance_type"],
                amount_requested=form.cleaned_data["amount_requested"],
                description=form.cleaned_data["description"])
            AuditLog.record(request, "assistance_requested", req)
            from . import sms

            sms.send_assistance_received(member.phone, req.reference)
            messages.success(request, _(
                "Ombi lako la msaada limepokelewa. Kumbukumbu: %(ref)s") % {
                    "ref": req.reference})
            return redirect("core:member_assistance")
        messages.error(request, _("Tafadhali sahihisha makosa hapa chini."))
    else:
        form = AssistanceForm()

    ctx = _member_ctx(request, member, "msaada", str(_("Msaada na Maombi")))
    ctx.update(q.member_assistance(member))
    ctx["form"] = form
    return render(request, "member/msaada.html", ctx)


@login_required
def member_family(request):
    """Familia na wanufaika."""
    member = _member_or_redirect(request)
    if member is None:
        return redirect("core:home")

    family_form = FamilyMemberForm()
    beneficiary_form = BeneficiaryForm()

    if request.method == "POST":
        kind = request.POST.get("kind")
        if kind == "family":
            family_form = FamilyMemberForm(request.POST)
            if family_form.is_valid():
                obj = family_form.save(commit=False)
                obj.member = member
                obj.save()
                messages.success(request, _("Mwanafamilia ameongezwa."))
                return redirect("core:member_family")
        elif kind == "beneficiary":
            beneficiary_form = BeneficiaryForm(request.POST)
            if beneficiary_form.is_valid():
                obj = beneficiary_form.save(commit=False)
                obj.member = member
                obj.save()
                messages.success(request, _("Mnufaika ameongezwa."))
                return redirect("core:member_family")
        elif kind == "delete_family":
            member.family.filter(pk=request.POST.get("pk")).delete()
            messages.info(request, _("Mwanafamilia ameondolewa."))
            return redirect("core:member_family")
        elif kind == "delete_beneficiary":
            member.beneficiaries.filter(pk=request.POST.get("pk")).delete()
            messages.info(request, _("Mnufaika ameondolewa."))
            return redirect("core:member_family")
        messages.error(request, _("Tafadhali sahihisha makosa hapa chini."))

    ctx = _member_ctx(request, member, "familia", str(_("Familia na Wanufaika")))
    ctx["family"] = member.family.all()
    ctx["beneficiaries"] = member.beneficiaries.all()
    ctx["family_form"] = family_form
    ctx["beneficiary_form"] = beneficiary_form
    return render(request, "member/familia.html", ctx)


@login_required
def member_card(request):
    """Kadi yangu ya uanachama."""
    member = _member_or_redirect(request)
    if member is None:
        return redirect("core:home")
    ctx = _member_ctx(request, member, "kadi", str(_("Kadi Yangu")))
    ctx.update(q.member_dashboard(member))
    ctx["cards"] = member.cards.all()
    return render(request, "member/kadi.html", ctx)


@login_required
def member_events(request):
    """Matukio niliyojiandikisha."""
    member = _member_or_redirect(request)
    if member is None:
        return redirect("core:home")
    ctx = _member_ctx(request, member, "matukio", str(_("Matukio Yangu")))
    ctx.update(q.member_events(member))
    return render(request, "member/matukio.html", ctx)


@login_required
def member_notices(request):
    """Taarifa na matangazo."""
    member = _member_or_redirect(request)
    if member is None:
        return redirect("core:home")
    Notification.objects.filter(member=member, is_read=False).update(is_read=True)
    ctx = _member_ctx(request, member, "taarifa", str(_("Taarifa na Matangazo")))
    ctx.update(q.member_notices(member))
    return render(request, "member/taarifa.html", ctx)


# ===========================================================================
#  AFISA — vitendo kwenye malipo na michango
# ===========================================================================
@role_required(*MONEY_ROLES)
@require_POST
def payment_action(request, pk, action):
    """Thibitisha au ghairi malipo yanayosubiri."""
    from finance.models import reverse_posting

    payment = get_object_or_404(Payment.objects.select_related("member"), pk=pk)
    if not _in_scope(request.user, payment.member):
        raise Http404
    if action == "confirm":
        if payment.status == PaymentStatus.CONFIRMED:
            messages.info(request, _("Malipo haya tayari yamethibitishwa."))
        else:
            payment.status = PaymentStatus.CONFIRMED
            payment.save(update_fields=["status", "updated_at"])
            payment.post_to_ledger()          # signal pia inalinda
            AuditLog.record(request, "payment_confirmed", payment)
            messages.success(request, _("Malipo %(no)s yamethibitishwa.") % {
                "no": payment.receipt_no})
    elif action == "cancel":
        if payment.status == PaymentStatus.CANCELLED:
            messages.info(request, _("Malipo haya tayari yameghairiwa."))
        else:
            #: Kughairi kulikuwa kunabadilisha `status` pekee, huku leja
            #: na pointi zikibaki. Sasa vinarudishwa kwa ingizo la
            #: kinyume — leja haifutwi, inarekebishwa.
            was_confirmed = payment.status == PaymentStatus.CONFIRMED
            payment.status = PaymentStatus.CANCELLED
            payment.save(update_fields=["status", "updated_at"])
            if was_confirmed:
                reverse_posting(payment, str(_("Malipo yameghairiwa")))
            AuditLog.record(request, "payment_cancelled", payment)
            messages.info(request, _("Malipo %(no)s yameghairiwa.") % {
                "no": payment.receipt_no})
    else:
        raise Http404
    return redirect(_back(request, reverse("core:malipo")))


@role_required(*MONEY_ROLES)
@require_POST
def contribution_action(request, pk, action):
    """Thibitisha au ghairi mchango."""
    from finance.models import reverse_posting

    c = get_object_or_404(Contribution.objects.select_related("member"), pk=pk)
    if c.member_id and not _in_scope(request.user, c.member):
        raise Http404
    if action == "confirm":
        if c.status == PaymentStatus.CONFIRMED:
            messages.info(request, _("Mchango huu tayari umethibitishwa."))
        else:
            c.status = PaymentStatus.CONFIRMED
            c.save(update_fields=["status", "updated_at"])
            c.post_to_ledger()
            AuditLog.record(request, "contribution_confirmed", c)
            messages.success(request, _("Mchango %(no)s umethibitishwa.") % {
                "no": c.receipt_no})
    elif action == "cancel":
        if c.status == PaymentStatus.CANCELLED:
            messages.info(request, _("Mchango huu tayari umeghairiwa."))
        else:
            was_confirmed = c.status == PaymentStatus.CONFIRMED
            c.status = PaymentStatus.CANCELLED
            c.save(update_fields=["status", "updated_at"])
            if was_confirmed:
                reverse_posting(c, str(_("Mchango umeghairiwa")))
            AuditLog.record(request, "contribution_cancelled", c)
            messages.info(request, _("Mchango %(no)s umeghairiwa.") % {"no": c.receipt_no})
    else:
        raise Http404
    return redirect(_back(request, reverse("core:michango")))


@staff_required
def receipt(request, kind, pk):
    """Risiti inayoweza kuchapishwa (Ctrl+P) kwa malipo au mchango."""
    if kind == "malipo":
        obj = get_object_or_404(Payment.objects.select_related("member"), pk=pk)
        if not _in_scope(request.user, obj.member):
            raise Http404
        ctx = {
            "no": obj.receipt_no, "kind": _("Ada ya Uanachama"),
            "name": obj.member.full_name, "membership_no": obj.member.membership_no,
            "amount": q.tzs(obj.amount), "method": obj.method_label,
            "date": obj.paid_at, "status": obj.get_status_display(),
            "badge": obj.badge, "reference": obj.reference,
            "detail": f"{q.MONTHS[obj.period_month - 1]} {obj.year}" if obj.period_month else str(obj.year),
        }
    elif kind == "mchango":
        obj = get_object_or_404(Contribution.objects.select_related("fund", "member"), pk=pk)
        if obj.member_id and not _in_scope(request.user, obj.member):
            raise Http404
        ctx = {
            "no": obj.receipt_no, "kind": obj.fund.tx("name"),
            "name": obj.display_name,
            "membership_no": obj.member.membership_no if obj.member else "—",
            "amount": q.tzs(obj.amount), "method": obj.get_method_display(),
            "date": obj.received_at, "status": obj.get_status_display(),
            "badge": obj.badge, "reference": obj.reference,
            "detail": obj.project.tx("title") if obj.project else (obj.note or "—"),
        }
    else:
        raise Http404
    ctx["settings_obj"] = SiteSetting.get()
    return render(request, "admin_panel/risiti.html", ctx)


@staff_required
def member_detail(request, pk):
    """Maelezo kamili ya mwanachama mmoja."""
    member = get_object_or_404(
        Member.objects.select_related("category", "region", "district", "ward"), pk=pk)
    allowed = scope_regions(request.user)
    if allowed is not None and member.region_id not in allowed:
        messages.warning(request, _("Mwanachama huyu si wa kanda yako."))
        return redirect("core:zone_members")
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "suspend":
            member.status = MemberStatus.SUSPENDED
        elif action == "activate":
            member.status = MemberStatus.ACTIVE
        elif action == "issue_card":
            from . import sms

            #: Kadi ni kitambulisho rasmi. Kuitoa ni kazi ya usajili, si
            #: ya afisa wa michango au wa wadau.
            if request.user.role not in REG_ROLES:
                messages.warning(request, _("Huna ruhusa ya kutoa kadi."))
                return redirect("core:member_detail", pk=pk)
            card = Card.issue(member, expires_on=member.expires_on)
            AuditLog.record(request, "card_issued", member)
            sms.send_card_issued(member.phone, card.serial, card.expires_on)
            messages.success(request, _("Kadi mpya imetolewa."))
            return redirect("core:member_detail", pk=pk)
        elif action == "grant_special":
            if request.user.role not in (Role.SUPER_ADMIN, Role.ADMIN):
                messages.warning(request, _("Msimamizi pekee ndiye anayeweza "
                                            "kutoa daraja la heshima."))
                return redirect("core:member_detail", pk=pk)
            special = Category.objects.filter(is_special=True).first()
            if special is None:
                messages.warning(request, _("Hakuna daraja maalum lililowekwa."))
            elif member.category_id == special.pk:
                messages.info(request, _("Mwanachama tayari yupo daraja la %(t)s.") % {
                    "t": special.name})
            else:
                member.category = special
                member.save(update_fields=["category", "updated_at"])
                Card.issue(member)          # kadi mpya yenye daraja jipya
                AuditLog.record(request, "special_tier_granted", member,
                                detail=special.name)
                Notification.objects.create(
                    member=member, user=member.user,
                    title=str(_("Umepandishwa daraja la %(t)s") % {"t": special.name}),
                    body=str(_("Uongozi wa MUWESTA umekutunuku daraja la heshima. "
                               "Kadi yako mpya iko tayari.")),
                    icon="star", tint="gold", url="/mwanachama/kadi/")
                messages.success(request, _(
                    "%(name)s amepandishwa daraja la %(t)s na kadi mpya imetolewa."
                ) % {"name": member.full_name, "t": special.name})
            return redirect("core:member_detail", pk=pk)
        elif action == "reset_login":
            #: `grant_special` hapo juu ilikuwa imezuiwa kwa msimamizi,
            #: lakini hii haikuwa imezuiwa kabisa. Afisa yeyote — hata
            #: wa wadau — angeweza kurejesha nenosiri la mwanachama
            #: yeyote, kusoma nenosiri la muda kwenye ujumbe ule ule,
            #: na kuingia kama mtu huyo. Pia ilikuwa inamfufua
            #: mwanachama aliyesimamishwa kimya kimya (`is_active=True`).
            if request.user.role not in ACCOUNT_ROLES:
                messages.warning(request, _("Msimamizi pekee ndiye anayeweza "
                                            "kurejesha taarifa za kuingia."))
                return redirect("core:member_detail", pk=pk)
            # Hutengeneza akaunti kama haipo, au huweka nenosiri jipya la muda
            import secrets
            alphabet = "abcdefghjkmnpqrstuvwxyz23456789"
            pw = "".join(secrets.choice(alphabet) for _ in range(10))
            if member.user is None:
                member.create_login(pw)
                AuditLog.record(request, "member_login_created", member)
            else:
                member.user.set_password(pw)
                #: `is_active` haiguswi. Kurejesha nenosiri si sababu ya
                #: kufufua akaunti iliyozimwa kwa makusudi.
                member.user.save(update_fields=["password"])
                AuditLog.record(request, "member_password_reset", member)
                from . import sms

                sms.send_password_reset(member.phone, member.user.username)
            messages.success(request, _(
                "Taarifa mpya za kuingia: jina la mtumiaji %(user)s, "
                "nenosiri la muda %(pw)s"
            ) % {"user": member.user.username, "pw": pw})
            return redirect("core:member_detail", pk=pk)
        if action in ("suspend", "activate"):
            if request.user.role not in MEMBER_STATUS_ROLES:
                messages.warning(request, _(
                    "Huna ruhusa ya kubadilisha hali ya uanachama."))
                return redirect("core:member_detail", pk=pk)
            member.save(update_fields=["status", "updated_at"])
            #: Kusitisha LAZIMA kufunge akaunti ya kuingia pia. Awali
            #: `Member.status` ilibadilika peke yake na `user.is_active`
            #: ikabaki `True`; hakuna mahali pengine hali hiyo
            #: ilikuwa ikiangaliwa, kwa hiyo aliyesitishwa aliendelea
            #: kuingia na kutumia mfumo kama kawaida. Uamuzi wa afisa
            #: haukuwa na athari yoyote.
            #:
            #: `is_active=False` inamtoa mara moja: `ModelBackend.get_user`
            #: inarudisha `None`, kwa hiyo hata kipindi kilichofunguliwa
            #: kinakoma kwenye ombi linalofuata — bila kuhitaji ukaguzi
            #: kwenye kila view ya mwanachama.
            if member.user_id:
                member.user.is_active = (action == "activate")
                member.user.save(update_fields=["is_active"])
            AuditLog.record(request, f"member_{action}", member)
            messages.success(request, _("Hali ya mwanachama imebadilishwa."))
        return redirect("core:member_detail", pk=pk)

    special = Category.objects.filter(is_special=True).first()
    ctx = q.member_detail(member)
    ctx["can_grant_special"] = (
        request.user.role in (Role.SUPER_ADMIN, Role.ADMIN)
        and special is not None and member.category_id != special.pk)
    ctx.update(_chrome(request, nav=navs.superadmin("wanachama"),
                       topbar_title=member.full_name,
                       topbar_sub=member.membership_no))
    return render(request, "admin_panel/mwanachama_detail.html", ctx)


@role_required(*WELFARE_ROLES)
def assistance_review(request):
    """Afisa wa ustawi: kupitia maombi ya msaada."""
    qs = AssistanceRequest.objects.select_related("member", "assistance_type")
    f = {k: (request.GET.get(k) or "") for k in ("q", "status", "type")}
    if f["q"]:
        qs = qs.filter(Q(reference__icontains=f["q"]) |
                       Q(member__full_name__icontains=f["q"]))
    if f["status"]:
        qs = qs.filter(status=f["status"])
    if f["type"]:
        qs = qs.filter(assistance_type_id=f["type"])

    if request.method == "POST":
        from . import sms

        req = get_object_or_404(
            AssistanceRequest.objects.select_related("member"),
            pk=request.POST.get("pk"))
        if not _in_scope(request.user, req.member):
            raise Http404
        action = request.POST.get("action")
        if action == "approve":
            #: Kiasi kilikuwa kinachukuliwa moja kwa moja kutoka POST
            #: bila ukaguzi wowote: "abc" ilivunja ukurasa kwa 500,
            #: "-50000" iliingia kama ilivyo, na kiasi kikubwa kuliko
            #: kilichoombwa nacho kiliingia. Sasa lazima kiwe namba,
            #: chanya, na kisizidi kilichoombwa.
            raw = (request.POST.get("amount") or "").replace(",", "").strip()
            approved = req.amount_requested
            if raw:
                try:
                    approved = Decimal(raw)
                except (InvalidOperation, ValueError):
                    messages.error(request, _("Kiasi ulichoweka si namba sahihi."))
                    return redirect("core:assistance_review")
                if approved <= 0:
                    messages.error(request, _("Kiasi lazima kiwe zaidi ya sifuri."))
                    return redirect("core:assistance_review")
                if approved > req.amount_requested:
                    messages.error(request, _(
                        "Huwezi kuidhinisha zaidi ya kilichoombwa (TZS %(k)s)."
                    ) % {"k": f"{req.amount_requested:,.0f}"})
                    return redirect("core:assistance_review")
            req.status = "approved"
            req.amount_approved = approved
            req.approved_by = request.user
            req.approved_at = timezone.now()
            req.save()
            AuditLog.record(request, "assistance_approved", req)
            sms.send_assistance_decision(req.member.phone, req.reference, True)
            messages.success(request, _("Ombi %(ref)s limeidhinishwa.") % {"ref": req.reference})
        elif action == "reject":
            req.status = "rejected"
            req.approved_by = request.user
            req.save(update_fields=["status", "approved_by", "updated_at"])
            AuditLog.record(request, "assistance_rejected", req)
            sms.send_assistance_decision(req.member.phone, req.reference, False)
            messages.info(request, _("Ombi %(ref)s limekataliwa.") % {"ref": req.reference})
        return redirect("core:assistance_review")

    from programs.models import AssistanceType
    ctx = q.assistance_review(qs)
    ctx["filters"] = f
    ctx["types"] = AssistanceType.objects.all()
    ctx.update(_chrome(request, nav=navs.superadmin("ustawi"),
                       topbar_title="MUWESTA Membership Management System",
                       topbar_sub=str(_("Maombi ya Msaada"))))
    return render(request, "admin_panel/ustawi.html", ctx)


# ===========================================================================
#  KUPAKUA RIPOTI (CSV — inafunguka Excel)
# ===========================================================================
#: Nani anaruhusiwa kupakua nini. CSV ni nakala inayotoka nje ya mfumo
#: — haina AuditLog wala ufuatiliaji baada ya kuhifadhiwa kwenye simu ya
#: mtu. Ilikuwa wazi kwa maafisa wote: afisa wa wadau angeweza kupakua
#: daftari lote la wanachama (majina, simu, namba za vitambulisho,
#: anwani), na afisa wa usajili orodha ya wahisani na michango yao.
EXPORT_ROLES = {
    "malipo": MONEY_ROLES,
    "michango": MONEY_ROLES,
    "wahisani": OUTREACH_ROLES,
    "wanachama": REG_ROLES,
    "maombi": REG_ROLES,
    "msaada": WELFARE_ROLES,
}


@staff_required
def export(request, kind):
    """Pakua data kama CSV. Vichujio vya ukurasa vinaheshimiwa."""
    from . import exports

    wanaoruhusiwa = EXPORT_ROLES.get(kind)
    if wanaoruhusiwa is not None and request.user.role not in [
            r.value if hasattr(r, "value") else r for r in wanaoruhusiwa]:
        messages.warning(request, _("Huna ruhusa ya kupakua data hii."))
        return redirect(_back(request, reverse("core:dashboard")))

    allowed = scope_regions(request.user)   # mratibu: kanda yake tu

    if kind == "malipo":
        qs = Payment.objects.all()
        if allowed is not None:
            qs = qs.filter(member__region_id__in=allowed)
        for key, field in [("status", "status"), ("method", "method")]:
            if request.GET.get(key):
                qs = qs.filter(**{field: request.GET[key]})
        if request.GET.get("from"):
            qs = qs.filter(paid_at__date__gte=request.GET["from"])
        if request.GET.get("to"):
            qs = qs.filter(paid_at__date__lte=request.GET["to"])
        if request.GET.get("q"):
            qs = qs.filter(Q(member__full_name__icontains=request.GET["q"]) |
                           Q(receipt_no__icontains=request.GET["q"]))
        result = exports.payments_csv(qs.order_by("-paid_at"))

    elif kind == "michango":
        qs = Contribution.objects.all()
        if allowed is not None:
            qs = qs.filter(member__region_id__in=allowed)
        if request.GET.get("fund"):
            qs = qs.filter(fund_id=request.GET["fund"])
        if request.GET.get("status"):
            qs = qs.filter(status=request.GET["status"])
        if request.GET.get("from"):
            qs = qs.filter(received_at__date__gte=request.GET["from"])
        if request.GET.get("to"):
            qs = qs.filter(received_at__date__lte=request.GET["to"])
        result = exports.contributions_csv(qs.order_by("-received_at"))

    elif kind == "wanachama":
        qs = Member.objects.all()
        if allowed is not None:
            qs = qs.filter(region_id__in=allowed)
        for key in ("status", "category", "region"):
            if request.GET.get(key):
                qs = qs.filter(**{key if key == "status" else f"{key}_id": request.GET[key]})
        result = exports.members_csv(qs.order_by("membership_no"))

    elif kind == "maombi":
        qs = Application.objects.all()
        if allowed is not None:
            qs = qs.filter(region_id__in=allowed)
        if request.GET.get("status"):
            qs = qs.filter(status=request.GET["status"])
        result = exports.applications_csv(qs.order_by("-created_at"))

    elif kind == "wahisani":
        #: Tawi hili lilikuwa halina `allowed` kabisa, tofauti na kila
        #: tawi jingine — mratibu wa kanda moja alipakua majina, simu na
        #: barua pepe za wahisani wote nchini.
        donors = Donor.objects.all()
        if allowed is not None:
            donors = donors.filter(
                contributions__member__region_id__in=allowed).distinct()
        result = exports.donors_csv(donors.order_by("name"))

    elif kind == "matukio":
        events = Event.objects.all()
        if allowed is not None:
            events = events.filter(region_id__in=allowed)
        result = exports.events_csv(events.order_by("-start_at"))

    elif kind == "mikoa":
        result = exports.regions_csv(allowed)

    elif kind == "kanda":
        result = exports.zones_csv()

    else:
        raise Http404

    AuditLog.record(request, "export", detail=kind)
    return result


@role_required(*OUTREACH_ROLES)
def media_upload(request):
    """Kupakia picha au video."""
    if request.method == "POST":
        form = MediaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(user=request.user)
            AuditLog.record(request, "media_uploaded", item)
            messages.success(request, _("Faili \"%(t)s\" limepakiwa.") % {"t": item.title})
            return redirect("core:media")
        messages.error(request, _("Tafadhali sahihisha makosa hapa chini."))
    else:
        form = MediaUploadForm()
    ctx = {"form": form}
    ctx.update(_chrome(request, nav=navs.outreach("media"),
                       topbar_title="MUWESTA Membership Management System",
                       topbar_sub=str(_("Pakia Faili"))))
    return render(request, "admin_panel/media_upload.html", ctx)


# ===========================================================================
#  MRATIBU — kila mratibu anaona kanda yake tu
# ===========================================================================
def user_zone(user):
    """
    Kanda anayosimamia mtumiaji.

    Mratibu ana kanda moja. Msimamizi na maafisa wa taifa hawana kanda,
    kwa hiyo wanaona nchi nzima (`None`).
    """
    if not user.is_authenticated:
        return None

    # Kanda inatoka kwenye `Leadership` KWANZA — ndio mfumo mmoja wa
    # ukweli sasa. `Zone.coordinator` inabaki kama njia ya pili kwa
    # rekodi za zamani zisizohamishwa bado.
    #
    # Awali ilikuwa inaangalia `role == COORDINATOR` pekee, kwa hiyo
    # mratibu asiye na `Zone.coordinator` alionekana kama afisa wa
    # taifa — au, baada ya mfumo mpya, hakuona chochote kabisa.
    from geo.models import LeaderLevel

    post = (user.leaderships.filter(level=LeaderLevel.ZONE,
                                    zone__isnull=False,
                                    ended_on__isnull=True)
            .select_related("zone").first())
    if post:
        return post.zone
    if user.role == Role.COORDINATOR:
        return Zone.objects.filter(coordinator=user).first()
    return None


def scope_regions(user):
    """
    Mikoa anayoruhusiwa kuona. `None` = mikoa yote.

    AWALI ILIKUWA IKIJUA NGAZI MOJA TU — KANDA. Ilikuwa:

        zone = user_zone(user)
        return None if zone is None else [mikoa ya kanda hiyo]

    Kwa hiyo kiongozi WA MKOA, WA WILAYA au WA KATA alipata `None` —
    yaani "mikoa yote". Jukumu lenyewe linaitwa "Mratibu wa MKOA", na
    ngazi hizo tatu zipo kwenye `LeaderLevel`, lakini paneli ya
    watumishi haikuzijua. Mwenyekiti wa kata mmoja aliona orodha ya
    wanachama WOTE wa nchi pamoja na namba zao za simu, akaweza
    kuwapakua kwa CSV, na `_in_scope` ilimruhusu kugusa malipo ya mtu
    wa mkoa wowote.

    Wakati huo huo `geo/scope.py` — ambayo docstring yake inasema wazi
    kwamba mantiki hii haipaswi kuandikwa mahali pengine — ilikuwa
    ikichuja ngazi zote tano kwa usahihi. Paneli mbili za mfumo mmoja
    zilikuwa na majibu mawili tofauti kwa swali moja.

    Sasa inatoka kwenye `geo.scope`: wadhifa wowote, ngazi yoyote.
    Asiye na wadhifa wala jukumu la makao makuu haoni mkoa wowote
    (`[]`), si nchi nzima — upande salama wa kukosea.
    """
    from geo.models import LeaderLevel
    from geo.scope import active_posts, sees_everyone

    if sees_everyone(user):
        return None

    ids = set()
    for p in active_posts(user):
        if p.level == LeaderLevel.ZONE and p.zone_id:
            ids.update(Region.objects.filter(zone_id=p.zone_id)
                       .values_list("pk", flat=True))
        elif p.level == LeaderLevel.REGION and p.region_id:
            ids.add(p.region_id)
        elif p.level == LeaderLevel.DISTRICT and p.district_id:
            if p.district and p.district.region_id:
                ids.add(p.district.region_id)
        elif p.level == LeaderLevel.WARD and p.ward_id:
            reg = getattr(getattr(p.ward, "district", None), "region_id", None)
            if reg:
                ids.add(reg)

    # Njia ya pili kwa rekodi za zamani: mratibu aliyewekwa kwenye
    # `Zone.coordinator` bila wadhifa wa `Leadership`.
    if not ids and user.is_authenticated and user.role == Role.COORDINATOR:
        zone = Zone.objects.filter(coordinator=user).first()
        if zone:
            ids.update(zone.regions.values_list("pk", flat=True))

    return sorted(ids)


def _zone_or_none(request):
    """
    Kanda ya kuonyesha kwenye dashibodi za kanda.

    `?kanda=<code>` NI YA MSIMAMIZI PEKEE. Awali ilikuwa wazi kwa yeyote
    aliyefika hapa: mratibu wa Kanda ya Kaskazini angeandika
    `?kanda=mashariki` na kuona dashibodi nzima ya kanda nyingine —
    wanachama, ada zisizolipwa, michango na ramani. Ufinyu wa kanda
    ulikuwa unategemea mtu asijaribu kubadilisha URL.

    Vivyo hivyo `Zone.objects.first()`: mratibu asiye na kanda
    alionyeshwa kanda ya kwanza kwenye orodha — si yake, ila
    ilifunguka kama yake.
    """
    zone = user_zone(request.user)
    if zone is not None:
        return zone
    if request.user.role not in [r.value for r in ADMINS_PLUS]:
        return None
    code = request.GET.get("kanda")
    return (Zone.objects.filter(code=code).first() if code
            else Zone.objects.first())


@role_required(*ZONE_ROLES)
def coordinator(request):
    """Dashibodi ya mratibu — kanda yake pekee."""
    zone = _zone_or_none(request)
    if zone is None:
        messages.warning(request, _(
            "Hujawekwa kwenye kanda yoyote. Wasiliana na msimamizi ili "
            "uwekwe kwenye kanda yako."))
        return redirect("core:dashboard")

    ctx = q.zone_dashboard(zone, year=_active_year(request))
    ctx["zone"] = zone
    ctx["all_zones"] = refdata.zones() if user_zone(request.user) is None else None
    ctx.update(_chrome(request, nav=navs.coordinator("dashboard"),
                       topbar_title=zone.tx("name"),
                       topbar_sub=str(_("Mratibu wa Kanda")),
                       map_regions=tz_map(ctx["regions"]),
                       map_legend=tz_legend(ctx["regions"])))
    return render(request, "admin_panel/kanda.html", ctx)


@role_required(*ZONE_ROLES)
def zone_members(request):
    """Wanachama wa kanda ya mratibu."""
    zone = user_zone(request.user)
    if zone is None:
        return redirect("core:wanachama")
    return _member_list(request, region_ids=list(zone.regions.values_list("pk", flat=True)),
                        nav=navs.coordinator("wanachama"), zone=zone)


@role_required(*ZONE_ROLES)
def zone_regions(request):
    """Mikoa na halmashauri za kanda."""
    zone = _zone_or_none(request)
    if zone is None:
        messages.warning(request, _("Hujawekwa kwenye kanda yoyote."))
        return redirect("core:dashboard")
    ctx = q.zone_regions(zone)
    ctx["zone"] = zone
    ctx.update(_chrome(request, nav=navs.coordinator("mikoa"),
                       topbar_title=zone.tx("name"),
                       topbar_sub=str(_("Mikoa na Halmashauri"))))
    return render(request, "admin_panel/kanda_mikoa.html", ctx)


# ===========================================================================
#  UJUMBE KWA WANACHAMA
# ===========================================================================
@role_required(*ADMINS_PLUS)
def broadcast(request):
    """
    Kutuma ujumbe kwa wanachama.

    Arifa za ndani zinafika mara moja kwenye dashibodi ya mwanachama.
    Barua pepe zinatumwa kama `EMAIL_HOST` imewekwa (bila hiyo, Django
    inachapisha kwenye console). SMS inahitaji gateway — ujumbe unahifadhiwa
    kwenye foleni tayari kwa kuunganishwa.
    """
    allowed = scope_regions(request.user)

    if request.method == "POST":
        form = BroadcastForm(request.POST, region_ids=allowed)
        if form.is_valid():
            members = list(form.recipients(allowed))
            channels = form.cleaned_data["channel"]
            subject = form.cleaned_data["subject"]
            template = form.cleaned_data["body"]

            def personalise(member):
                return (template
                        .replace("{jina}", member.full_name)
                        .replace("{namba}", member.membership_no))

            sent = {"app": 0, "email": 0, "sms": 0}

            if "app" in channels:
                Notification.objects.bulk_create([
                    Notification(member=m, user=m.user, title=subject,
                                 body=personalise(m), icon="megaphone", tint="navy",
                                 url="/mwanachama/taarifa/")
                    for m in members])
                sent["app"] = len(members)

            if "email" in channels:
                from django.conf import settings as dj_settings
                from django.core.mail import send_mass_mail
                messages_out = [
                    (subject, personalise(m), dj_settings.DEFAULT_FROM_EMAIL, [m.email])
                    for m in members if m.email]
                if messages_out:
                    send_mass_mail(messages_out, fail_silently=True)
                sent["email"] = len(messages_out)

            for channel in channels:
                MessageLog.objects.create(
                    channel=channel, subject=subject, body=template,
                    recipients=len(members) if channel != "email" else sent["email"],
                    status="sent" if channel in ("app", "email") else "queued",
                    sent_by=request.user)
            sent["sms"] = len(members) if "sms" in channels else 0

            AuditLog.record(request, "broadcast", detail=f"{subject} -> {len(members)}")
            messages.success(request, _(
                "Ujumbe umewafikia wanachama %(n)d: arifa %(app)d, barua pepe %(mail)d."
            ) % {"n": len(members), "app": sent["app"], "mail": sent["email"]})
            if "sms" in channels:
                messages.info(request, _(
                    "SMS %(n)d zimehifadhiwa kwenye foleni. Zitatumwa gateway "
                    "itakapounganishwa."
                ) % {"n": sent["sms"]})
            return redirect("core:broadcast")
        messages.error(request, _("Tafadhali sahihisha makosa hapa chini."))
    else:
        form = BroadcastForm(region_ids=allowed)

    zone = user_zone(request.user)
    ctx = q.broadcast_page(allowed)
    ctx["form"] = form
    ctx["zone"] = zone
    nav = navs.coordinator("ujumbe") if zone else navs.superadmin("ujumbe")
    ctx.update(_chrome(request, nav=nav,
                       topbar_title="MUWESTA Membership Management System",
                       topbar_sub=str(_("Ujumbe kwa Wanachama"))))
    return render(request, "admin_panel/ujumbe.html", ctx)


@role_required(*REG_ROLES)
def member_edit(request, pk):
    """Afisa kuhariri taarifa za mwanachama."""
    member = get_object_or_404(Member, pk=pk)
    allowed = scope_regions(request.user)
    if allowed is not None and member.region_id not in allowed:
        messages.warning(request, _("Mwanachama huyu si wa kanda yako."))
        return redirect("core:zone_members")

    can_special = request.user.role in (Role.SUPER_ADMIN, Role.ADMIN)
    if request.method == "POST":
        form = MemberEditForm(request.POST, request.FILES, instance=member,
                              can_assign_special=can_special)
        if form.is_valid():
            form.save()
            AuditLog.record(request, "member_edited", member,
                            detail=", ".join(form.changed_data))
            messages.success(request, _("Taarifa za %(name)s zimesasishwa.") % {
                "name": member.full_name})
            return redirect("core:member_detail", pk=pk)
        messages.error(request, _("Tafadhali sahihisha makosa hapa chini."))
    else:
        form = MemberEditForm(instance=member, can_assign_special=can_special)

    ctx = {"form": form, "m": member, "can_special": can_special}
    ctx.update(_chrome(request, nav=navs.superadmin("wanachama"),
                       topbar_title=member.full_name,
                       topbar_sub=str(_("Hariri Taarifa"))))
    return render(request, "admin_panel/mwanachama_hariri.html", ctx)


@role_required(*REG_ROLES)
def application_edit(request, pk):
    """Afisa kusahihisha ombi kabla ya kuidhinisha."""
    app = get_object_or_404(Application, pk=pk)
    allowed = scope_regions(request.user)
    if allowed is not None and app.region_id not in allowed:
        messages.warning(request, _("Ombi hili si la kanda yako."))
        return redirect("core:maombi")
    if app.status in (ApplicationStatus.APPROVED, ApplicationStatus.REJECTED,
                      ApplicationStatus.AWAITING_PAYMENT):
        messages.info(request, _("Ombi %(ref)s tayari limeshughulikiwa.") % {
            "ref": app.reference})
        return redirect("core:maombi")

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES, instance=app)
        if form.is_valid():
            form.save()
            AuditLog.record(request, "application_edited", app,
                            detail=", ".join(form.changed_data))
            messages.success(request, _("Ombi %(ref)s limesasishwa.") % {"ref": app.reference})
            return redirect("core:maombi")
        messages.error(request, _("Tafadhali sahihisha makosa hapa chini."))
    else:
        form = ApplicationForm(instance=app)

    ctx = {"form": form, "app": app}
    ctx.update(_chrome(request, nav=navs.usajili("maombi"),
                       topbar_title=app.full_name,
                       topbar_sub=app.reference))
    return render(request, "admin_panel/ombi_hariri.html", ctx)


@login_required
def member_card_print(request):
    """
    Kadi inayoweza kuchapishwa au kuhifadhiwa PDF.

    Hakuna library ya PDF inayohitajika — kivinjari chenyewe kina
    "Save as PDF" kwenye dirisha la kuchapisha. `?chapisha=1` inafungua
    dirisha hilo moja kwa moja.
    """
    member = getattr(request.user, "member", None)
    if member is None:
        messages.info(request, _("Akaunti yako si ya mwanachama."))
        return redirect("core:home")
    card = member.cards.filter(is_active=True).first()
    ctx = {
        "m": member, "card": card,
        "settings_obj": SiteSetting.get(),
        "verify_url": card.verify_path if card else "",
    }
    ctx.update(_chrome(request, nav=navs.member("kadi"), verse=q.verse(1),
                       topbar_title=str(_("Kadi Yangu")),
                       user_role=f"{member.category.name} Member",
                       user_initials=member.initials))
    return render(request, "member/kadi_chapisha.html", ctx)


# ===========================================================================
#  USIMAMIZI WA MFUMO — ndani ya dashibodi, si Django admin
# ===========================================================================
def _model_of(entry):
    from django.apps import apps as django_apps
    return django_apps.get_model(entry["model"])


def _admin_form(entry, model):
    """Tengeneza ModelForm kwa vigezo vya usajili."""
    from django import forms as dj_forms
    fields = entry.get("fields")
    if fields is None:
        fields = [f.name for f in model._meta.fields
                  if f.editable and f.name not in ("id", "created_at", "updated_at")]

    Meta = type("Meta", (), {"model": model, "fields": fields})
    body = {"Meta": Meta}

    def __init__(self, *a, **kw):
        dj_forms.ModelForm.__init__(self, *a, **kw)
        for name, field in self.fields.items():
            if isinstance(field.widget, dj_forms.DateInput):
                field.widget.input_type = "date"
            elif isinstance(field.widget, dj_forms.DateTimeInput):
                field.widget.input_type = "datetime-local"
        self._style()

    body["__init__"] = __init__
    return type("AdminForm", (BootstrapMixin, dj_forms.ModelForm), body)


def _cell(obj, field):
    """Thamani ya safu, tayari kwa kuonyeshwa."""
    getter = getattr(obj, f"get_{field}_display", None)
    if callable(getter):
        return getter()
    value = getattr(obj, field, "")
    if callable(value):
        value = value()
    if isinstance(value, bool):
        return value
    return value if value not in (None, "") else "—"


@staff_required
def manage_index(request):
    """Faharasa ya vitu vyote vinavyosimamiwa."""
    ctx = {"groups": registry.groups(request.user)}
    ctx.update(_chrome(request, nav=navs.superadmin("mfumo"),
                       topbar_title="MUWESTA Membership Management System",
                       topbar_sub=str(_("Usimamizi wa Mfumo"))))
    return render(request, "admin_panel/mfumo_faharasa.html", ctx)


def _can_approve(user):
    """Ni Msimamizi pekee anayeweza kuruhusu tangazo lionekane kwa umma."""
    return bool(user and user.is_authenticated
                and (user.is_superuser
                     or user.role in (Role.SUPER_ADMIN, Role.MANAGEMENT)))


@staff_required
def manage_list(request, slug):
    """Orodha ya rekodi za model moja."""
    entry = registry.get_entry(slug)
    if entry is None:
        raise Http404
    if not registry.allowed(entry, request.user):
        messages.warning(request, _("Huna ruhusa ya kusimamia %(x)s.") % {
            "x": entry["label"]})
        return redirect("core:manage_index")
    model = _model_of(entry)

    if entry.get("singleton"):
        obj = model.objects.first() or model.objects.create()
        return redirect("core:manage_edit", slug=slug, pk=obj.pk)

    qs = model.objects.all()
    term = request.GET.get("q") or ""
    if term and entry.get("search"):
        query = Q()
        for f in entry["search"]:
            query |= Q(**{f"{f}__icontains": term})
        qs = qs.filter(query)

    active_filters = {}
    for f in entry.get("filters", []):
        val = request.GET.get(f)
        if val:
            qs = qs.filter(**{f: val})
            active_filters[f] = val

    page = _page(request)
    per_page = 25
    total = qs.count()
    pages = max((total + per_page - 1) // per_page, 1)
    page = min(page, pages)
    rows = qs[(page - 1) * per_page: page * per_page]

    filter_defs = []
    for f in entry.get("filters", []):
        field = model._meta.get_field(f)
        if field.choices:
            choices = list(field.choices)
        elif field.is_relation:
            choices = [(o.pk, str(o)) for o in field.related_model.objects.all()[:200]]
        else:
            choices = [("True", _("Ndiyo")), ("False", _("Hapana"))]
        filter_defs.append({"name": f, "label": field.verbose_name,
                            "choices": choices, "value": active_filters.get(f, "")})

    ctx = {
        "slug": slug, "entry": entry, "readonly": entry.get("readonly", False),
        "headers": [h for _f, h in entry["columns"]],
        "rows": [{"pk": o.pk,
                  "cells": [_cell(o, f) for f, _h in entry["columns"]]} for o in rows],
        "total": total, "page": page, "pages": pages,
        "term": term, "filter_defs": filter_defs,
        **q.page_meta(page, pages, per_page, total),
    }
    ctx.update(_chrome(request, nav=navs.superadmin("mfumo"),
                       topbar_title=entry["label"],
                       topbar_sub=str(_("Usimamizi wa Mfumo"))))
    return render(request, "admin_panel/mfumo_orodha.html", ctx)


@staff_required
def manage_add(request, slug):
    """Kuongeza rekodi mpya."""
    return manage_edit(request, slug, pk=None)


@staff_required
def manage_edit(request, slug, pk=None):
    """Kuongeza au kuhariri rekodi."""
    entry = registry.get_entry(slug)
    if entry is None:
        raise Http404
    if not registry.allowed(entry, request.user):
        messages.warning(request, _("Huna ruhusa ya kusimamia %(x)s.") % {
            "x": entry["label"]})
        return redirect("core:manage_index")
    if entry.get("readonly"):
        messages.info(request, _("Rekodi hizi haziwezi kuhaririwa."))
        return redirect("core:manage_list", slug=slug)

    model = _model_of(entry)
    obj = get_object_or_404(model, pk=pk) if pk else None
    Form = _admin_form(entry, model)

    if request.method == "POST":
        if request.POST.get("action") == "delete" and obj is not None:
            label = str(obj)
            try:
                obj.delete()
            except Exception as exc:
                messages.error(request, _("Haiwezi kufutwa: %(e)s") % {"e": exc})
                return redirect("core:manage_edit", slug=slug, pk=pk)
            AuditLog.record(request, "deleted", detail=f"{entry['label']}: {label}")
            messages.info(request, _("\"%(x)s\" imefutwa.") % {"x": label})
            return redirect("core:manage_list", slug=slug)

        form = Form(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            # Msimamizi pekee ndiye anayeidhinisha tangazo. Afisa au Mratibu
            # akijaribu kuweka "approved" mwenyewe, tunairudisha "pending" —
            # vinginevyo mtu yeyote mwenye akaunti ya ofisi angeweza
            # kuchapisha chochote kwa jina la MUWESTA.
            if slug == "matangazo" and "status" in form.fields:
                wanted = form.cleaned_data.get("status")
                if wanted == "approved" and not _can_approve(request.user):
                    form.instance.status = "pending"
                    messages.info(request, _(
                        "Tangazo limehifadhiwa na linasubiri idhini ya Msimamizi."))
                elif wanted == "approved":
                    form.instance.approved_by = request.user
                    form.instance.approved_at = timezone.now()
                if obj is None:
                    form.instance.created_by = request.user
            saved = form.save()
            #: Fomu ya watumiaji haina uwanja wa nenosiri, kwa hiyo
            #: `ModelForm.save()` ilihifadhi `password=""`. Akaunti
            #: ilionekana imeundwa vizuri, `has_usable_password()`
            #: ikarudisha `True`, lakini `check_password` ilikataa kila
            #: kitu — mtumiaji mpya hakuweza kuingia kamwe, na hakuna
            #: kosa lililoonekana popote. Sasa tunampa nenosiri la muda
            #: na kumwonyesha msimamizi.
            if slug == "watumiaji" and obj is None and not saved.has_usable_password():
                import secrets
                alphabet = "abcdefghjkmnpqrstuvwxyz23456789"
                pw = "".join(secrets.choice(alphabet) for _i in range(10))
                saved.set_password(pw)
                saved.save(update_fields=["password"])
                messages.info(request, _(
                    "Nenosiri la muda la %(user)s ni %(pw)s. Mpe abadilishe "
                    "mara ya kwanza atakapoingia."
                ) % {"user": saved.username, "pw": pw})
            AuditLog.record(request, "created" if obj is None else "updated", saved,
                            detail=entry["label"])
            messages.success(request, _("\"%(x)s\" imehifadhiwa.") % {"x": saved})
            if entry.get("singleton"):
                return redirect("core:manage_edit", slug=slug, pk=saved.pk)
            return redirect("core:manage_list", slug=slug)
        messages.error(request, _("Tafadhali sahihisha makosa hapa chini."))
    else:
        form = Form(instance=obj)

    ctx = {
        "slug": slug, "entry": entry, "form": form, "obj": obj,
        "singleton": entry.get("singleton", False),
    }
    ctx.update(_chrome(request, nav=navs.superadmin("mfumo"),
                       topbar_title=entry["label"],
                       topbar_sub=str(_("Hariri") if obj else _("Ongeza Mpya"))))
    return render(request, "admin_panel/mfumo_fomu.html", ctx)
