"""
Mteja wa Pesapal API 3.0.

Mtiririko:
    1. RequestToken      -> bearer token (inaisha baada ya dakika 5)
    2. RegisterIPNURL    -> ipn_id (mara moja tu; hifadhi kwenye env)
    3. SubmitOrderRequest-> redirect_url + order_tracking_id
    4. Mtumiaji analipa kwenye ukurasa wa Pesapal
    5. Pesapal inampeleka kwenye callback_url YETU, na pia inapiga IPN
    6. GetTransactionStatus -> hali halisi ya malipo

MUHIMU KUHUSU USALAMA
---------------------
* `consumer_key` na `consumer_secret` HAZIANDIKWI kwenye code. Zinatoka
  kwenye environment variables. Zikiwekwa kwenye faili, zitaishia kwenye
  git history na hazitatoka tena.
* Callback PEKEE haitoshi kuthibitisha malipo — mtu anaweza kuiita mwenyewe
  kwenye kivinjari. Hali halisi HULAZIMA ithibitishwe kwa
  `GetTransactionStatus`, na ndivyo tunavyofanya.
* Namba za kadi hazipiti kwenye seva zetu hata kidogo. Mtumiaji analipia
  kwenye ukurasa wa Pesapal.
"""
import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

log = logging.getLogger(__name__)

SANDBOX = "https://cybqa.pesapal.com/pesapalv3"
LIVE = "https://pay.pesapal.com/v3"

TOKEN_CACHE_KEY = "pesapal:token"
#: Token huisha baada ya dakika 5; tunaihifadhi kwa 4 ili tusikutane na ukingo.
TOKEN_TTL = 4 * 60


class PesapalError(Exception):
    """Kosa lolote linalotoka Pesapal au kwenye mawasiliano nayo."""


def _base():
    env = getattr(settings, "PESAPAL_ENV", "sandbox").lower()
    return LIVE if env in ("live", "production") else SANDBOX


def is_configured():
    return bool(getattr(settings, "PESAPAL_CONSUMER_KEY", "")
                and getattr(settings, "PESAPAL_CONSUMER_SECRET", ""))


def _post(path, payload, token=None, method="POST"):
    url = f"{_base()}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:500]
        log.error("Pesapal %s -> HTTP %s: %s", path, exc.code, detail)
        raise PesapalError(f"Pesapal HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        log.error("Pesapal %s -> %s", path, exc)
        raise PesapalError("Pesapal haipatikani kwa sasa") from exc

    # Pesapal hurudisha 200 hata kwenye makosa; kosa lipo ndani ya `error`.
    err = body.get("error")
    if err:
        if isinstance(err, dict):
            # Pesapal mara nyingi huacha `message` tupu na kuweka maelezo
            # kwenye `code` pekee (mf. invalid_consumer_key_or_secret_provided).
            message = err.get("message") or err.get("code") or ""
        else:
            message = str(err)
        log.error("Pesapal %s -> %s", path, message)
        raise PesapalError(message or "Kosa kutoka Pesapal")
    return body


def token(force=False):
    """Bearer token, ikihifadhiwa kwa dakika 4."""
    if not force:
        cached = cache.get(TOKEN_CACHE_KEY)
        if cached:
            return cached

    body = _post("/api/Auth/RequestToken", {
        "consumer_key": settings.PESAPAL_CONSUMER_KEY,
        "consumer_secret": settings.PESAPAL_CONSUMER_SECRET,
    })
    value = body.get("token")
    if not value:
        raise PesapalError("Pesapal haikurudisha token")
    cache.set(TOKEN_CACHE_KEY, value, TOKEN_TTL)
    return value


def register_ipn(url, method="POST"):
    """
    Sajili IPN URL. Hufanywa MARA MOJA; hifadhi `ipn_id` kwenye
    PESAPAL_IPN_ID ili isirudiwe kila mara.
    """
    body = _post("/api/URLSetup/RegisterIPN",
                 {"url": url, "ipn_notification_type": method},
                 token=token())
    return body.get("ipn_id")


def list_ipns():
    return _post("/api/URLSetup/GetIpnList", None, token=token(), method="GET")


def submit_order(*, merchant_reference, amount, description, callback_url,
                 currency="TZS", first_name="", last_name="", email="", phone="",
                 country_code="TZ"):
    """
    Anzisha malipo. Hurudisha `(order_tracking_id, redirect_url)`.

    `merchant_reference` ni namba yetu ya risiti — ndiyo tutakayotumia
    kuunganisha jibu la Pesapal na rekodi yetu.
    """
    ipn_id = getattr(settings, "PESAPAL_IPN_ID", "")
    if not ipn_id:
        raise PesapalError(
            "PESAPAL_IPN_ID haijawekwa. Endesha `manage.py pesapal_ipn` kwanza.")

    billing = {"country_code": country_code}
    if email:
        billing["email_address"] = email
    if phone:
        billing["phone_number"] = phone
    if first_name:
        billing["first_name"] = first_name
    if last_name:
        billing["last_name"] = last_name

    body = _post("/api/Transactions/SubmitOrderRequest", {
        "id": merchant_reference,
        "currency": currency,
        "amount": float(amount),
        "description": description[:100],
        "callback_url": callback_url,
        "notification_id": ipn_id,
        "billing_address": billing,
    }, token=token())

    tracking = body.get("order_tracking_id")
    redirect = body.get("redirect_url")
    if not tracking or not redirect:
        raise PesapalError("Pesapal haikurudisha redirect_url")
    return tracking, redirect


def transaction_status(order_tracking_id):
    """
    Hali halisi ya malipo. HII ndiyo chanzo cha ukweli — si callback.

    Hurudisha dict yenye `status_code` (0=INVALID, 1=COMPLETED, 2=FAILED,
    3=REVERSED) pamoja na `payment_status_description`.
    """
    query = urllib.parse.urlencode({"orderTrackingId": order_tracking_id})
    return _post(f"/api/Transactions/GetTransactionStatus?{query}", None,
                 token=token(), method="GET")


#: Ramani ya hali za Pesapal kwenda hali zetu.
STATUS_MAP = {1: "confirmed", 2: "failed", 3: "reversed", 0: "pending"}


def map_status(body):
    try:
        code = int(body.get("status_code", 0))
    except (TypeError, ValueError):
        code = 0
    return STATUS_MAP.get(code, "pending")
