"""
Views za MUWESTA MMS.

Data zote zinatoka database kupitia `core.queries`.
"""
import json
import logging

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
from .data import (about as about_data, giving, legal, membership as mem_data,
                   verses as verses_data,
                   navs, pages as pg, tz_map)
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

MAP_LEGEND = [
    {"label": "Zaidi ya 10,000", "color": "#0d5433"},
    {"label": "5,000 - 10,000", "color": "#12864a"},
    {"label": "2,000 - 5,000", "color": "#4cbd83"},
    {"label": "Chini ya 2,000", "color": "#c9e8d5"},
]


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


def _filter_nav(nav, user):
    """
    Ondoa viungo vya `/mfumo/` ambavyo mtumiaji hana ruhusa navyo.

    Bila hii, nav ingeonyesha viungo vinavyoishia 404 kwa majukumu
    yasiyoruhusiwa.
    """
    def ok(item):
        url = item.get("url") or ""
        if not url.startswith("/mfumo/"):
            return True
        slug = url.strip("/").split("/")[1] if url.count("/") > 2 else None
        if slug is None:
            return True
        entry = registry.get_entry(slug)
        return entry is None or registry.allowed(entry, user)

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


def _chrome(request, **kw):
    user = request.user
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
        "msg_count": None,
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
        base["nav"] = _filter_nav(base["nav"], user)
    return base


def _roles():
    return [
        {"label": "Mwanachama", "icon": "user", "url": reverse("core:login") + "?as=member",
         "tint": "green", "desc": "Kadi, malipo, pointi na maombi yako"},
        {"label": "Afisa", "icon": "briefcase", "url": reverse("core:login") + "?as=officer",
         "tint": "navy", "desc": "Usajili, malipo na michango"},
        {"label": "Mratibu", "icon": "map", "url": reverse("core:login") + "?as=coordinator",
         "tint": "purple", "desc": "Wadau, wahisani na kampeni"},
        {"label": "Msimamizi", "icon": "shield", "url": reverse("core:login") + "?as=admin",
         "tint": "red", "desc": "Mfumo mzima na mikoa yote"},
    ]


def _pub(request, key, extra=None):
    ctx = {"site_menu": pg.menu(), "footer_menu": pg.footer_menu(),
           "page_key": key, "roles": _roles()}
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
            return redirect(f"{reverse('core:login')}?next={request.path}")
        if request.user.role not in STAFF_ONLY:
            messages.warning(request, _("Huna ruhusa ya kufikia ukurasa huu."))
            return redirect("core:member_dashboard")
        return view(request, *args, **kwargs)
    wrapper.__name__ = view.__name__
    wrapper.__doc__ = view.__doc__
    return wrapper


# ===========================================================================
#  UTHIBITISHO
# ===========================================================================
#: Majaribio ya juu ya kuingia kwa dakika 15 kutoka IP moja
LOGIN_MAX_ATTEMPTS = 8
LOGIN_LOCKOUT_SECONDS = 15 * 60


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return (forwarded.split(",")[0].strip() if forwarded
            else request.META.get("REMOTE_ADDR", "")) or "?"


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
LOGIN_ROLES = [
    {"key": "donor", "label": "Mhisani", "icon": "hand-heart", "tint": "green",
     "staff": False,
     "hint": "Ingia ili kuona kumbukumbu za michango yako yote."},
    {"key": "volunteer", "label": "Kujitolea", "icon": "users", "tint": "green",
     "staff": False,
     "hint": "Wajitoleaji hutumia akaunti ile ile ya mwanachama."},
    {"key": "member", "label": "Mwanachama", "icon": "user", "tint": "green",
     "staff": False,
     "hint": "Kadi yako, malipo, pointi na maombi yako."},
    {"key": "officer", "label": "Afisa", "icon": "briefcase", "tint": "gold",
     "staff": True,
     "hint": "Usajili, malipo, michango na ustawi."},
    {"key": "coordinator", "label": "Mratibu", "icon": "map", "tint": "navy",
     "staff": True,
     "hint": "Mikoa, wadau na kampeni za kanda yako."},
    {"key": "admin", "label": "Msimamizi", "icon": "shield", "tint": "purple",
     "staff": True,
     "hint": "Mfumo mzima na mikoa yote."},
]

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


