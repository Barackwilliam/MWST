"""
Mteja wa Selcom Checkout API.

Faida kuu juu ya Pesapal: **USSD push**. Mtu anaingiza namba ya simu,
anapokea kidokezo cha M-Pesa/Airtel/Mixx kwenye simu yake, na analipa
bila kuondoka kwenye tovuti yetu. Pesapal humtoa nje kwenda ukurasa
wake — hatua ya ziada ambayo huwapoteza baadhi ya watu.

MTIRIRIKO
---------
    1. create_order_minimal  -> order imeundwa upande wa Selcom
    2. wallet_pull_payment   -> kidokezo kinatumwa kwenye simu ya mtu
    3. Mtu anaingiza PIN yake kwenye simu
    4. Selcom inapiga webhook YETU, na pia tunaweza kuuliza wenyewe
    5. order_status          -> hali halisi ya malipo

USALAMA
-------
* Selcom hutumia HMAC-SHA256, si bearer token. Kila ombi linatiwa saini
  kwa `api_secret` ambayo HAIENDI kwenye mtandao kamwe — inayoenda ni
  saini pekee. Hii ni bora kuliko token inayoweza kuibiwa ikiwa njiani.
* Saini inahusisha `timestamp`, kwa hiyo ombi lililonaswa haliwezi
  kutumika tena baadaye (replay attack).
* Webhook PEKEE haitoshi kuthibitisha malipo — mtu anaweza kuipiga
  mwenyewe. Hali halisi HULAZIMA ithibitishwe kwa `order_status`, sawa
  na tunavyofanya kwa Pesapal.
* Namba za simu hazihifadhiwi kwa Selcom; PIN inaingizwa kwenye simu ya
  mtu mwenyewe, si kwenye tovuti yetu.
"""
import base64
import hashlib
import hmac
import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone as dt_timezone

from django.conf import settings

log = logging.getLogger(__name__)

#: Selcom haina mazingira mawili tofauti kwa URL; ni akaunti tofauti.
#: Anwani hii ni ile ile kwa majaribio na kwa uzalishaji.
BASE = "https://apigw.selcommobile.com/v1"

TIMEOUT = 30


class SelcomError(Exception):
    """Kosa lolote linalotoka Selcom au kwenye mawasiliano nayo."""


def is_configured():
    return bool(getattr(settings, "SELCOM_API_KEY", "")
                and getattr(settings, "SELCOM_API_SECRET", "")
                and getattr(settings, "SELCOM_VENDOR_ID", ""))


# ---------------------------------------------------------------------------
#  Saini
# ---------------------------------------------------------------------------
def _timestamp():
    """
    Muundo wa ISO-8601 wenye eneo la saa, mfano 2026-08-17T14:22:05+03:00.

    Selcom inakataa muundo mwingine wowote, na saini inaihusisha — kwa
    hiyo hii lazima iwe sawa kabisa.
    """
    now = datetime.now(dt_timezone.utc).astimezone()
    return now.strftime("%Y-%m-%dT%H:%M:%S%z")[:-2] + ":" + now.strftime("%z")[-2:]


