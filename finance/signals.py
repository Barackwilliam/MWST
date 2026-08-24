"""
Signals za fedha.

Malipo au mchango ukibadilishwa kuwa `confirmed` popote — kwenye admin,
kwenye form, au kwenye script — leja inaingizwa moja kwa moja.
`post_to_ledger()` ina ulinzi wa kutorudia, kwa hiyo si hatari kuiita mara nyingi.

Arifa za SMS nazo zinatoka hapa kwa sababu ile ile: hatujali malipo
yametoka Pesapal, Selcom, au afisa amethibitisha kwa mkono — mtu
anapaswa kupata risiti kwa njia zote.
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Contribution, Payment, PaymentStatus

log = logging.getLogger(__name__)


def _phone(obj):
    """Namba ya kumjulisha: ya mwanachama, ya ombi, au ya mtoaji."""
    if obj.member_id and obj.member.phone:
        return obj.member.phone
    if getattr(obj, "application_id", None) and obj.application.phone:
        return obj.application.phone
    return (getattr(obj, "donor_phone", "") or "").strip()


def _receipt_sms(gift):
    """
    Risiti kwa SMS. Inatumwa MARA MOJA tu kwa kila malipo.

    Kutuma kunafanyika kwa `try` kwa sababu signal hii inaendeshwa ndani
    ya muamala wa malipo. Kosa la SMS lisirudishe nyuma malipo halisi —
    pesa tayari imeingia.
    """
    if gift.sms_sent:
        return
    phone = _phone(gift)
    if not phone:
        return

    try:
        from core import sms
        from core.data import giving

        if gift.purpose == "uhuisho":
            member = gift.member
            if member and member.expires_on:
                sms.send_renewal_done(phone, member.expires_on)
        elif gift.purpose == "ada":
            sms.send_fee_receipt(phone, int(gift.amount), gift.receipt_no,
                                 gift.months or 0)
        else:
            spec = giving.purpose(gift.purpose)
            sms.send_contribution_receipt(
                phone, int(gift.amount), gift.receipt_no,
                spec["name"] if spec else "")
    except Exception:
        log.exception("Risiti ya SMS ya %s haikutumwa", gift.receipt_no)
        return

    gift.sms_sent = True
    gift.save(update_fields=["sms_sent", "updated_at"])


def _failed_sms(gift):
    """
    Mjulishe kwamba malipo hayakukamilika.

    Muhimu kuliko inavyoonekana: mtu asiyeambiwa hajui kama pesa yake
    imekatwa, na huweza kulipa mara ya pili bila sababu.
    """
    if gift.sms_sent:
        return
    phone = _phone(gift)
    if not phone:
        return
    try:
        from core import sms
        sms.send_payment_failed(phone, int(gift.amount))
    except Exception:
        log.exception("Arifa ya malipo yasiyokamilika %s haikutumwa",
                      gift.receipt_no)
        return
    gift.sms_sent = True
    gift.save(update_fields=["sms_sent", "updated_at"])


@receiver(post_save, sender=Payment)
def payment_posted(sender, instance, **kwargs):
    if instance.status == PaymentStatus.CONFIRMED and instance.ledger_entry_id is None:
        instance.post_to_ledger()


@receiver(post_save, sender=Contribution)
def contribution_posted(sender, instance, **kwargs):
    if instance.status in (PaymentStatus.FAILED, PaymentStatus.CANCELLED):
        _failed_sms(instance)
        return
    if instance.status != PaymentStatus.CONFIRMED:
        return

    # Malipo ya uanachama hubadilisha hali ya mtu — humfanya mwombaji
    # kuwa mwanachama, au humhuishia kipindi. Michango ya mwezi ("ada")
    # HAIGUSI muda; inaingia leja tu kama mchango mwingine wowote.
    # Hii lazima ije kwanza kwa sababu ndiyo inayoweza kuweka `member`
    # kwenye malipo ya ombi jipya, na leja inahitaji `member`.
    if instance.purpose in ("ada", "uhuisho"):
        instance.apply_membership()
    if instance.ledger_entry_id is None and instance.member_id:
        instance.post_to_ledger()

    # Risiti mwishoni — ikitangulia, `apply_membership` isingekuwa
    # imeweka tarehe mpya wala mwanachama.
    instance.refresh_from_db()
    _receipt_sms(instance)
