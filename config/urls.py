import os

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from django.contrib import admin

# Django admin ni ya MSIMAMIZI MKUU pekee (`is_superuser`), si kila
# afisa — angalia `config/admin.py`.
#
# Njia yake inatoka `DJANGO_ADMIN_URL`. Njia ya siri si ulinzi kamili
# (mtu yeyote mwenye nenosiri la msimamizi mkuu bado anaingia), lakini
# inaondoa mashambulizi ya kubahatisha yanayolenga `/admin/` moja kwa
# moja — na hayo ni mengi.
#
# Ikiachwa tupu, Django admin haipatikani kabisa. Usimamizi wa kila
# siku unafanyika `/dashibodi/`.
DJANGO_ADMIN_URL = os.environ.get("DJANGO_ADMIN_URL", "dharura-admin/")

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include(("core.urls", "core"), namespace="core")),
]

if DJANGO_ADMIN_URL:
    urlpatterns.insert(0, path(DJANGO_ADMIN_URL, admin.site.urls))

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    #: WhiteNoise inahudumia `STATIC_ROOT` pekee. Faili zilizopakiwa —
    #: picha za wanachama, picha za maombi, faili za maktaba — ziko
    #: `MEDIA_ROOT`, kwa hiyo zote zilikuwa zikirudisha 404 kwenye
    #: production. Afisa alipakia picha, akaambiwa "imefanikiwa", kisha
    #: picha haikuonekana popote.
    #:
    #: Kuhudumia kwa Django si kwa kasi, lakini ni bora kuliko 404.
    #: TAZAMA: disk ya Render inafutika kila deploy — kwa faili
    #: zinazopaswa kudumu, tumia hifadhi ya nje (Supabase Storage au S3).
    from django.views.static import serve

    urlpatterns += [
        path("media/<path:path>", serve, {"document_root": settings.MEDIA_ROOT}),
    ]
