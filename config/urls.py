import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# Django admin ipo kwa dharura pekee (mfano kurejesha data zilizoharibika).
# Haitajwi popote kwenye menyu — usimamizi wote unafanyika `/mfumo/`.
# Weka DJANGO_ADMIN_URL kwenye environment kuibadilisha au kuizima kabisa.
DJANGO_ADMIN_URL = os.environ.get("DJANGO_ADMIN_URL", "dharura-admin/")

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include(("core.urls", "core"), namespace="core")),
]

if DJANGO_ADMIN_URL:
    urlpatterns.insert(0, path(DJANGO_ADMIN_URL, admin.site.urls))

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "MWST — Usimamizi wa Mfumo"
admin.site.site_title = "MWST Admin"
admin.site.index_title = "Karibu kwenye usimamizi wa MWST"
