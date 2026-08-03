"""
Kupakua ripoti kama CSV.

CSV inafunguka moja kwa moja kwenye Excel na haihitaji library yoyote ya ziada.
BOM ya UTF-8 imewekwa ili herufi za Kiswahili zisiharibike Excel ikifungua.
"""
import csv

from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import gettext as _


def csv_response(filename, headers, rows):
    """Tengeneza faili ya CSV inayoweza kupakuliwa."""
    stamp = timezone.localdate().strftime("%Y%m%d")
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}-{stamp}.csv"'
    response.write("\ufeff")          # BOM kwa ajili ya Excel
    writer = csv.writer(response)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return response


def payments_csv(qs):
    return csv_response(
        "malipo",
        [_("Risiti"), _("Namba ya Mwanachama"), _("Jina"), _("Aina ya Uanachama"),
         _("Kiasi"), _("Mwezi"), _("Mwaka"), _("Njia"), _("Kumbukumbu"),
         _("Tarehe"), _("Hali")],
        [[p.receipt_no, p.member.membership_no, p.member.full_name,
          p.member.category.name, p.amount, p.period_month or "", p.year,
          p.get_method_display(), p.reference,
          p.paid_at.strftime("%Y-%m-%d %H:%M"), p.get_status_display()]
         for p in qs.select_related("member", "member__category")],
    )


def contributions_csv(qs):
    return csv_response(
        "michango",
        [_("Risiti"), _("Mchangiaji"), _("Namba ya Mwanachama"), _("Aina"),
         _("Kiasi"), _("Mradi"), _("Njia"), _("Tarehe"), _("Hali")],
        [[c.receipt_no, c.display_name,
          c.member.membership_no if c.member else "", c.fund.name, c.amount,
          c.project.title if c.project else "", c.get_method_display(),
          c.received_at.strftime("%Y-%m-%d %H:%M"), c.get_status_display()]
         for c in qs.select_related("fund", "member", "donor", "project")],
    )


def members_csv(qs):
    return csv_response(
        "wanachama",
        [_("Namba ya Mwanachama"), _("Namba ya Akaunti"), _("Jina Kamili"),
         _("Jinsia"), _("Simu"), _("Barua Pepe"), _("Kitambulisho"),
         _("Aina ya Uanachama"), _("Mkoa"), _("Wilaya"), _("Tarehe ya Usajili"), _("Hali")],
        [[m.membership_no, m.account_no, m.full_name, m.get_gender_display() or "",
          m.phone, m.email, m.national_id, m.category.name,
          m.region.name if m.region else "", m.district.name if m.district else "",
          m.joined_on, m.get_status_display()]
         for m in qs.select_related("category", "region", "district")],
    )


def applications_csv(qs):
    return csv_response(
        "maombi",
        [_("Namba ya Maombi"), _("Jina Kamili"), _("Simu"), _("Barua Pepe"),
         _("Aina ya Uanachama"), _("Mkoa"), _("Wilaya"), _("Tarehe"), _("Hali")],
        [[a.reference, a.full_name, a.phone, a.email, a.category.name,
          a.region.name if a.region else "", a.district.name if a.district else "",
          a.created_at.strftime("%Y-%m-%d"), a.get_status_display()]
         for a in qs.select_related("category", "region", "district")],
    )


def donors_csv(qs):
    return csv_response(
        "wahisani",
        [_("Jina"), _("Aina"), _("Mkoa"), _("Simu"), _("Barua Pepe"),
         _("Ni mdau"), _("Jumla Aliyotoa")],
        [[d.name, d.get_donor_type_display(), d.region.name if d.region else "",
          d.phone, d.email, _("Ndiyo") if d.is_partner else _("Hapana"),
          d.total_given()] for d in qs.select_related("region")],
    )


def events_csv(qs):
    return csv_response(
        "matukio",
        [_("Tukio"), _("Aina"), _("Mahali"), _("Ukumbi"), _("Kuanza"),
         _("Hali"), _("Washiriki")],
        [[e.title, e.event_type.name, e.region.name if e.region else "", e.venue,
          e.start_at.strftime("%Y-%m-%d %H:%M"), e.get_status_display(),
          e.participant_count()]
         for e in qs.select_related("event_type", "region")],
    )


def regions_csv(region_ids=None):
    from django.db.models import Count
    from geo.models import Region, Ward
    from members.models import Member
    counts = {r["region_id"]: r["n"] for r in
              Member.objects.values("region_id").annotate(n=Count("id"))}
    qs = Region.objects.select_related("zone")
    if region_ids is not None:
        qs = qs.filter(pk__in=region_ids)
    return csv_response(
        "mikoa",
        [_("Mkoa"), _("Kanda"), _("Idadi ya Wanachama"),
         _("Halmashauri"), _("Kata")],
        [[r.name, r.zone.name if r.zone else "", counts.get(r.pk, 0),
          r.districts.count(), Ward.objects.filter(district__region=r).count()]
         for r in qs],
    )


def zones_csv():
    from django.db.models import Count
    from geo.models import Zone
    from members.models import Member
    counts = {r["region__zone_id"]: r["n"] for r in
              Member.objects.values("region__zone_id").annotate(n=Count("id"))}
    return csv_response(
        "kanda",
        [_("Kanda"), _("Mratibu"), _("Ofisi"), _("Mikoa"), _("Idadi ya Wanachama")],
        [[z.name, z.coordinator.get_full_name() if z.coordinator else "",
          z.office, ", ".join(z.regions.values_list("name", flat=True)),
          counts.get(z.pk, 0)]
         for z in Zone.objects.select_related("coordinator").prefetch_related("regions")],
    )
