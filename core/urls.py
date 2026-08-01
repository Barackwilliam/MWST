from django.urls import path
from . import views

urlpatterns = [
    # ---- Tovuti ya umma ----
    path("", views.home, name="home"),
    path("kuhusu/", views.kuhusu, name="kuhusu"),
    path("uanachama/", views.uanachama, name="uanachama"),
    path("huduma/", views.huduma, name="huduma"),
    path("habari/", views.habari, name="habari"),
    path("matukio-yetu/", views.matukio_umma, name="matukio_umma"),
    path("mawasiliano/", views.mawasiliano, name="mawasiliano"),
    path("jiunge/", views.jiunge, name="jiunge"),
    path("ingia/", views.login, name="login"),

    # ---- Dashboards ----
    path("taifa/", views.national, name="national"),
    path("usajili/", views.usajili, name="usajili"),
    path("malipo/", views.malipo, name="malipo"),
    path("michango/", views.michango, name="michango"),
    path("wadau/", views.wadau, name="wadau"),
    path("matukio/", views.matukio, name="matukio"),
    path("media/", views.media, name="media"),
    path("dashibodi/", views.dashboard, name="dashboard"),
    path("mwanachama/", views.member_dashboard, name="member_dashboard"),
]
