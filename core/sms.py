"""
Kutuma SMS kupitia NextSMS (messaging-service.co.tz).

KANUNI KUU: kutuma SMS HAKUVUNJI ombi — kama ilivyo kwenye `mailer.py`.
Mtandao unaweza kukatika, salio linaweza kuisha, au NextSMS wanaweza
kuwa na hitilafu. Mtu anayejiunga asipate ukurasa wa hitilafu kwa sababu
ya lolote kati ya hayo.

Tanzania inatumia SMS zaidi ya barua pepe, na SMS inafika hata kwenye
simu ya kawaida isiyo na intaneti. Ndiyo maana mfumo huu upo.

--- Mambo ya NextSMS yanayoathiri muundo ------------------------------

1. KIKOMO CHA KUFURIKA (status 63): namba moja inaweza kupokea ujumbe
   20 tofauti au 6 unaofanana kwa saa. Code za kuingia zote ni tofauti
   (kila moja ina tarakimu zake), kwa hiyo kikomo ni 20 — lakini bado
   ni sababu ya kuweka kikomo chetu wenyewe.

2. JINA LA MTUMAJI (status 58): lazima lisajiliwe kwenye NextSMS.
   Lisilosajiliwa linarudisha FAILED_SENDER bila SMS kutumwa.

3. SALIO (status 57): likiisha, kila SMS inashindwa. Ndiyo maana
   `send()` inarudisha False badala ya kutupa kosa — mfumo unaendelea.

4. TEST MODE: `/api/sms/v2/test/text/single` inarudisha jibu la kweli
   bila kutuma wala kupunguza salio. Ndiyo tunayotumia kwenye
   development.
"""
import base64
import json
import logging
import re
import urllib.error
import urllib.request

from django.conf import settings

log = logging.getLogger(__name__)

BASE = "https://messaging-service.co.tz"
TIMEOUT = 20


class SmsError(Exception):
    """Kosa lolote linalotoka NextSMS au kwenye mawasiliano nayo."""


def is_configured():
    """
    Je, SMS zinatumwa kweli?

    Inahitaji jina la mtumaji pamoja na token AU (username na password).
    Kikosekana kimoja, hakuna SMS itakayotumwa — na ni bora kujua hilo
    kabla ya kuwasha code za kuingia kuliko baada.
    """
    if not getattr(settings, "NEXTSMS_SENDER", ""):
        return False
    if getattr(settings, "NEXTSMS_TOKEN", ""):
        return True
    return bool(getattr(settings, "NEXTSMS_USERNAME", "")
                and getattr(settings, "NEXTSMS_PASSWORD", ""))


def msisdn(phone):
    """
    Geuza namba ya simu kuwa muundo wa kimataifa unaotakiwa: 255XXXXXXXXX.

    Watu huandika namba kwa njia nyingi — 0769..., +255769..., 255769...,
    au yenye nafasi na mistari. Zote zinakuwa 255769600102.

    Namba isiyoeleweka inarudishwa kama ilivyo baada ya kusafishwa;
    NextSMS itaikataa na tutaona kosa kwenye log. Ni bora kuliko
    kubadilisha namba ya mtu kimakosa.
    """
    digits = re.sub(r"\D", "", str(phone or ""))
    if digits.startswith("255"):
        return digits
    if digits.startswith("0"):
        return "255" + digits[1:]
    # 9 tarakimu bila sufuri wala msimbo wa nchi: 769600102
    if len(digits) == 9:
        return "255" + digits
    return digits


def _auth_header():
    token = getattr(settings, "NEXTSMS_TOKEN", "")
    if token:
        return f"Bearer {token}"
    raw = f"{settings.NEXTSMS_USERNAME}:{settings.NEXTSMS_PASSWORD}"
    return "Basic " + base64.b64encode(raw.encode()).decode()


def _endpoint():
    """
    Njia ya kutuma. Test mode inarudisha jibu la kweli bila kutuma SMS
    wala kupunguza salio — ndiyo ya development.
    """
    if getattr(settings, "NEXTSMS_TEST_MODE", False):
        return "/api/sms/v2/test/text/single"
    return "/api/sms/v2/text/single"


