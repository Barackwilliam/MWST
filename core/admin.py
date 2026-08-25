"""Usajili wa `core` kwenye Django admin."""
from django.contrib import admin

from .models import Sequence


@admin.register(Sequence)
class SequenceAdmin(admin.ModelAdmin):
    """
    Hesabu za namba za mfululizo (maombi, wanachama, risiti).

    ONYO: kupunguza `value` hapa kunasababisha namba kujirudia — mfano
    maombi mawili yenye `APP/MUWESTA/2026/0021`. Ipo kwa kuangalia;
    ibadilishwe pale tu kitu kimeharibika kweli.
    """
    list_display = ("key", "value")
    search_fields = ("key",)
    readonly_fields = ("key",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
