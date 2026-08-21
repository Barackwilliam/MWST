"""
Kutuma barua pepe za mfumo.

KANUNI KUU: kutuma barua pepe HAKUVUNJI ombi. SMTP inaweza kuchelewa,
kukataa, au kuzimika. Mtu anayejiunga asipate ukurasa wa hitilafu kwa
sababu Gmail ilikuwa na shida — ombi lake lihifadhiwe, na kosa liingie
kwenye log ili afisa aone.

Barua pepe zote hutumwa kwa Kiswahili na Kiingereza pamoja. Ni fupi,
kwa hiyo hakuna gharama ya kuweka lugha zote mbili — na hatuhitaji
kujua lugha ya mtu kabla hajaingia.
"""
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

log = logging.getLogger(__name__)

#: Rangi za MUWESTA — barua pepe ionekane inatoka kwao, si kwa mtu yeyote.
GREEN = "#0d5433"
GOLD = "#c9a227"


def is_configured():
    """
    Je, barua pepe zinatumwa kweli?

    Bila `EMAIL_HOST`, Django inaandika kwenye console badala ya kutuma.
    Hii ni muhimu kujua kabla ya kuwasha code za kuingia — vinginevyo
    kila mtu angefungiwa nje.
    """
    return bool(getattr(settings, "EMAIL_HOST", ""))


def _shell(title, intro, body_html, footer=""):
    return f"""<!DOCTYPE html><html><body style="margin:0;padding:24px;
background:#f6f7f5;font-family:-apple-system,Segoe UI,Roboto,sans-serif;color:#1a1a1a">
  <div style="max-width:520px;margin:0 auto;background:#fff;border-radius:14px;
overflow:hidden;border:1px solid #e6e8e4">
    <div style="background:linear-gradient(112deg,{GREEN},#12864a);padding:20px 24px">
      <div style="color:#fff;font-size:19px;font-weight:800;letter-spacing:.02em">MUWESTA</div>
      <div style="color:rgba(255,255,255,.72);font-size:11px;margin-top:2px">
        Muslim Welfare Society of Tanzania</div>
    </div>
    <div style="padding:24px">
      <h2 style="margin:0 0 10px;font-size:17px;color:{GREEN}">{title}</h2>
      <p style="margin:0 0 16px;font-size:13.5px;line-height:1.6;color:#444">{intro}</p>
      {body_html}
      <p style="margin:18px 0 0;font-size:11.5px;line-height:1.6;color:#888">{footer}</p>
    </div>
    <div style="padding:14px 24px;background:#fafbfa;border-top:1px solid #e6e8e4;
font-size:11px;color:#999">
      Shariff PBZ House, Nyerere Square, Dodoma &middot; +255 769 600 102
    </div>
  </div>
</body></html>"""


def _send(to, subject, text, html):
    """Tuma. Hurudisha True/False; haitupi kosa nje kamwe."""
    if not to:
        return False
    try:
        msg = EmailMultiAlternatives(
            subject=subject, body=text,
            from_email=settings.DEFAULT_FROM_EMAIL, to=[to])
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=False)
        return True
    except Exception:
        # `exception` inaingiza traceback nzima kwenye log ya Render.
        log.exception("Barua pepe kwenda %s haikutumwa", to)
        return False