def send(phone, text, reference="", queue=True):
    """
    Tuma SMS moja. Hurudisha True/False; haitupi kosa nje kamwe.

    `reference` ni kitambulisho chetu — kinasaidia kufuatilia ujumbe
    kwenye dashibodi ya NextSMS.

    `queue=False` inatumiwa na amri inayotuma foleni yenyewe. Bila hiyo,
    ujumbe uliokataliwa ungejiongeza kwenye foleni tena kila jaribio na
    foleni isingeisha kamwe.
    """
    to = msisdn(phone)

    # Namba inakaguliwa KWANZA. Namba mbovu haitengenezeki kwa kujaribu
    # tena, kwa hiyo haiingii kwenye foleni — ingekaa pale milele
    # ikijaribiwa bila mafanikio na kujaza foleni.
    if len(to) < 12:
        log.error("Namba si sahihi: %r (imekuwa %r)", phone, to)
        return False

    if not is_configured():
        log.warning("NextSMS haijawekwa — SMS kwenda %s imeingia foleni", to)
        if queue:
            _queue(to, text, reference, "haijawekwa")
        return False

    payload = {
        "from": settings.NEXTSMS_SENDER,
        "to": to,
        "text": text,
    }
    if reference:
        payload["reference"] = reference[:60]

    req = urllib.request.Request(
        BASE + _endpoint(),
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": _auth_header(),
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            body = json.loads(res.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:400]
        log.error("NextSMS %s -> HTTP %s: %s", to, e.code, detail)
        if queue:
            _queue(to, text, reference, f"HTTP {e.code}")
        return False
    except Exception as e:
        log.exception("NextSMS %s haikufikiwa", to)
        if queue:
            _queue(to, text, reference, str(e)[:120])
        return False

    ok, reason = _ok(body, to)
    if not ok and queue and _worth_retry(reason):
        _queue(to, text, reference, reason)
    return ok


def _ok(body, to):
    """
    Soma jibu la NextSMS. Hurudisha (imefaulu, sababu).

    Jibu lenye mafanikio lina `messages` yenye `status`. Hali za kundi
    PENDING (18) na DELIVERY (20) ni nzuri; REJECTED (19) na FAILED (22)
    si nzuri, na kila moja ina sababu inayosaidia kutatua.
    """
    messages = body.get("messages") or []
    if not messages:
        log.error("NextSMS %s -> jibu lisilo na messages: %s",
                  to, json.dumps(body)[:300])
        return False, "jibu lisiloeleweka"

    status = (messages[0] or {}).get("status") or {}
    group = status.get("groupId")
    name = status.get("name", "?")

    if group in (18, 20):          # PENDING au DELIVERY
        log.info("NextSMS %s -> %s", to, name)
        return True, ""

    # REJECTED (19) na FAILED (22) — maelezo yanasaidia kutatua haraka
    log.error("NextSMS %s -> %s: %s", to, name, status.get("description", ""))
    return False, name


#: Sababu zisizotengenezeka kwa kujaribu tena. Namba iliyozuiwa au isiyo
#: sahihi itakataliwa milele — kuiweka kwenye foleni ni kupoteza muda na
#: kujaza foleni kwa ujumbe usiotumika kamwe.
NO_RETRY = {
    "REJECTED_DND",                       # mtu amejiondoa
    "REJECTED_DESTINATION",               # namba imezuiwa
    "REJECTED_INVALID_DESTINATION",       # namba si sahihi
    "REJECTED_PREFIX_MISSING",            # mtandao hautambuliki
    "REJECTED_DESTINATION_NOT_REGISTERED",
    "REJECTED_MESSAGE_TOO_LONG",
    "REJECTED_DUPLICATE_MESSAGE_ID",
}


def _worth_retry(reason):
    """Je, inafaa kujaribu tena? Salio na mtandao ndiyo; namba mbovu hapana."""
    return reason not in NO_RETRY


def _queue(to, text, reference, error):
    """Hifadhi kwenye foleni. Haivunji chochote ikishindikana."""
    try:
        from content.models import SmsOutbox
        SmsOutbox.enqueue(to, text, reference, error)
    except Exception:
        log.exception("SMS kwenda %s haikuingia kwenye foleni", to)


def balance():
    """
    Salio lililobaki. Hurudisha namba, au `None` ikishindikana.

    Nyaraka za NextSMS zinasema maombi YOTE ni POST, lakini njia ya salio
    hufanya kazi kwa GET kwenye baadhi ya akaunti. Tunajaribu zote mbili
    badala ya kukisia — na tunaonyesha jibu halisi kwenye log, kwa sababu
    "403 Forbidden" peke yake haitoshi kutatua tatizo.

    Inatumiwa na amri `salio_sms`. SMS zikiisha, code za kuingia zinaacha
    kufanya kazi kimya kimya — ni tatizo linalotakiwa kugundulika mapema.
    """
    if not is_configured():
        return None

    for path, method in (("/api/sms/v1/balance", "GET"),
                         ("/api/sms/v1/balance", "POST")):
        body = _get(path, method)
        if body is None:
            continue
        for key in ("sms_balance", "balance", "credits", "smsBalance"):
            if key in body:
                try:
                    return int(float(body[key]))
                except (TypeError, ValueError):
                    return None
        log.error("Salio: jibu lisilo na salio -> %s", json.dumps(body)[:300])
    return None


def _get(path, method="GET"):
    """Ombi dogo la kusoma. Hurudisha JSON au `None`, na huandika kosa halisi."""
    data = b"{}" if method == "POST" else None
    req = urllib.request.Request(
        BASE + path, data=data, method=method,
        headers={
            "Authorization": _auth_header(),
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            return json.loads(res.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:400]
        log.error("NextSMS %s %s -> HTTP %s: %s", method, path, e.code, detail)
    except Exception:
        log.exception("NextSMS %s %s haikufikiwa", method, path)
    return None


# ---------------------------------------------------------------------------
#  Ujumbe wa mfumo
#
#  SMS hulipiwa kwa kila sehemu 160. Ujumbe hapa chini umewekwa mfupi
#  kwa makusudi — kila herufi ya ziada ni gharama inayojirudia.
# ---------------------------------------------------------------------------
def send_code(phone, code, purpose, minutes=10):
    """
    Code ya kuthibitisha namba au ya kuingia.

    `queue=False` KWA MAKUSUDI. Code inaisha baada ya dakika 10; ikitumwa
    saa mbili baadaye na foleni, mtu anapokea code isiyofanya kazi na
    kuchanganyikiwa — na huenda akadhani ni ulaghai. Ni bora ishindwe
    sasa hivi (mfumo unamruhusu aingie) kuliko ifike imechelewa.
    """
    if purpose == "login":
        text = (f"MUWESTA: Code yako ya kuingia ni {code}. "
                f"Inaisha baada ya dakika {minutes}. Usimpe mtu yeyote.")
    else:
        text = (f"MUWESTA: Code yako ya kuthibitisha ni {code}. "
                f"Inaisha baada ya dakika {minutes}.")
    return send(phone, text, reference=f"code-{purpose}", queue=False)


def send_login_alert(phone, name, ok=True):
    """
    Mjulishe mtu kwamba akaunti yake imeguswa.

    Hakuna IP wala kifaa hapa — SMS ni fupi, na taarifa hizo hazina
    maana kwa mtu wa kawaida. Zipo kwenye barua pepe kwa anayezihitaji.
    """
    first = (name or "").split()[0] if name else ""
    if ok:
        text = (f"MUWESTA: Habari {first}, akaunti yako imeingia sasa hivi. "
                f"Kama si wewe, badilisha nenosiri mara moja.")
    else:
        text = (f"MUWESTA: Habari {first}, kuna aliyejaribu kuingia kwenye "
                f"akaunti yako kwa nenosiri lisilo sahihi.")
    return send(phone, text, reference="login-alert")


def send_application_received(phone, reference):
    """
    Hongera baada ya kutuma ombi la uanachama.

    Ujumbe umefupishwa hadi herufi 147 kwa makusudi. SMS hulipiwa kwa
    sehemu 160 — toleo la kwanza lilikuwa 174, yaani SMS mbili kwa kila
    mwombaji. Namba ya kumbukumbu imebaki kwa sababu ndiyo atakayoitumia
    kulipia (/lipa/?ombi=...).
    """
    text = (f"MUWESTA: Hongera! Ombi lako limepokelewa. Kumbukumbu: {reference}. "
            f"Subiri uthibitisho wa afisa upate namba ya uanachama na uanze kulipia.")
    return send(phone, text, reference="ombi-limepokelewa")


def send_application_approved(phone, reference, amount, url):
    """
    Ombi limehakikiwa — sasa analipa.

    Hii ndiyo hatua iliyokuwa haipo: afisa alikuwa anapata kiungo cha
    malipo, lakini mwombaji hakuwa anaambiwa chochote. Alikuwa akisubiri
    simu ambayo huenda isipigwe.
    """
    text = (f"MUWESTA: Ombi {reference} limehakikiwa. Lipa TZS {amount:,} "
            f"kuanza uanachama: {url}")
    return send(phone, text, reference="ombi-limehakikiwa")


def send_membership_ready(phone, membership_no):
    """
    Malipo yamethibitishwa — uanachama umeanza.

    NENOSIRI HALIPELEKWI kwa SMS. SMS haifutiki kwenye simu, na simu
    hupotea au hukopeshwa. Afisa ndiye anayempa nenosiri la muda ana kwa
    ana au kwa simu.
    """
    text = (f"MUWESTA: Karibu! Uanachama wako umeanza. Namba yako: "
            f"{membership_no}. Wasiliana na afisa upate taarifa za kuingia.")
    return send(phone, text, reference="uanachama-tayari")


# ---------------------------------------------------------------------------
#  KUNDI A — pesa na ufikiaji
#
#  Hizi zinahusu pesa au uwezo wa kuingia. Risiti kwa SMS ni kitu mtu
#  anakihifadhi simuni na kukirejea; asipopata uthibitisho, atapiga simu
#  ofisini — na hiyo nayo ni gharama.
# ---------------------------------------------------------------------------
def send_contribution_receipt(phone, amount, receipt_no, purpose=""):
    """Risiti ya mchango uliothibitishwa."""
    what = f" ({purpose})" if purpose else ""
    text = (f"MUWESTA: Asante! Tumepokea TZS {amount:,}{what}. "
            f"Risiti: {receipt_no}. Mungu akubariki.")
    return send(phone, text, reference="risiti-mchango")


def send_fee_receipt(phone, amount, receipt_no, months=0):
    """Risiti ya ada ya uanachama."""
    muda = f" kwa miezi {months}" if months else ""
    text = (f"MUWESTA: Tumepokea ada yako TZS {amount:,}{muda}. "
            f"Risiti: {receipt_no}. Asante.")
    return send(phone, text, reference="risiti-ada")


def send_renewal_done(phone, expires_on):
    """Uanachama umehuishwa."""
    text = (f"MUWESTA: Uanachama wako umehuishwa. Sasa ni halali hadi "
            f"{expires_on:%d/%m/%Y}. Kadi mpya inapatikana ofisini.")
    return send(phone, text, reference="uhuisho")


def send_payment_failed(phone, amount):
    """
    Malipo hayakukamilika.

    Muhimu kuliko inavyoonekana: mtu asiyeambiwa hujua hakuna kilichotoka
    kwenye akaunti yake, na huweza kulipa mara ya pili bila sababu.
    """
    text = (f"MUWESTA: Malipo yako ya TZS {amount:,} hayakukamilika. "
            f"Hakuna kilichokatwa. Unaweza kujaribu tena.")
    return send(phone, text, reference="malipo-hayakukamilika")


def send_password_reset(phone, username):
    """Nenosiri limewekwa upya na afisa."""
    text = (f"MUWESTA: Nenosiri la akaunti {username} limewekwa upya. "
            f"Wasiliana na afisa upate la muda. Kama si wewe, tujulishe.")
    return send(phone, text, reference="nenosiri-limewekwa-upya")


# ---------------------------------------------------------------------------
#  KUNDI B — mabadiliko ya hali
# ---------------------------------------------------------------------------
def send_expiry_notice(phone, expires_on, days_left, url):
    """Kumbusho la uanachama unaokaribia kuisha."""
    if days_left < 0:
        text = (f"MUWESTA: Uanachama wako uliisha {expires_on:%d/%m/%Y}. "
                f"Huisha hapa: {url}")
    else:
        text = (f"MUWESTA: Uanachama wako unaisha {expires_on:%d/%m/%Y} "
                f"(siku {days_left}). Huisha hapa: {url}")
    return send(phone, text, reference="muda-unaisha")


def send_application_rejected(phone, reference):
    """Ombi la uanachama halikukubaliwa."""
    text = (f"MUWESTA: Samahani, ombi {reference} halikukubaliwa. "
            f"Wasiliana nasi kwa maelezo zaidi: 0769600102")
    return send(phone, text, reference="ombi-limekataliwa")


def send_assistance_received(phone, reference):
    """Ombi la msaada limepokelewa."""
    text = (f"MUWESTA: Ombi lako la msaada limepokelewa. Kumbukumbu: "
            f"{reference}. Tutakujulisha baada ya kulipitia.")
    return send(phone, text, reference="msaada-limepokelewa")


def send_assistance_decision(phone, reference, approved):
    """Jibu la ombi la msaada."""
    if approved:
        text = (f"MUWESTA: Ombi lako la msaada {reference} limekubaliwa. "
                f"Wasiliana na afisa wa ustawi kwa hatua zinazofuata.")
    else:
        text = (f"MUWESTA: Ombi lako la msaada {reference} halikukubaliwa "
                f"kwa sasa. Wasiliana nasi kwa maelezo: 0769600102")
    return send(phone, text, reference="msaada-jibu")


def send_card_issued(phone, serial, expires_on):
    """Kadi mpya imetolewa."""
    text = (f"MUWESTA: Kadi yako mpya {serial} iko tayari, inaisha "
            f"{expires_on:%d/%m/%Y}. Ichukue ofisini.")
    return send(phone, text, reference="kadi-mpya")
