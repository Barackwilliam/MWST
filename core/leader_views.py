"""
Sehemu ya uongozi: dashibodi, wanachama, matatizo na mawasiliano.

Kila view inapita `core.leadership`, ambayo nayo inapita `geo.scope`.
Hakuna view inayouliza database moja kwa moja — ndiyo njia pekee ya
kuhakikisha kiongozi wa Kata A hamwoni mwanachama wa Kata B.
"""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from accounts.models import AuditLog
from geo.scope import can_see_member, sees_everyone
from members.models import Member, MemberStatus
from programs.models import (Broadcast, Case, CaseCategory, CaseStatus,
                             CaseUrgency, Message, Thread)

from . import leadership as L
from .data import navs


def leader_required(view):
    """
    Kiongozi pekee.

    Mwanachama wa kawaida hana sehemu hii. Anayeingia bila wadhifa
    anarudishwa kwenye ukurasa wake badala ya kuona ukurasa tupu.
    """
    @wraps(view)
    @login_required
    def inner(request, *args, **kwargs):
        if not L.is_leader(request.user):
            messages.error(request, _("Huna wadhifa wa uongozi kwenye mfumo."))
            return redirect(request.user.home_url_name())
        return view(request, *args, **kwargs)
    return inner


def _chrome(request, active, **kw):
    from .views import _chrome as base_chrome

    # Kiongozi mwenye rekodi ya uanachama anapata sehemu ya "Uanachama
    # Wangu" kwenye menyu. Asiye nayo (mfano afisa wa makao makuu
    # aliyepewa wadhifa) hapati — vinginevyo angebofya na kupata kosa.
    is_member = getattr(request.user, "member", None) is not None
    # Kata ni ngazi ya uwanjani — menyu yake inatofautiana na ya
    # wilaya/mkoa/kanda, ambao wanafanya kazi kupitia viongozi.
    from geo.models import LeaderLevel
    from geo.scope import top_level
    is_field = top_level(request.user) == LeaderLevel.WARD
    kw.update(base_chrome(request, nav=navs.uongozi(active, is_member=is_member,
                                                    is_field=is_field),
                          topbar_title="MUWESTA Membership Management System",
                          topbar_sub=str(_("Uongozi"))))
    return kw


# ---------------------------------------------------------------------------
#  Dashibodi
# ---------------------------------------------------------------------------
@leader_required
def dashibodi(request):
    ctx = L.dashboard(request.user)
    return render(request, "leader/dashibodi.html", _chrome(request, "dashboard", **ctx))


@leader_required
def wanachama(request):
    q = (request.GET.get("q") or "").strip()
    status = request.GET.get("status") or ""

    # Kuchuja kwa eneo dogo, kutoka kwenye mchanganuo wa dashibodi.
    # Majina yanayoruhusiwa yamepangwa — mtu asiweze kuchuja kwa sehemu
    # yoyote ya modeli kwa kubadilisha URL.
    area = None
    for field in ("ward", "district", "region"):
        val = request.GET.get(field)
        if val and val.isdigit():
            area = (field, int(val))
            break

    rows = L.member_rows(request.user, q=q, status=status, area=area)
    return render(request, "leader/wanachama.html", _chrome(
        request, "wanachama", rows=rows, q=q, status=status,
        statuses=MemberStatus.choices, total=len(rows),
        areas=L.areas_label(request.user) if hasattr(L, "areas_label") else ""))


# ---------------------------------------------------------------------------
#  Matatizo
# ---------------------------------------------------------------------------
@leader_required
def matatizo(request):
    cases = L.scope_cases(request.user)
    status = request.GET.get("status") or ""
    if status:
        cases = cases.filter(status=status)
    return render(request, "leader/matatizo.html", _chrome(
        request, "matatizo", rows=L.case_rows(cases), status=status,
        statuses=CaseStatus.choices, total=cases.count()))


@leader_required
def tatizo(request, pk):
    """Tatizo moja pamoja na hatua zake zote."""
    case = get_object_or_404(Case.objects.select_related("member"), pk=pk)
    if not L.scope_cases(request.user).filter(pk=pk).exists():
        raise Http404
    events = case.events.select_related("actor").all()
    return render(request, "leader/tatizo.html", _chrome(
        request, "matatizo", case=case, events=events,
        can_escalate=case.level != "national" and case.is_open))


