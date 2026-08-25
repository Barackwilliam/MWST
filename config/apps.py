"""
Usanidi wa `django.contrib.admin` kwa MUWESTA.

`AdminConfig` ya Django inaendesha `autodiscover()` inayosoma `admin.py`
ya kila app. Tunahitaji `admin.site` iwe yetu KABLA ya hapo — vinginevyo
kila `@admin.register(...)` ingesajili kwenye site ya Django, na yetu
ingebaki tupu.
"""
from django.contrib.admin.apps import AdminConfig as DjangoAdminConfig


class AdminConfig(DjangoAdminConfig):
    default_site = "config.admin.MuwestaAdminSite"
