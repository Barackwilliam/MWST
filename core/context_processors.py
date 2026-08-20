"""Vitu vinavyoonekana kwenye kila ukurasa."""
from django.utils import timezone
from django.utils.translation import get_language, gettext

# Majina ya siku na miezi kwa Kiswahili. Kiingereza kinatoka kwa strftime.
DAYS_SW = ["Jumatatu", "Jumanne", "Jumatano", "Alhamisi",
           "Ijumaa", "Jumamosi", "Jumapili"]
MONTHS_SW = ["Januari", "Februari", "Machi", "Aprili", "Mei", "Juni",
             "Julai", "Agosti", "Septemba", "Oktoba", "Novemba", "Desemba"]


def format_date(dt, lang):
    """Tarehe kamili kwa lugha inayotumika sasa."""
    if lang.startswith("en"):
        return dt.strftime("%A, %d %B %Y")
    return f"{DAYS_SW[dt.weekday()]}, {dt.day:02d} {MONTHS_SW[dt.month - 1]} {dt.year}"


def hijri_year(dt):
    """
    Kadirio la mwaka wa Hijri kutoka mwaka wa Gregorian.

    Ni fomula ya kukadiria, si hesabu kamili ya kalenda ya mwezi —
    inatosha kwa kuonyesha kwenye topbar. Kwa usahihi kamili
    inahitaji library ya kalenda ya Kiislamu.
    """
    g = dt.year + (dt.timetuple().tm_yday / 365.25)
    return int((g - 622) * 33 / 32) + 1


def social_links():
    """Viungo vya mitandao kutoka kwenye mipangilio. Visivyowekwa vinafichwa."""
    from content.models import SiteSetting
    st = SiteSetting.get()
    wa = (st.whatsapp or "").replace(" ", "").replace("+", "")
    rows = [
        ("facebook", "facebook", st.facebook),
        ("x-social", "X", st.twitter),
        ("youtube", "YouTube", st.youtube),
        ("instagram", "instagram", st.instagram),
        ("whatsapp", "WhatsApp", f"https://wa.me/{wa}" if wa else ""),
    ]
    return [{"icon": i, "label": lbl, "url": u} for i, lbl, u in rows if u]


def brand(request):
    from content.models import SiteSetting

    now = timezone.localtime()
    lang = (get_language() or "sw").lower()
    st = SiteSetting.get()

    # Hali ya kuingia — inatumika kwenye header, drawer na kila CTA ya "Jiunge".
    user = getattr(request, "user", None)
    authed = bool(user is not None and user.is_authenticated)
    role = getattr(user, "role", "") if authed else ""

    # Namba ya simu inayotumika kwenye viungo vya `tel:` — bila nafasi.
    phone = (st.phone or "").strip()
    phone_link = phone.replace(" ", "").replace("-", "")

    return {
        "is_authed": authed,
        # Mhisani bado anaweza kujiunga kama mwanachama; wengine tayari wamo.
        "can_join": (not authed) or role == "donor",
        "is_donor": role == "donor",
        "year": now.year,
        "today": format_date(now, lang),
        "hijri": gettext("Mwaka %(y)d H") % {"y": hijri_year(now)},
        #: Vitu hivi vinatoka kwenye mipangilio ya tovuti (SiteSetting),
        #: si kwenye code. Ofisi ikibadilisha namba ya simu au anwani,
        #: inabadilika kila mahali bila kuhitaji deployment mpya.
        "settings_obj": st,
        "org_name": st.org_name or "Muslim Welfare Society of Tanzania",
        "org_short": "MUWESTA",
        "org_phone": phone,
        "org_phone_link": phone_link,
        "org_email": st.email or "",
        "social": social_links(),
        "org_tagline": ((st.tagline_en if lang.startswith("en") else st.tagline)
                        or st.tagline or "Imani kwa Vitendo, Huduma na Maendeleo kwa Binadamu"),
        "org_address": ((st.address_en if lang.startswith("en") else st.address)
                        or st.address or ""),
        "org_values": ["Imani", "Huruma", "Huduma", "Maendeleo"],
        "i18n_js": {
            # Ujumbe huu unaonekana tu kwa vipengele vichache ambavyo
            # bado havijajengwa (SMS, barua pepe, PDF, ripoti za Excel).
            # Kila kitu kingine kinafanya kazi kwa data halisi.
            "backend_pending": gettext(
                "Kipengele hiki bado hakijajengwa. Kinahitaji huduma ya nje "
                "(SMS, barua pepe, PDF au Excel) itakayoungwa awamu ijayo. "
                "Vipengele vingine vyote vinafanya kazi kwa data halisi."
            ),
            "pending_eyebrow": gettext("Awamu ijayo"),
            "pending_title": gettext("Kipengele hiki"),
            "pending_chip": gettext("Data nyingine yote ni halisi"),
            "pending_close": gettext("Sawa, nimeelewa"),
            "pending_explore": gettext("Endelea Kutazama"),
        },
    }
