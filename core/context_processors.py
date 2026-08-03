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
    now = timezone.localtime()
    lang = (get_language() or "sw").lower()
    return {
        "year": now.year,
        "today": format_date(now, lang),
        "hijri": gettext("Mwaka %(y)d H") % {"y": hijri_year(now)},
        "org_name": "Muslim Welfare Society of Tanzania",
        "org_short": "MWST",
        "social": social_links(),
        "org_tagline": "Imani kwa Vitendo, Huduma na Maendeleo kwa Binadamu",
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
