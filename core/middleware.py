"""Middleware ya mradi."""


class DefaultSwahiliMiddleware:
    """
    Kiswahili ndiyo lugha ya msingi — si lugha ya kivinjari.

    Django hupanga hivi: session -> cookie -> `Accept-Language` -> settings.
    Kwa hiyo mtu mwenye kivinjari cha Kiingereza alikuwa anapata tovuti ya
    Kiingereza hata bila kuomba. Hapa tunaondoa `Accept-Language` kabla
    `LocaleMiddleware` haijaisoma, ILI MRADI mtumiaji hajachagua lugha
    mwenyewe. Akichagua, chaguo lake linahifadhiwa kwenye session/cookie
    na hili halimgusi.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.conf import settings

        chosen = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        if not chosen:
            session = getattr(request, "session", None)
            if session is not None:
                chosen = session.get("_language")
        if not chosen:
            request.META.pop("HTTP_ACCEPT_LANGUAGE", None)
        return self.get_response(request)


class IdleTimeoutMiddleware:
    """
    Mtu aliyeingia anatolewa baada ya dakika `SESSION_IDLE_MINUTES` (5)
    bila shughuli yoyote, na anaombwa kuingia upya.

    "Shughuli" ni ombi lolote la ukurasa, pamoja na `/hai/` ambayo
    kivinjari hupiga kimya kimya mtu anapoandika au kusogeza ukurasa
    (angalia `mwst.js`) — bila hiyo, mtu anayejaza fomu ndefu angetolewa
    na kupoteza alichoandika. Maombi mengine ya nyuma (XHR), kama ukurasa
    wa kusubiri malipo unaouliza hali kila sekunde chache, HAYAHESABIWI:
    yangemweka mtu ndani milele hata akiondoka kwenye kompyuta.
    """

    #: Muda wa kusasisha alama ya shughuli. Kuandika session kila ombi
    #: ni kuandika database kila ombi; sekunde 15 zinatosha kwa usahihi.
    WRITE_EVERY = 15

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import time

        from django.conf import settings

        idle = getattr(settings, "SESSION_IDLE_SECONDS", 0)
        user = getattr(request, "user", None)
        if not idle or user is None or not user.is_authenticated:
            return self.get_response(request)
        #: Kutoka kunashughulikiwa na `logout_view` yenyewe. Bila hii, mtu
        #: aliyetolewa angepelekwa `/ingia/?next=/toka/` — na kuingia upya
        #: kungemtoa tena papo hapo.
        if request.path == "/toka/":
            return self.get_response(request)

        now = time.time()
        last = request.session.get("_last_activity")
        xhr = request.headers.get("x-requested-with") == "XMLHttpRequest"
        keepalive = request.path == "/hai/"

        if last and now - last > idle:
            return self._expire(request, xhr)

        if (not xhr or keepalive) and (not last or now - last >= self.WRITE_EVERY):
            request.session["_last_activity"] = now
        return self.get_response(request)

    def _expire(self, request, xhr):
        from django.contrib import messages
        from django.contrib.auth import logout
        from django.http import JsonResponse
        from django.shortcuts import redirect
        from django.urls import reverse
        from django.utils.http import urlencode
        from django.utils.translation import gettext as _

        logout(request)
        if xhr:
            return JsonResponse({"expired": True}, status=401)
        messages.info(request, _(
            "Umetolewa kwa sababu hukuwa na shughuli kwa muda. Tafadhali ingia upya."))
        url = reverse("core:login")
        if request.method == "GET":
            url += "?" + urlencode({"next": request.get_full_path()})
        return redirect(url)