def _sign(payload, timestamp):
    """
    Tengeneza saini ya HMAC-SHA256 kwa mujibu wa Selcom.

    Selcom huunganisha `timestamp` na kila thamani ya payload KWA
    MPANGILIO ULE ULE unaotumwa kwenye `signed-fields`. Mpangilio ukibadilika,
    saini haitalingana — ndiyo maana tunatumia orodha moja kwa vyote
    badala ya kutegemea mpangilio wa dict.
    """
    keys = list(payload.keys())
    buf = "timestamp=" + timestamp
    for key in keys:
        buf += f"&{key}={payload[key]}"

    digest = hmac.new(
        settings.SELCOM_API_SECRET.encode("utf-8"),
        buf.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode(), ",".join(keys)


def _headers(payload):
    timestamp = _timestamp()
    signature, signed_fields = _sign(payload, timestamp)
    token = base64.b64encode(settings.SELCOM_API_KEY.encode()).decode()
    return {
        "Content-Type": "application/json",
        "Authorization": f"SELCOM {token}",
        "Digest-Method": "HS256",
        "Digest": signature,
        "Timestamp": timestamp,
        "Signed-Fields": signed_fields,
    }


# ---------------------------------------------------------------------------
#  Mawasiliano
# ---------------------------------------------------------------------------
def _request(path, payload=None, method="POST"):
    url = f"{BASE}{path}"
    body = None

    if method == "GET" and payload:
        # GET inahitaji saini pia, lakini data inaenda kwenye query string.
        headers = _headers(payload)
        url = f"{url}?{urllib.parse.urlencode(payload)}"
    else:
        payload = payload or {}
        headers = _headers(payload)
        body = json.dumps(payload).encode()

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode()
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        log.error("Selcom %s -> HTTP %s %s", path, exc.code, raw[:400])
        raise SelcomError(_message(raw) or f"Selcom imekataa ombi ({exc.code})")
    except urllib.error.URLError as exc:
        log.error("Selcom %s -> %s", path, exc.reason)
        raise SelcomError("Imeshindikana kufikia Selcom. Jaribu tena.")

    try:
        data = json.loads(raw)
    except ValueError:
        log.error("Selcom %s -> jibu si JSON: %s", path, raw[:300])
        raise SelcomError("Jibu la Selcom halieleweki.")

    # Selcom hurudisha `resultcode` "000" kwa mafanikio.
    if str(data.get("resultcode", "")) not in ("000", "111"):
        message = data.get("message") or data.get("result") or ""
        log.error("Selcom %s -> %s %s", path, data.get("resultcode"), message)
        raise SelcomError(message or "Kosa kutoka Selcom")

    return data


def _message(raw):
    try:
        return json.loads(raw).get("message", "")
    except Exception:
        return ""


# ---------------------------------------------------------------------------
#  Vitendo
# ---------------------------------------------------------------------------
def create_order(*, order_id, amount, buyer_name, buyer_phone,
                 buyer_email="", webhook_url="", currency="TZS", days=1):
    """
    Unda order upande wa Selcom.

    `order_id` ni namba yetu ya risiti — ndiyo tunayoitumia kuunganisha
    malipo na rekodi yetu tunapopokea webhook.
    """
    payload = {
        "vendor": settings.SELCOM_VENDOR_ID,
        "order_id": order_id,
        "buyer_email": buyer_email or "malipo@muslimwelfare.or.tz",
        "buyer_name": buyer_name[:60],
        "buyer_phone": _msisdn(buyer_phone),
        "amount": int(amount),
        "currency": currency,
        "no_of_items": 1,
    }
    if webhook_url:
        # Selcom inahitaji webhook ikiwa base64.
        payload["webhook"] = base64.b64encode(webhook_url.encode()).decode()
    payload["expiry"] = days * 24 * 60

    return _request("/checkout/create-order-minimal", payload)


def push_ussd(*, order_id, phone):
    """
    Tuma kidokezo cha malipo kwenye simu ya mtu.

    Hii ndiyo faida kuu ya Selcom: mtu haondoki kwenye tovuti yetu.
    Anapokea kidokezo, anaingiza PIN, na malipo yanakamilika.
    """
    payload = {
        "transid": order_id,
        "order_id": order_id,
        "msisdn": _msisdn(phone),
    }
    return _request("/checkout/wallet-payment", payload)


def order_status(order_id):
    """
    Hali halisi ya malipo kwa Selcom.

    Hii ndiyo chanzo cha ukweli. Webhook ni ishara tu ya kuangalia —
    haitumiki peke yake kuthibitisha kuwa pesa imeingia.
    """
    payload = {"order_id": order_id}
    return _request("/checkout/order-status", payload, method="GET")


def payment_status(data):
    """
    Geuza jibu la Selcom kuwa mojawapo ya: confirmed / pending / failed.

    Selcom hutumia `payment_status` yenye COMPLETED / PENDING / REJECTED
    / USERCANCELLED. Isiyofahamika inahesabiwa kama `pending` — si
    `confirmed`. Kudhani malipo yamefanikiwa ni kosa la gharama zaidi
    kuliko kumwacha mtu asubiri uthibitisho.
    """
    rows = data.get("data") or []
    row = rows[0] if rows else data
    state = str(row.get("payment_status", "")).upper()

    if state in ("COMPLETED", "SUCCESS", "PAID"):
        return "confirmed"
    if state in ("REJECTED", "FAILED", "CANCELLED", "USERCANCELLED", "EXPIRED"):
        return "failed"
    return "pending"


def transaction_ref(data):
    """Namba ya Selcom ya muamala — kwa kumbukumbu na kufuatilia."""
    rows = data.get("data") or []
    row = rows[0] if rows else data
    return (row.get("transid") or row.get("reference") or "")[:64]


def _msisdn(phone):
    """
    Namba ya simu kwa muundo wa Selcom: 255XXXXXXXXX.

    Watu huandika kwa njia nyingi (0712..., +255712..., 255712...).
    Zote zinabadilishwa hapa badala ya kumlazimu mtu aandike kwa
    muundo mmoja.
    """
    digits = "".join(ch for ch in str(phone) if ch.isdigit())
    if digits.startswith("255"):
        return digits
    if digits.startswith("0"):
        return "255" + digits[1:]
    if len(digits) == 9:
        return "255" + digits
    return digits
