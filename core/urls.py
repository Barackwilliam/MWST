from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

urlpatterns = [
    # ---- Tovuti ya umma ----
    path("", views.home, name="home"),
    path("kuhusu/", views.kuhusu, name="kuhusu"),
    path("uanachama/", views.uanachama, name="uanachama"),
    path("huduma/", views.huduma, name="huduma"),
    path("habari/", views.habari, name="habari"),
    path("matukio-yetu/", views.matukio_umma, name="matukio_umma"),
    path("picha/", views.picha, name="picha"),
    path("mawasiliano/", views.mawasiliano, name="mawasiliano"),
    path("faragha/", views.faragha, name="faragha"),
    path("vidakuzi/", views.vidakuzi, name="vidakuzi"),
    path("jiunge/", views.jiunge, name="jiunge"),
    path("hakiki/<str:serial>/", views.card_verify, name="card_verify"),
    path("tukio/<int:pk>/jiandikishe/", views.event_register, name="event_register"),

    # ---- Uthibitisho ----
    path("ingia/", views.login_view, name="login"),
    path("toka/", views.logout_view, name="logout"),

    # ---- Kurejesha nenosiri (views za Django) ----
    path("nenosiri/sahau/", auth_views.PasswordResetView.as_view(
        template_name="public/password_reset.html",
        email_template_name="public/password_reset_email.txt",
        success_url=reverse_lazy("core:password_reset_done")),
        name="password_reset"),
    path("nenosiri/imetumwa/", auth_views.PasswordResetDoneView.as_view(
        template_name="public/password_reset_done.html"), name="password_reset_done"),
    path("nenosiri/weka/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="public/password_reset_confirm.html",
        success_url=reverse_lazy("core:password_reset_complete")),
        name="password_reset_confirm"),
    path("nenosiri/imekamilika/", auth_views.PasswordResetCompleteView.as_view(
        template_name="public/password_reset_complete.html"),
        name="password_reset_complete"),

    # ---- API ndogo ----
    path("api/wilaya/", views.api_districts, name="api_districts"),
    path("api/kata/", views.api_wards, name="api_wards"),

    # ---- Dashboards ----
    path("taifa/", views.national, name="national"),
    path("usajili/", views.usajili, name="usajili"),
    path("maombi/", views.maombi, name="maombi"),
    # Lazima iwe kabla ya <str:action> — vinginevyo "hariri" inachukuliwa kama action
    path("maombi/<int:pk>/hariri/", views.application_edit, name="application_edit"),
    path("maombi/<int:pk>/<str:action>/", views.maombi_action, name="maombi_action"),
    path("wanachama/", views.wanachama, name="wanachama"),
    path("malipo/", views.malipo, name="malipo"),
    path("michango/", views.michango, name="michango"),
    path("malipo/<int:pk>/<str:action>/", views.payment_action, name="payment_action"),
    path("michango/<int:pk>/<str:action>/", views.contribution_action, name="contribution_action"),
    path("risiti/<str:kind>/<int:pk>/", views.receipt, name="receipt"),
    path("mwanachama-taarifa/<int:pk>/", views.member_detail, name="member_detail"),
    path("mwanachama-taarifa/<int:pk>/hariri/", views.member_edit, name="member_edit"),
    path("ustawi/", views.assistance_review, name="assistance_review"),
    path("ujumbe/", views.broadcast, name="broadcast"),
    path("pakua/<str:kind>/", views.export, name="export"),

    # ---- Usimamizi wa mfumo (ndani ya dashibodi) ----
    path("mfumo/", views.manage_index, name="manage_index"),
    path("mfumo/<slug:slug>/", views.manage_list, name="manage_list"),
    path("mfumo/<slug:slug>/mpya/", views.manage_add, name="manage_add"),
    path("mfumo/<slug:slug>/<int:pk>/", views.manage_edit, name="manage_edit"),
    path("wadau/", views.wadau, name="wadau"),
    path("matukio/", views.matukio, name="matukio"),
    path("media/", views.media, name="media"),
    path("media/pakia/", views.media_upload, name="media_upload"),
    path("dashibodi/", views.dashboard, name="dashboard"),

    # ---- Mratibu wa kanda ----
    path("kanda/", views.coordinator, name="coordinator"),
    path("kanda/mikoa/", views.zone_regions, name="zone_regions"),
    path("kanda/wanachama/", views.zone_members, name="zone_members"),

    # ---- Mwanachama ----
    path("mwanachama/", views.member_dashboard, name="member_dashboard"),
    path("mwanachama/wasifu/", views.member_profile, name="member_profile"),
    path("mwanachama/malipo/", views.member_payments, name="member_payments"),
    path("mwanachama/michango/", views.member_contributions, name="member_contributions"),
    path("mwanachama/pointi/", views.member_points, name="member_points"),
    path("mwanachama/msaada/", views.member_assistance, name="member_assistance"),
    path("mwanachama/familia/", views.member_family, name="member_family"),
    path("mwanachama/kadi/", views.member_card, name="member_card"),
    path("mwanachama/kadi/chapisha/", views.member_card_print, name="member_card_print"),
    path("mwanachama/matukio/", views.member_events, name="member_events"),
    path("mwanachama/taarifa/", views.member_notices, name="member_notices"),
]