@leader_required
@require_POST
def tatizo_action(request, pk, action):
    case = get_object_or_404(Case, pk=pk)
    if not L.scope_cases(request.user).filter(pk=pk).exists():
        raise Http404

    note = (request.POST.get("note") or "").strip()

    if action == "escalate":
        nxt = case.escalate(user=request.user, note=note)
        if nxt is None:
            messages.warning(request, _(
                "Tatizo hili tayari liko ngazi ya Taifa — hakuna pa kupandisha."))
        else:
            AuditLog.record(request, "case_escalated", case)
            messages.success(request, _(
                "Tatizo %(ref)s limepandishwa ngazi ya %(lv)s."
            ) % {"ref": case.reference, "lv": case.get_level_display()})

    elif action == "resolve":
        if not note:
            messages.error(request, _("Eleza suluhisho kabla ya kufunga tatizo."))
        else:
            case.resolve(user=request.user, resolution=note)
            AuditLog.record(request, "case_resolved", case)
            messages.success(request, _("Tatizo %(ref)s limetatuliwa.") % {
                "ref": case.reference})

    elif action == "comment":
        if note:
            case.log("comment", user=request.user, note=note)
            if case.status == CaseStatus.OPEN:
                case.status = CaseStatus.IN_PROGRESS
                case.save(update_fields=["status", "updated_at"])
            messages.success(request, _("Maoni yameongezwa."))

    return redirect("core:leader_tatizo", pk=pk)


# ---------------------------------------------------------------------------
#  Matangazo
# ---------------------------------------------------------------------------
@leader_required
def matangazo(request):
    post = L.leader_area(request.user)
    targets = L.broadcast_targets(request.user)

    if request.method == "POST":
        subject = (request.POST.get("subject") or "").strip()
        body = (request.POST.get("body") or "").strip()
        if not subject or not body:
            messages.error(request, _("Weka kichwa na ujumbe."))
        elif post is None and not sees_everyone(request.user):
            messages.error(request, _("Huna eneo la kutumia."))
        else:
            area = {}
            level = post.level if post else "national"
            if post:
                for f in ("ward", "district", "region", "zone"):
                    if getattr(post, f"{f}_id", None):
                        area[f] = getattr(post, f)
            b = Broadcast.objects.create(
                sender=request.user, level=level, subject=subject, body=body,
                reached=targets.count(), **area)
            AuditLog.record(request, "broadcast_sent", b)
            messages.success(request, _(
                "Tangazo limetumwa kwa wanachama %(n)d."
            ) % {"n": b.reached})
            return redirect("core:leader_matangazo")

    return render(request, "leader/matangazo.html", _chrome(
        request, "matangazo", sent=L.broadcasts_for(request.user),
        target_count=targets.count(),
        area=post.area_name if post else _("Taifa")))


# ---------------------------------------------------------------------------
#  Mazungumzo
# ---------------------------------------------------------------------------
@leader_required
def anzisha_mazungumzo(request, pk):
    """
    Kiongozi anaanzisha mazungumzo na mwanachama wake.

    Awali kiongozi angeweza kujibu tu — mwanachama ndiye aliyepaswa
    kuanza. Hilo lilikuwa kosa: kiongozi ndiye mwenye sababu nyingi za
    kuanzisha (kukumbusha ada, kuuliza hali, kufuatilia tatizo).
    """
    member = get_object_or_404(Member, pk=pk)
    if not can_see_member(request.user, member):
        raise Http404

    post = L.leader_area(request.user)
    level = post.level if post else "national"
    thread = L.open_thread(member, level=level)
    return redirect("core:leader_mazungumzo_moja", pk=thread.pk)


