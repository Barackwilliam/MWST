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