def _login_ctx(request, extra=None):
    """
    Muktadha wa ukurasa wa kuingia.

    ONYO: jukumu lililochaguliwa ni MWONGOZO wa maonyesho tu. Jukumu halisi
    linatoka kwenye akaunti yenyewe (`user.role`) — mtu hawezi kupata ruhusa
    za msimamizi kwa kubofya kitufe cha "Msimamizi".
    """
    picked = (request.POST.get("as") or request.GET.get("as") or "member").lower()
    keys = [r["key"] for r in LOGIN_ROLES]
    if picked not in keys:
        picked = "member"
    spec = next(r for r in LOGIN_ROLES if r["key"] == picked)

    def copy(is_staff):
        row = IDENTIFIER_COPY[is_staff]
        return {k: (gettext(v) if k in ("label", "placeholder", "hint") else v)
                for k, v in row.items()}

    ctx = {
        "login_roles": LOGIN_ROLES,
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
    return _pub(request, "", ctx)


def login_view(request):
    if request.user.is_authenticated:
        return redirect(request.user.home_url_name())

    from django.core.cache import cache
    cache_key = f"login-fail:{_client_ip(request)}"

    if request.method == "POST":
        attempts = cache.get(cache_key, 0)
        if attempts >= LOGIN_MAX_ATTEMPTS:
            messages.error(request, _(
                "Umejaribu mara nyingi mno. Subiri dakika 15 kisha ujaribu tena, "
                "au tumia \"Umesahau nenosiri?\"."))
            return render(request, "public/login.html", _login_ctx(request))

        identifier = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        user = _find_user(identifier, password, request) if identifier else None

        if user is not None:
            cache.delete(cache_key)
            auth_login(request, user)
            # "Kumbuka mimi": bila hiyo, kipindi kinaisha kivinjari kikifungwa.
            if not request.POST.get("remember"):
                request.session.set_expiry(0)
            AuditLog.record(request, "login")
            messages.success(request, _("Karibu, %(name)s!") % {
                "name": user.get_full_name() or user.username})
            return redirect(_safe_next(request, reverse(user.home_url_name())))

        cache.set(cache_key, attempts + 1, LOGIN_LOCKOUT_SECONDS)
        AuditLog.record(request, "login_failed", detail=identifier[:60])
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

    return render(request, "public/login.html", _login_ctx(request))


def logout_view(request):
    if request.user.is_authenticated:
        AuditLog.record(request, "logout")
    auth_logout(request)
    messages.info(request, _("Umetoka kwenye mfumo."))
    return redirect("core:home")


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

    phone = (gift.donor.phone if gift.donor else "") or ""
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
            buyer_email=(gift.donor.email if gift.donor else "") or "",
            webhook_url=f"{st.SITE_URL}{reverse('core:selcom_webhook')}",
            currency=gift.currency or "TZS",
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


def _selcom_sync(gift):
    """
    Thibitisha hali halisi ya malipo kwa Selcom.

    Kama ilivyo kwa Pesapal: webhook ni ishara tu. Hali halisi
    inachukuliwa hapa, si kutoka kwenye kile kilichotumwa kwetu.
    """
    from finance.gateways import selcom
    from finance.models import PaymentStatus

    if not gift.gateway_ref:
        return gift
    try:
        body = selcom.order_status(gift.gateway_ref)
    except selcom.SelcomError:
        return gift

    state = selcom.payment_status(body)
    if state == "confirmed" and gift.status != PaymentStatus.CONFIRMED:
        gift.status = PaymentStatus.CONFIRMED
        ref = selcom.transaction_ref(body)
        fields = ["status"]
        if ref and ref != gift.gateway_ref:
            gift.gateway_ref = ref
            fields.append("gateway_ref")
        gift.save(update_fields=fields)
    elif state == "failed" and gift.status == PaymentStatus.PENDING:
        gift.status = PaymentStatus.FAILED
        gift.save(update_fields=["status"])
    return gift


def selcom_subiri(request, receipt):
    """
    Ukurasa wa kusubiri wakati mtu anaingiza PIN kwenye simu yake.

    Unajisasisha kila sekunde chache. Mtu akikamilisha, unampeleka
    kwenye risiti; akighairi, unamwambia na kumpa nafasi ya kujaribu tena.
    """
    from finance.models import Contribution, PaymentStatus

    gift = get_object_or_404(Contribution, receipt_no=receipt)
    if request.session.get("mwst_last_gift") != receipt and not request.user.is_authenticated:
        raise Http404

    _selcom_sync(gift)
    if gift.status != PaymentStatus.PENDING:
        return redirect("core:changia_asante", receipt=gift.receipt_no)

    return render(request, "public/selcom_subiri.html",
                  _pub(request, "changia", {
                      "gift": gift,
                      "phone": (gift.donor.phone if gift.donor else "") or "",
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
    _selcom_sync(gift)
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
            currency=gift.currency or "TZS",
            first_name=names[0] if names else "",
            last_name=names[1] if len(names) > 1 else "",
            email=(gift.donor.email if gift.donor else "") or "",
            phone=(gift.donor.phone if gift.donor else "") or "",
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
    from finance.models import PaymentStatus

    if not gift.gateway_ref:
        return gift
    try:
        body = pesapal.transaction_status(gift.gateway_ref)
    except pesapal.PesapalError:
        return gift

    state = pesapal.map_status(body)
    if state == "confirmed" and gift.status != PaymentStatus.CONFIRMED:
        gift.status = PaymentStatus.CONFIRMED
        gift.save(update_fields=["status"])
    elif state in ("failed", "reversed"):
        gift.status = PaymentStatus.FAILED
        gift.save(update_fields=["status"])
    return gift


def pesapal_callback(request):
    """Mtumiaji anarudishwa hapa baada ya kulipa."""
    from finance.models import Contribution, PaymentStatus

    tracking = request.GET.get("OrderTrackingId", "")
    reference = request.GET.get("OrderMerchantReference", "")
    gift = (Contribution.objects.filter(gateway_ref=tracking).first()
            or Contribution.objects.filter(receipt_no=reference).first())
    if gift is None:
        raise Http404

    _pesapal_sync(gift)
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
    from finance.models import Donor

    lang = get_language()
    catalogue = {
        "purposes": giving.localise(giving.PURPOSES, lang),
        "purpose_groups": giving.localise(giving.PURPOSE_GROUPS, lang),
        "recurrences": giving.localise(giving.RECURRENCES, lang),
        "providers": giving.localise(giving.PROVIDERS, lang),
        "provider_groups": giving.localise(giving.PROVIDER_GROUPS, lang),
        "currencies": giving.CURRENCIES,
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
                method="pesapal" if data["provider"] == "pesapal" else data["provider"][:20],
                note=(data.get("note") or "")[:200],
                status=PaymentStatus.PENDING,
                donor_name=data["full_name"])
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
            app = Application.objects.filter(reference__iexact=ref).first()
            if app and not app.member_id:
                initial.update({"payer_type": "new", "membership_no": app.reference,
                                "full_name": app.full_name, "phone": app.phone,
                                "email": app.email, "package": app.category.code,
                                "include_registration": True})

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
    if request.session.get("mwst_last_gift") != receipt and not request.user.is_authenticated:
        raise Http404

    has_account = bool(gift.donor and gift.donor.user_id)
    # Ada ya uanachama si mchango wa kawaida — mlipaji anakuwa mwanachama,
    # kwa hiyo hafai kualikwa kufungua akaunti ya mhisani. Badala yake
    # anaonyeshwa taarifa zake za uanachama.
    is_fee = gift.purpose == "ada"
    member = gift.member if is_fee else None

    return render(request, "public/changia_asante.html",
                  _pub(request, "changia", {
                      "gift": gift,
                      "is_fee": is_fee,
                      "member": member,
                      "temp_password": getattr(member, "temp_password", None),
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
            Contribution.objects.filter(donor__isnull=True).filter(
                Q(donor_name__iexact=data["full_name"])).update(donor=donor)

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
            app = form.save()
            AuditLog.record(request, "application_submitted", app)
            messages.success(request, _(
                "Ombi lako limepokelewa. Namba ya kumbukumbu ni %(ref)s — "
                "iandike. Afisa wa usajili atahakiki taarifa zako, kisha "
                "utapigiwa simu na kupewa namba yako ya uanachama pamoja na "
                "nenosiri la kuingia kwenye mfumo."
            ) % {"ref": app.reference})
            return redirect("core:jiunge")
        messages.error(request, _("Tafadhali sahihisha makosa hapa chini."))
    else:
        form = ApplicationForm()
    ctx["form"] = form
    return render(request, "public/jiunge.html", _pub(request, "uanachama", ctx))


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
    return redirect(request.META.get("HTTP_REFERER") or reverse("core:matukio_umma"))


def api_districts(request):
    region = request.GET.get("region")
    rows = District.objects.filter(region_id=region).values("id", "name") if region else []
    return JsonResponse({"results": list(rows)})


def api_wards(request):
    district = request.GET.get("district")
    rows = Ward.objects.filter(district_id=district).values("id", "name") if district else []
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
@staff_required
def national(request):
    ctx = q.national(year=_active_year(request))
    nav = (navs.coordinator("taifa") if user_zone(request.user)
           else navs.national("dashboard"))
    ctx.update(_chrome(request, nav=nav,
                       topbar_title="MUWESTA Membership Management System",
                       topbar_sub="Dashboard - Msimamizi Mkuu (Mikoa Yote za Tanzania)",
                       map_regions=tz_map(ctx["regions"]), map_legend=MAP_LEGEND))
    return render(request, "admin_panel/national.html", ctx)


@staff_required
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
    ctx = q.usajili(year=_active_year(request))
    ctx["form"] = form
    ctx.update(_chrome(request, nav=navs.usajili("usajili"),
                       topbar_title="MUWESTA Membership Management System",
                       topbar_sub="Dashboard > Usajili wa Mwanachama"))
    return render(request, "admin_panel/usajili.html", ctx)


@staff_required
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


@staff_required
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


@staff_required
def wadau(request):
    ctx = q.wadau(year=_active_year(request))
    ctx.update(_chrome(request, nav=navs.outreach("dashboard"), verse=q.verse(1),
                       show_search=True, search_placeholder="Tafuta...",
                       map_regions=tz_map(ctx["regions"])))
    return render(request, "admin_panel/wadau.html", ctx)


@staff_required
def matukio(request):
    allowed = scope_regions(request.user)
    ctx = q.matukio(month_key=request.GET.get("month"), year=_active_year(request),
                    region_ids=allowed)
    nav = navs.coordinator("matukio") if allowed is not None else navs.outreach("matukio")
    ctx.update(_chrome(request, nav=nav))
    return render(request, "admin_panel/matukio.html", ctx)


@staff_required
def media(request):
    ctx = q.media(year=_active_year(request))
    nav = (navs.coordinator("media") if user_zone(request.user)
           else navs.outreach("media"))
    ctx.update(_chrome(request, nav=nav))
    return render(request, "admin_panel/media.html", ctx)


@staff_required
def dashboard(request):
    ctx = q.superadmin(year=_active_year(request))
    ctx.update(_chrome(request, nav=navs.superadmin("dashboard"),
                       show_search=True, search_placeholder="Tafuta hapa..."))
    return render(request, "admin_panel/dashboard.html", ctx)


@staff_required
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

    rows = [{
        "id": a.pk, "ref": a.reference, "name": a.full_name, "category": a.category.name,
        "place": f"{a.region.name if a.region else '—'} / {a.district.name if a.district else '—'}",
        "date": a.created_at.strftime("%d/%m/%Y"), "phone": a.phone, "email": a.email,
        "status": a.get_status_display(), "badge": a.badge,
        "initials": q._initials(a.full_name), "pending": a.status in ("pending", "review"),
    } for a in qs[:50]]

    ctx = {
        "rows": rows, "filters": f, "total": qs.count(),
        "statuses": ApplicationStatus.choices,
        "categories": Category.objects.all(),
        "regions_list": Region.objects.all(),
        "detail": rows[0] if rows else None,
        "kpis": q.usajili()["kpis"],
    }
    ctx.update(_chrome(request, nav=navs.usajili("maombi"),
                       topbar_title="MUWESTA Membership Management System",
                       topbar_sub="Maombi ya Uanachama"))
    return render(request, "admin_panel/maombi.html", ctx)


@staff_required
@require_POST
def maombi_action(request, pk, action):
    app = get_object_or_404(Application, pk=pk)
    if app.status in (ApplicationStatus.APPROVED, ApplicationStatus.REJECTED,
                      ApplicationStatus.AWAITING_PAYMENT):
        messages.info(request, _("Ombi %(ref)s tayari limeshughulikiwa.") % {
            "ref": app.reference})
        return redirect("core:maombi")
    if action == "approve":
        from django.conf import settings

        app.approve(request.user)
        AuditLog.record(request, "application_approved", app)
        pay_url = f"{settings.SITE_URL}{reverse('core:lipa')}?ombi={app.reference}"
        messages.success(request, _(
            "Ombi %(ref)s limehakikiwa. Sasa linasubiri malipo ya ada."
        ) % {"ref": app.reference})
        # Namba ya uanachama, kadi na nenosiri hutolewa malipo
        # yakithibitishwa — si hapa.
        messages.info(request, _(
            "Mpe mwombaji kiungo hiki cha kulipia: %(url)s — kiasi "
            "kinachotakiwa ni TZS %(amount)s. Atapata namba ya uanachama, "
            "kadi na nenosiri la kuingia mara malipo yatakapothibitishwa."
        ) % {"url": pay_url, "amount": f"{app.amount_due():,}"})
    elif action == "reject":
        app.status = ApplicationStatus.REJECTED
        app.reviewed_by = request.user
        app.reviewed_at = timezone.now()
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
    qs = Member.objects.select_related("category", "region", "district")
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
        "categories": Category.objects.all(),
        "regions_list": (Region.objects.filter(pk__in=region_ids)
                         if region_ids is not None else Region.objects.all()),
        "zone": zone,
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
@staff_required
@require_POST
def payment_action(request, pk, action):
    """Thibitisha au ghairi malipo yanayosubiri."""
    payment = get_object_or_404(Payment, pk=pk)
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
        payment.status = PaymentStatus.CANCELLED
        payment.save(update_fields=["status", "updated_at"])
        AuditLog.record(request, "payment_cancelled", payment)
        messages.info(request, _("Malipo %(no)s yameghairiwa.") % {"no": payment.receipt_no})
    else:
        raise Http404
    return redirect(request.META.get("HTTP_REFERER") or reverse("core:malipo"))


@staff_required
@require_POST
def contribution_action(request, pk, action):
    """Thibitisha au ghairi mchango."""
    c = get_object_or_404(Contribution, pk=pk)
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
        c.status = PaymentStatus.CANCELLED
        c.save(update_fields=["status", "updated_at"])
        AuditLog.record(request, "contribution_cancelled", c)
        messages.info(request, _("Mchango %(no)s umeghairiwa.") % {"no": c.receipt_no})
    else:
        raise Http404
    return redirect(request.META.get("HTTP_REFERER") or reverse("core:michango"))


@staff_required
def receipt(request, kind, pk):
    """Risiti inayoweza kuchapishwa (Ctrl+P) kwa malipo au mchango."""
    if kind == "malipo":
        obj = get_object_or_404(Payment.objects.select_related("member"), pk=pk)
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
            Card.issue(member)
            AuditLog.record(request, "card_issued", member)
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
            # Hutengeneza akaunti kama haipo, au huweka nenosiri jipya la muda
            import secrets
            alphabet = "abcdefghjkmnpqrstuvwxyz23456789"
            pw = "".join(secrets.choice(alphabet) for _ in range(10))
            if member.user is None:
                member.create_login(pw)
                AuditLog.record(request, "member_login_created", member)
            else:
                member.user.set_password(pw)
                member.user.is_active = True
                member.user.save()
                AuditLog.record(request, "member_password_reset", member)
            messages.success(request, _(
                "Taarifa mpya za kuingia: jina la mtumiaji %(user)s, "
                "nenosiri la muda %(pw)s"
            ) % {"user": member.user.username, "pw": pw})
            return redirect("core:member_detail", pk=pk)
        if action in ("suspend", "activate"):
            member.save(update_fields=["status", "updated_at"])
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


@staff_required
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
        req = get_object_or_404(AssistanceRequest, pk=request.POST.get("pk"))
        action = request.POST.get("action")
        if action == "approve":
            req.status = "approved"
            req.amount_approved = request.POST.get("amount") or req.amount_requested
            req.approved_by = request.user
            req.approved_at = timezone.now()
            req.save()
            AuditLog.record(request, "assistance_approved", req)
            messages.success(request, _("Ombi %(ref)s limeidhinishwa.") % {"ref": req.reference})
        elif action == "reject":
            req.status = "rejected"
            req.approved_by = request.user
            req.save(update_fields=["status", "approved_by", "updated_at"])
            AuditLog.record(request, "assistance_rejected", req)
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
@staff_required
def export(request, kind):
    """Pakua data kama CSV. Vichujio vya ukurasa vinaheshimiwa."""
    from . import exports

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
        result = exports.donors_csv(Donor.objects.all().order_by("name"))

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


@staff_required
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
    if not user.is_authenticated or user.role != Role.COORDINATOR:
        return None
    return Zone.objects.filter(coordinator=user).first()


def scope_regions(user):
    """Mikoa anayoruhusiwa kuona. `None` = mikoa yote."""
    zone = user_zone(user)
    return None if zone is None else list(zone.regions.values_list("pk", flat=True))


@staff_required
def coordinator(request):
    """Dashibodi ya mratibu — kanda yake pekee."""
    zone = user_zone(request.user)
    if zone is None:
        # Msimamizi anaweza kuchagua kanda kwa ?kanda=code
        code = request.GET.get("kanda")
        zone = Zone.objects.filter(code=code).first() if code else Zone.objects.first()
    if zone is None:
        messages.warning(request, _("Hakuna kanda iliyowekwa."))
        return redirect("core:national")

    ctx = q.zone_dashboard(zone, year=_active_year(request))
    ctx["zone"] = zone
    ctx["all_zones"] = Zone.objects.all() if user_zone(request.user) is None else None
    ctx.update(_chrome(request, nav=navs.coordinator("dashboard"),
                       topbar_title=zone.tx("name"),
                       topbar_sub=str(_("Mratibu wa Kanda")),
                       map_regions=tz_map(ctx["regions"]), map_legend=MAP_LEGEND))
    return render(request, "admin_panel/kanda.html", ctx)


@staff_required
def zone_members(request):
    """Wanachama wa kanda ya mratibu."""
    zone = user_zone(request.user)
    if zone is None:
        return redirect("core:wanachama")
    return _member_list(request, region_ids=list(zone.regions.values_list("pk", flat=True)),
                        nav=navs.coordinator("wanachama"), zone=zone)


@staff_required
def zone_regions(request):
    """Mikoa na halmashauri za kanda."""
    zone = user_zone(request.user)
    if zone is None:
        code = request.GET.get("kanda")
        zone = Zone.objects.filter(code=code).first() or Zone.objects.first()
    ctx = q.zone_regions(zone)
    ctx["zone"] = zone
    ctx.update(_chrome(request, nav=navs.coordinator("mikoa"),
                       topbar_title=zone.tx("name"),
                       topbar_sub=str(_("Mikoa na Halmashauri"))))
    return render(request, "admin_panel/kanda_mikoa.html", ctx)


# ===========================================================================
#  UJUMBE KWA WANACHAMA
# ===========================================================================
@staff_required
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


@staff_required
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


@staff_required
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