@leader_required
def mazungumzo(request):
    """
    Orodha ya mazungumzo, pamoja na sehemu ya KUANZISHA mapya.

    Awali kuanzisha kulikuwa kwenye ukurasa wa wanachama pekee, huku
    ukurasa huu ukisema "mwanachama akikuandikia, yataonekana hapa" —
    yaani ulimwambia kiongozi kwamba hawezi kuanzisha. Sasa anaweza
    kutafuta mwanachama na kuanzisha hapa hapa.
    """
    q = (request.GET.get("mtu") or "").strip()
    matokeo = L.member_rows(request.user, q=q)[:12] if q else []
    return render(request, "leader/mazungumzo.html", _chrome(
        request, "mazungumzo", threads=L.threads_for_leader(request.user),
        q=q, matokeo=matokeo))


@leader_required
def mazungumzo_moja(request, pk):
    thread = get_object_or_404(Thread.objects.select_related("member"), pk=pk)
    if not can_see_member(request.user, thread.member):
        raise Http404

    if request.method == "POST":
        body = (request.POST.get("body") or "").strip()
        if body:
            Message.objects.create(thread=thread, sender=request.user,
                                   from_leader=True, body=body)
            thread.touch()
            return redirect("core:leader_mazungumzo_moja", pk=pk)

    return render(request, "leader/mazungumzo_moja.html", _chrome(
        request, "mazungumzo", thread=thread,
        msgs=thread.messages.select_related("sender").all()))


# ---------------------------------------------------------------------------
#  Upande wa mwanachama
# ---------------------------------------------------------------------------
@login_required
def member_tatizo_mpya(request):
    """Mwanachama anafungua tatizo kwa kiongozi wa kata yake."""
    member = getattr(request.user, "member", None)
    if member is None:
        messages.error(request, _("Ukurasa huu ni wa wanachama."))
        return redirect("/")

    if request.method == "POST":
        subject = (request.POST.get("subject") or "").strip()
        body = (request.POST.get("body") or "").strip()
        if not subject or not body:
            messages.error(request, _("Weka kichwa na maelezo ya tatizo."))
        else:
            case = Case.objects.create(
                member=member, subject=subject, body=body,
                category=request.POST.get("category") or CaseCategory.OTHER,
                urgency=request.POST.get("urgency") or CaseUrgency.NORMAL)
            case.log("opened", user=request.user)
            AuditLog.record(request, "case_opened", case)
            messages.success(request, _(
                "Tatizo lako limepokelewa. Namba ya kumbukumbu: %(ref)s. "
                "Kiongozi wa kata yako atalishughulikia."
            ) % {"ref": case.reference})
            return redirect("core:member_matatizo")

    from .views import _chrome as base_chrome
    ctx = {"categories": CaseCategory.choices, "urgencies": CaseUrgency.choices}
    ctx.update(base_chrome(request, nav=navs.mwanachama("matatizo", user=request.user),
                           topbar_title="MUWESTA", topbar_sub=_("Toa Taarifa")))
    return render(request, "member/tatizo_mpya.html", ctx)


@login_required
def member_matatizo(request):
    member = getattr(request.user, "member", None)
    if member is None:
        return redirect("/")
    cases = Case.objects.filter(member=member).order_by("-created_at")

    from .views import _chrome as base_chrome
    ctx = {"rows": L.case_rows(cases),
           "broadcasts": L.member_broadcasts(member)}
    ctx.update(base_chrome(request, nav=navs.mwanachama("matatizo", user=request.user),
                           topbar_title="MUWESTA", topbar_sub=_("Matatizo Yangu")))
    return render(request, "member/matatizo.html", ctx)


@login_required
def member_viongozi(request):
    """
    Viongozi wa mwanachama, na sehemu ya kuzungumza nao.

    Mwanachama anaambiwa "toa taarifa kwa kiongozi wako" — ni haki yake
    kujua huyo ni nani na namba yake.
    """
    member = getattr(request.user, "member", None)
    if member is None:
        messages.error(request, _("Ukurasa huu ni wa wanachama."))
        return redirect("/")

    from .views import _chrome as base_chrome
    ctx = {"leaders": L.my_leaders(member),
           "threads": L.member_threads(member)}
    ctx.update(base_chrome(request, nav=navs.mwanachama("viongozi", user=request.user),
                           topbar_title="MUWESTA",
                           topbar_sub=_("Viongozi Wangu")))
    return render(request, "member/viongozi.html", ctx)


