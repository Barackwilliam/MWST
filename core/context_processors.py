from datetime import datetime

from django.utils.translation import gettext


def brand(request):
    """Vitu vinavyoonekana kwenye kila ukurasa."""
    now = datetime.now()
    return {
        "year": now.year,
        "today": now.strftime("%A, %d %B %Y")
            .replace("Monday", "Jumatatu").replace("Tuesday", "Jumanne")
            .replace("Wednesday", "Jumatano").replace("Thursday", "Alhamisi")
            .replace("Friday", "Ijumaa").replace("Saturday", "Jumamosi")
            .replace("Sunday", "Jumapili"),
        "org_name": "Muslim Welfare Society of Tanzania",
        "org_short": "MWST",
        "org_tagline": "Imani kwa Vitendo, Huduma na Maendeleo kwa Binadamu",
        "org_values": ["Imani", "Huruma", "Huduma", "Maendeleo"],
        "i18n_js": {
            "backend_pending": gettext(
                "Kipengele hiki kitapatikana mfumo wa nyuma (backend) utakapokamilika. "
                "Kwa sasa unaona muundo na taarifa za mfano."
            ),
            "pending_eyebrow": gettext("Inakuja hivi karibuni"),
            "pending_title": gettext("Kipengele hiki"),
            "pending_chip": gettext("Muundo umekamilika \u2014 data ni ya mfano"),
            "pending_close": gettext("Sawa, nimeelewa"),
            "pending_explore": gettext("Endelea Kutazama"),
        },
    }
