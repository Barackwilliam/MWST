"""Vipengele vinavyotumika kwenye models zote."""
from django.db import models
from django.utils import timezone
from django.utils.translation import get_language


def normalize_phone(raw):
    """
    Muundo mmoja wa namba za simu: 0712345678.

    Inakubali 0712 345 678, +255712345678, 255-712-345-678 na kuzigeuza
    zote kuwa muundo mmoja. Bila hii, kutafuta au kulinganisha namba
    kunashindwa kwa sababu ya nafasi na vistari.
    """
    if not raw:
        return ""
    digits = "".join(ch for ch in str(raw) if ch.isdigit())
    if digits.startswith("255"):
        digits = "0" + digits[3:]
    elif digits.startswith("7") or digits.startswith("6"):
        digits = "0" + digits
    return digits


class Bilingual(models.Model):
    """
    Model yenye maudhui ya Kiswahili na Kiingereza.

    Kila field inayotafsirika ina toleo la `_en`. Tumia `.tx("title")`
    kupata thamani kwa lugha inayotumika sasa.
    """
    class Meta:
        abstract = True

    def tx(self, field):
        lang = (get_language() or "sw").lower()
        if lang.startswith("en"):
            val = getattr(self, f"{field}_en", "") or ""
            if val:
                return val
        return getattr(self, field, "") or ""


class TimeStamped(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Sequence(models.Model):
    """
    Kihesabu salama cha namba za mfululizo (namba za uanachama, risiti n.k.).
    Hutumika pamoja na select_for_update ili kuzuia namba pacha.
    """
    key = models.CharField(max_length=64, unique=True)
    value = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "core_sequence"

    def __str__(self):
        return f"{self.key} = {self.value}"

    @classmethod
    def next(cls, key):
        """Rudisha namba inayofuata kwa usalama (lazima iwe ndani ya transaction)."""
        obj, _ = cls.objects.select_for_update().get_or_create(key=key)
        obj.value += 1
        obj.save(update_fields=["value"])
        return obj.value