@login_required
def member_mazungumzo(request, level="ward"):
    """Mazungumzo ya mwanachama na ngazi fulani ya uongozi."""
    member = getattr(request.user, "member", None)
    if member is None:
        return redirect("/")

    valid = {c[0] for c in Thread._meta.get_field("level").choices}
    if level not in valid:
        raise Http404

    thread = L.open_thread(member, level=level)

    if request.method == "POST":
        body = (request.POST.get("body") or "").strip()
        if body:
            Message.objects.create(thread=thread, sender=request.user,
                                   from_leader=False, body=body)
            thread.touch()
        return redirect("core:member_mazungumzo", level=level)

    from .views import _chrome as base_chrome
    ctx = {"thread": thread, "level": level,
           "msgs": thread.messages.select_related("sender").all(),
           "leaders": [x for x in L.my_leaders(member) if x["level"] == level]}
    ctx.update(base_chrome(request, nav=navs.mwanachama("viongozi", user=request.user),
                           topbar_title="MUWESTA",
                           topbar_sub=_("Mazungumzo")))
    return render(request, "member/mazungumzo.html", ctx)


# ---------------------------------------------------------------------------
#  Vipengele vya mfumo, vilivyochujwa kwa eneo lake
# ---------------------------------------------------------------------------
@leader_required
def ada(request):
    hali = request.GET.get("hali") or ""
    return render(request, "leader/ada.html", _chrome(
        request, "ada", rows=L.ada_rows(request.user, hali=hali),
        hali=hali, wasiolipa=L.wasiolipa(request.user)))


@leader_required
@require_POST
def ada_action(request, pk, action):
    """
    Kiongozi anathibitisha malipo ya eneo lake.

    Ni ruhusa nzito — inagusa fedha. Kwa hiyo:
      * Mwanachama LAZIMA awe wa eneo lake (`can_touch_payment`)
      * Kila hatua inaandikwa kwenye `AuditLog` ikionyesha ni kiongozi,
        si afisa — ili kuwe na tofauti wakati wa ukaguzi
    """
    from finance.models import Payment, PaymentStatus

    payment = get_object_or_404(Payment, pk=pk)
    if not L.can_touch_payment(request.user, payment):
        raise Http404

    if action == "confirm":
        if payment.status == PaymentStatus.CONFIRMED:
            messages.info(request, _("Malipo haya tayari yamethibitishwa."))
        else:
            payment.status = PaymentStatus.CONFIRMED
            payment.save(update_fields=["status", "updated_at"])
            payment.post_to_ledger()
            AuditLog.record(request, "payment_confirmed_by_leader", payment)
            messages.success(request, _("Malipo %(no)s yamethibitishwa.") % {
                "no": payment.receipt_no})
    elif action == "cancel":
        payment.status = PaymentStatus.CANCELLED
        payment.save(update_fields=["status", "updated_at"])
        AuditLog.record(request, "payment_cancelled_by_leader", payment)
        messages.info(request, _("Malipo %(no)s yameghairiwa.") % {
            "no": payment.receipt_no})
    else:
        raise Http404
    return redirect("core:leader_ada")


@leader_required
def maombi(request):
    """Maombi mapya ya eneo lake — KUONA TU."""
    return render(request, "leader/maombi.html", _chrome(
        request, "maombi", rows=L.maombi_rows(request.user)))


@leader_required
def michango(request):
    return render(request, "leader/michango.html", _chrome(
        request, "michango", rows=L.michango_rows(request.user)))


@leader_required
def msaada(request):
    return render(request, "leader/msaada.html", _chrome(
        request, "msaada", rows=L.msaada_rows(request.user)))


@leader_required
def viongozi(request):
    """
    Viongozi walio chini yangu.

    Ni ukurasa wa ngazi za juu pekee — kiongozi wa kata hana ngazi ya
    chini, kwa hiyo anarudishwa kwenye dashibodi yake badala ya kuona
    ukurasa tupu.
    """
    data = L.viongozi_chini(request.user)
    if data is None:
        messages.info(request, _(
            "Ukurasa huu ni wa viongozi wenye maeneo chini yao."))
        return redirect("core:leader_dashboard")
    return render(request, "leader/viongozi.html", _chrome(
        request, "viongozi", **data))
