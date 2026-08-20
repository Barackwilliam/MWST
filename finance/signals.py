"""
Signals za fedha.

Malipo au mchango ukibadilishwa kuwa `confirmed` popote — kwenye admin,
kwenye form, au kwenye script — leja inaingizwa moja kwa moja.
`post_to_ledger()` ina ulinzi wa kutorudia, kwa hiyo si hatari kuiita mara nyingi.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Contribution, Payment, PaymentStatus


@receiver(post_save, sender=Payment)
def payment_posted(sender, instance, **kwargs):
    if instance.status == PaymentStatus.CONFIRMED and instance.ledger_entry_id is None:
        instance.post_to_ledger()


@receiver(post_save, sender=Contribution)
def contribution_posted(sender, instance, **kwargs):
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