# ---------------------------------------------------------------------------
#  Code ya tarakimu sita
# ---------------------------------------------------------------------------
def send_code(to, code, purpose, minutes=10):
    """Tuma code ya kuthibitisha barua pepe au ya kuingia."""
    if purpose == "login":
        title = "Code yako ya kuingia / Your sign-in code"
        intro = ("Tumia code hii kukamilisha kuingia kwenye mfumo wa MUWESTA.<br>"
                 "<span style='color:#888'>Use this code to complete your MUWESTA sign-in.</span>")
        footer = ("Kama si wewe uliyeomba kuingia, <b>badilisha nenosiri lako mara moja</b> "
                  "na uwasiliane nasi.<br>If you did not request this, change your password "
                  "immediately and contact us.")
    else:
        title = "Thibitisha barua pepe yako / Verify your email"
        intro = ("Karibu MUWESTA. Tumia code hii kuthibitisha kuwa barua pepe hii ni yako.<br>"
                 "<span style='color:#888'>Welcome to MUWESTA. Use this code to confirm "
                 "this email address is yours.</span>")
        footer = ("Kama hukuomba hii, puuza barua pepe hii.<br>"
                  "If you did not request this, please ignore this email.")

    body = f"""
      <div style="text-align:center;padding:18px;border-radius:12px;
background:#f1f7f3;border:1px solid #d6e6dd">
        <div style="font-size:34px;font-weight:800;letter-spacing:.28em;
color:{GREEN};font-family:ui-monospace,SFMono-Regular,monospace">{code}</div>
        <div style="margin-top:8px;font-size:11.5px;color:#777">
          Inaisha baada ya dakika {minutes} &middot; Expires in {minutes} minutes
        </div>
      </div>"""

    text = (f"MUWESTA\n\n{title}\n\nCode: {code}\n\n"
            f"Inaisha baada ya dakika {minutes}. Expires in {minutes} minutes.\n")
    return _send(to, f"MUWESTA: {code} — {title.split(' / ')[0]}",
                 text, _shell(title, intro, body, footer))


# ---------------------------------------------------------------------------
#  Arifa za kuingia
# ---------------------------------------------------------------------------
def send_login_alert(to, name, ip, device, ok=True):
    """
    Mjulishe mtu kwamba akaunti yake imeguswa.

    Hutumwa kwa kufaulu na kwa kushindwa. Kwa kushindwa, mtu anajua mtu
    fulani anajaribu nenosiri lake — ndiyo dalili ya kwanza ya shambulio.
    """
    when = timezone.localtime().strftime("%d %b %Y, %H:%M")
    if ok:
        title = "Umeingia kwenye mfumo / New sign-in"
        intro = (f"Habari {name}, akaunti yako imeingia sasa hivi.<br>"
                 f"<span style='color:#888'>Your account was just signed in.</span>")
        footer = ("Kama si wewe, <b>badilisha nenosiri lako mara moja</b>.<br>"
                  "If this was not you, change your password immediately.")
        tint, head = "#f1f7f3", GREEN
    else:
        title = "Jaribio la kuingia lililoshindwa / Failed sign-in attempt"
        intro = (f"Habari {name}, kuna aliyejaribu kuingia kwenye akaunti yako "
                 f"kwa nenosiri lisilo sahihi.<br>"
                 f"<span style='color:#888'>Someone tried to sign in to your account "
                 f"with the wrong password.</span>")
        footer = ("Kama si wewe, hakuna kilichofunguliwa — lakini ni vizuri "
                  "kubadilisha nenosiri lako.<br>If this was not you, nothing was "
                  "opened, but changing your password is wise.")
        tint, head = "#fdf3f2", "#b4231d"

    rows = [("Tarehe / Time", when), ("Anwani ya IP / IP", ip or "—"),
            ("Kifaa / Device", (device or "—")[:90])]
    body = f"""<div style="padding:14px 16px;border-radius:12px;background:{tint}">
      <table style="width:100%;font-size:12.5px;color:#444;border-collapse:collapse">
        {"".join(f'<tr><td style="padding:4px 0;color:#888">{k}</td>'
                 f'<td style="padding:4px 0;text-align:right;font-weight:600">{v}</td></tr>'
                 for k, v in rows)}
      </table></div>"""

    text = (f"MUWESTA\n\n{title}\n\n" +
            "\n".join(f"{k}: {v}" for k, v in rows) + "\n")
    return _send(to, f"MUWESTA: {title.split(' / ')[0]}",
                 text, _shell(title, intro, body, footer))
