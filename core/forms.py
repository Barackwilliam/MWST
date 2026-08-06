"""Fomu zinazohifadhi data halisi."""
from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from content.models import ContactMessage
from finance.models import (Contribution, Fund, Payment, PaymentMethod,
                            PaymentStatus)
from geo.models import District, Region, Ward
from members.models import Application, Category, Member
from programs.models import EventRegistration


class BilingualChoiceField(forms.ModelChoiceField):
    """ModelChoiceField inayoonyesha jina kwa lugha inayotumika sasa."""
    def __init__(self, *args, tx_field="name", **kwargs):
        self.tx_field = tx_field
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        if hasattr(obj, "tx"):
            return obj.tx(self.tx_field)
        return str(obj)


class BootstrapMixin:
    """Weka class za design system kwenye kila field."""
    def _style(self):
        for name, field in self.fields.items():
            w = field.widget
            if isinstance(w, forms.Select):
                w.attrs.setdefault("class", "select")
            elif isinstance(w, forms.Textarea):
                w.attrs.setdefault("class", "textarea")
            elif isinstance(w, (forms.CheckboxInput, forms.RadioSelect)):
                pass
            else:
                w.attrs.setdefault("class", "input")


class ApplicationForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Application
        fields = ["full_name", "gender", "date_of_birth", "national_id", "nationality",
                  "religion", "phone", "email", "region", "district", "ward",
                  "street", "address", "category", "photo"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["region"].queryset = Region.objects.all()
        self.fields["region"].empty_label = _("Chagua Mkoa")
        self.fields["district"].queryset = District.objects.none()
        self.fields["district"].empty_label = _("Chagua Wilaya")
        self.fields["ward"].queryset = Ward.objects.none()
        self.fields["ward"].empty_label = _("Chagua Kata")
        self.fields["gender"].choices = [("", _("Chagua Jinsia"))] + list(
            self.fields["gender"].choices)[1:]
        # Tanzanite haipo hapa — ni daraja la heshima linalotolewa na msimamizi
        self.fields["category"].queryset = Category.objects.filter(is_selectable=True)
        self.fields["category"].empty_label = _("Chagua Aina ya Uanachama")

        # Vinavyohitajika ili ombi lishughulikiwe. Vingine ni vya hiari —
        # mwombaji asizuiliwe kwa kukosa kitambulisho au barua pepe.
        for name in ("gender", "date_of_birth", "region", "district"):
            self.fields[name].required = True

        self.fields["national_id"].help_text = _(
            "Si lazima sasa, lakini itahitajika kabla ya kupewa kadi")
        self.fields["email"].help_text = _(
            "Si lazima. Ikiwepo, utapokea risiti na taarifa kwa barua pepe")
        self.fields["photo"].help_text = _("JPEG au PNG, chini ya MB 2")

        data = self.data or {}
        region_id = data.get("region") or getattr(self.instance, "region_id", None)
        if region_id:
            self.fields["district"].queryset = District.objects.filter(region_id=region_id)
        district_id = data.get("district") or getattr(self.instance, "district_id", None)
        if district_id:
            self.fields["ward"].queryset = Ward.objects.filter(district_id=district_id)
        self._style()

    def clean_phone(self):
        """Namba ya simu ya Tanzania: 07XXXXXXXX au +2557XXXXXXXX."""
        from core.mixins import normalize_phone
        digits = normalize_phone(self.cleaned_data["phone"])
        if not (len(digits) == 10 and digits.startswith("0")):
            raise forms.ValidationError(
                _("Weka namba sahihi ya simu, mfano 0712 345 678."))
        return digits

    def clean_date_of_birth(self):
        """Umri wa chini ni miaka 18."""
        from django.utils import timezone
        dob = self.cleaned_data["date_of_birth"]
        today = timezone.localdate()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 18:
            raise forms.ValidationError(
                _("Mwombaji lazima awe na umri wa miaka 18 au zaidi."))
        if age > 120:
            raise forms.ValidationError(_("Hakikisha tarehe ya kuzaliwa ni sahihi."))
        return dob

    def clean(self):
        """
        Zuia maombi yanayorudiwa.

        Mtu akibonyeza "Tuma" mara mbili, au akirudia fomu, hatuzalishi
        maombi mengi. Pia tunamzuia aliyekwisha kuwa mwanachama.
        """
        cleaned = super().clean()
        phone = cleaned.get("phone")
        nid = (cleaned.get("national_id") or "").strip()
        if not phone or self.instance.pk:
            return cleaned

        from members.models import Application, ApplicationStatus, Member

        if Member.objects.filter(phone=phone).exists() or (
                nid and Member.objects.filter(national_id=nid).exists()):
            raise forms.ValidationError(_(
                "Namba hii tayari ni ya mwanachama. Kama umesahau namba yako "
                "ya uanachama, wasiliana nasi."))

        pending = Application.objects.filter(
            phone=phone,
            status__in=[ApplicationStatus.PENDING, ApplicationStatus.REVIEW],
        ).first()
        if pending:
            raise forms.ValidationError(_(
                "Tayari una ombi linalosubiri, namba %(ref)s. Tutawasiliana "
                "nawe hivi karibuni."
            ) % {"ref": pending.reference})
        return cleaned

    def clean_national_id(self):
        """Kitambulisho kisirudiwe."""
        nid = (self.cleaned_data.get("national_id") or "").strip()
        if not nid:
            return nid
        from members.models import Member
        clash = Member.objects.filter(national_id=nid)
        if clash.exists():
            raise forms.ValidationError(
                _("Namba hii ya kitambulisho tayari imesajiliwa."))
        return nid


class ContactForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["full_name", "phone", "email", "subject", "body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 5})}

    SUBJECTS = ["Uanachama", "Michango na Malipo", "Msaada wa Ustawi",
                "Ushirikiano na Udhamini", "Malalamiko", "Nyingine"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subject"] = forms.ChoiceField(
            label=_("Mada"), choices=[(s, s) for s in self.SUBJECTS])
        self._style()


class PaymentForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["member", "amount", "year", "period_month", "method",
                  "bank_name", "reference", "status", "paid_at"]
        widgets = {"paid_at": forms.DateTimeInput(attrs={"type": "datetime-local"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["member"].queryset = Member.objects.order_by("full_name")
        self._style()

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError(_("Kiasi lazima kiwe zaidi ya sifuri."))
        return amount


class ContributionForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ["fund", "donor_name", "member", "donor", "project", "campaign",
                  "amount", "method", "bank_name", "reference", "status", "note", "received_at"]
        widgets = {"received_at": forms.DateTimeInput(attrs={"type": "datetime-local"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fund"].queryset = Fund.objects.exclude(code="ada")
        self.fields["member"].queryset = Member.objects.order_by("full_name")
        self.fields["member"].required = False
        self._style()

    def clean(self):
        cleaned = super().clean()
        if not (cleaned.get("member") or cleaned.get("donor") or cleaned.get("donor_name")):
            raise forms.ValidationError(
                _("Weka mwanachama, mhisani au jina la mchangiaji."))
        return cleaned


class EventRegistrationForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ["full_name", "phone", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


class AssistanceForm(BootstrapMixin, forms.Form):
    from programs.models import AssistanceType
    assistance_type = BilingualChoiceField(
        label=_("Aina ya Msaada"), queryset=AssistanceType.objects.all())
    amount_requested = forms.DecimalField(label=_("Kiasi"), min_value=0, decimal_places=2)
    description = forms.CharField(label=_("Maelezo"), widget=forms.Textarea(attrs={"rows": 4}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


class ProfileForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Member
        fields = ["full_name", "phone", "email", "occupation", "region",
                  "district", "ward", "street", "address", "photo"]
        widgets = {"address": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.region_id:
            self.fields["district"].queryset = District.objects.filter(
                region_id=self.instance.region_id)
        if self.instance and self.instance.district_id:
            self.fields["ward"].queryset = Ward.objects.filter(
                district_id=self.instance.district_id)
        self._style()


# ===========================================================================
#  FOMU ZA MWANACHAMA (huduma binafsi)
# ===========================================================================
class MemberPaymentForm(BootstrapMixin, forms.Form):
    """Mwanachama kulipa ada yake mwenyewe."""
    amount = forms.DecimalField(label=_("Kiasi (TZS)"), min_value=1, decimal_places=2)
    period_month = forms.ChoiceField(label=_("Mwezi"), choices=[
        (i, m) for i, m in enumerate(
            ["Januari", "Februari", "Machi", "Aprili", "Mei", "Juni", "Julai",
             "Agosti", "Septemba", "Oktoba", "Novemba", "Desemba"], start=1)])
    method = forms.ChoiceField(label=_("Njia ya Malipo"), choices=PaymentMethod.choices)
    reference = forms.CharField(label=_("Namba ya Muamala"), max_length=80, required=False,
                                help_text=_("Kama umelipa kwa simu, weka namba ya uthibitisho"))

    def __init__(self, *args, member=None, **kwargs):
        super().__init__(*args, **kwargs)
        if member:
            self.fields["amount"].initial = member.category.monthly_fee
        from django.utils import timezone
        self.fields["period_month"].initial = timezone.localdate().month
        self._style()

    def save(self, member):
        """Malipo yanaingia yakiwa 'pending' hadi afisa athibitishe."""
        return Payment.objects.create(
            member=member,
            amount=self.cleaned_data["amount"],
            period_month=int(self.cleaned_data["period_month"]),
            method=self.cleaned_data["method"],
            reference=self.cleaned_data["reference"],
            status=PaymentStatus.PENDING,
        )


class MemberContributionForm(BootstrapMixin, forms.Form):
    """Mwanachama kutoa mchango."""
    fund = BilingualChoiceField(label=_("Aina ya Mchango"), queryset=Fund.objects.none())
    project = BilingualChoiceField(label=_("Mradi (si lazima)"), required=False,
                                   queryset=None, tx_field="title")
    amount = forms.DecimalField(label=_("Kiasi (TZS)"), min_value=1, decimal_places=2)
    method = forms.ChoiceField(label=_("Njia ya Malipo"), choices=PaymentMethod.choices)
    reference = forms.CharField(label=_("Namba ya Muamala"), max_length=80, required=False)
    note = forms.CharField(label=_("Maelezo"), max_length=200, required=False)

    def __init__(self, *args, **kwargs):
        from finance.models import Project
        super().__init__(*args, **kwargs)
        self.fields["fund"].queryset = Fund.objects.exclude(code="ada")
        self.fields["project"].queryset = Project.objects.filter(status="ongoing")
        self.fields["project"].empty_label = _("Uendeshaji wa jumla")
        self._style()

    def save(self, member):
        c = Contribution.objects.create(
            member=member, fund=self.cleaned_data["fund"],
            project=self.cleaned_data["project"], amount=self.cleaned_data["amount"],
            method=self.cleaned_data["method"], reference=self.cleaned_data["reference"],
            note=self.cleaned_data["note"], status=PaymentStatus.PENDING,
        )
        return c


class FamilyMemberForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        from members.models import FamilyMember
        model = FamilyMember
        fields = ["full_name", "relationship", "date_of_birth", "gender", "phone"]
        widgets = {"date_of_birth": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["gender"] = forms.ChoiceField(
            label=_("Jinsia"), required=False,
            choices=[("", "—"), ("male", _("Mwanaume")), ("female", _("Mwanamke"))])
        self._style()


class BeneficiaryForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        from members.models import Beneficiary
        model = Beneficiary
        fields = ["full_name", "relationship", "phone", "percentage_share"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


class MediaUploadForm(BootstrapMixin, forms.ModelForm):
    """Kupakia picha au video kwenye maktaba ya media."""
    class Meta:
        from content.models import MediaItem
        model = MediaItem
        fields = ["title", "title_en", "kind", "category", "album", "file", "duration"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title_en"].label = _("Kichwa kwa Kiingereza")
        self.fields["title_en"].required = False
        self.fields["duration"].required = False
        self.fields["file"].required = True
        self._style()

    def clean_file(self):
        f = self.cleaned_data["file"]
        limit = 25 * 1024 * 1024
        if f.size > limit:
            raise forms.ValidationError(_("Faili ni kubwa mno. Kiwango cha juu ni MB 25."))
        return f

    def save(self, commit=True, user=None):
        obj = super().save(commit=False)
        f = self.cleaned_data["file"]
        obj.size_mb = round(f.size / (1024 * 1024), 1)
        if user is not None:
            obj.uploaded_by = user
        if commit:
            obj.save()
        return obj


class BroadcastForm(BootstrapMixin, forms.Form):
    """
    Kutuma ujumbe kwa wanachama.

    Arifa za ndani zinafika mara moja. Barua pepe zinatumwa kama `EMAIL_HOST`
    imewekwa. SMS inahitaji gateway — bado haijaunganishwa, kwa hiyo ujumbe
    unahifadhiwa kwenye foleni.
    """
    CHANNELS = [("app", _("Arifa ya Ndani")), ("email", _("Barua Pepe")), ("sms", "SMS")]
    AUDIENCE = [
        ("all", _("Wanachama wote")),
        ("active", _("Wanachama hai pekee")),
        ("category", _("Kategoria maalum")),
        ("region", _("Mkoa maalum")),
        ("arrears", _("Waliochelewa kulipa")),
    ]

    channel = forms.MultipleChoiceField(
        label=_("Njia"), choices=CHANNELS, initial=["app"],
        widget=forms.CheckboxSelectMultiple)
    audience = forms.ChoiceField(label=_("Wapokeaji"), choices=AUDIENCE)
    category = forms.ModelChoiceField(label=_("Kategoria"), required=False,
                                      queryset=Category.objects.all())
    region = forms.ModelChoiceField(label=_("Mkoa"), required=False,
                                    queryset=Region.objects.all())
    subject = forms.CharField(label=_("Mada"), max_length=180)
    body = forms.CharField(label=_("Ujumbe"), widget=forms.Textarea(attrs={"rows": 6}),
                           help_text=_("Tumia {jina} na {namba} kubadilishwa na taarifa "
                                       "za kila mwanachama"))

    def __init__(self, *args, region_ids=None, **kwargs):
        super().__init__(*args, **kwargs)
        if region_ids is not None:
            self.fields["region"].queryset = Region.objects.filter(pk__in=region_ids)
        self._style()

    def clean(self):
        cleaned = super().clean()
        aud = cleaned.get("audience")
        if aud == "category" and not cleaned.get("category"):
            self.add_error("category", _("Chagua kategoria."))
        if aud == "region" and not cleaned.get("region"):
            self.add_error("region", _("Chagua mkoa."))
        return cleaned

    def recipients(self, region_ids=None):
        """Wanachama watakaopokea ujumbe."""
        from members.models import MemberStatus
        qs = Member.objects.select_related("category", "region")
        if region_ids is not None:
            qs = qs.filter(region_id__in=region_ids)

        aud = self.cleaned_data["audience"]
        if aud == "active":
            qs = qs.filter(status=MemberStatus.ACTIVE)
        elif aud == "category":
            qs = qs.filter(category=self.cleaned_data["category"])
        elif aud == "region":
            qs = qs.filter(region=self.cleaned_data["region"])
        elif aud == "arrears":
            from django.utils import timezone
            from finance.models import PaymentStatus as PS
            cutoff = timezone.localdate() - timezone.timedelta(days=45)
            paid = Payment.objects.filter(
                status=PS.CONFIRMED, paid_at__date__gte=cutoff
            ).values_list("member_id", flat=True)
            qs = qs.filter(status=MemberStatus.ACTIVE).exclude(pk__in=paid)
        return qs


class MemberEditForm(BootstrapMixin, forms.ModelForm):
    """
    Afisa kuhariri taarifa za mwanachama.

    Madaraja maalum (Tanzanite) yanaonekana kwa msimamizi pekee. Afisa wa
    kawaida hawezi kumpandisha mwanachama huko.
    """
    class Meta:
        model = Member
        fields = ["full_name", "gender", "date_of_birth", "national_id", "nationality",
                  "religion", "occupation", "phone", "email", "region", "district",
                  "ward", "street", "address", "category", "status", "expires_on"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "expires_on": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, can_assign_special=False, **kwargs):
        super().__init__(*args, **kwargs)
        cats = Category.objects.all()
        if not can_assign_special:
            # Ruhusu daraja la sasa libaki hata kama ni maalum, ili kuhariri
            # taarifa nyingine kusifute daraja alilonalo.
            current = getattr(self.instance, "category_id", None)
            cats = cats.filter(Q(is_selectable=True) | Q(pk=current))
        self.fields["category"].queryset = cats

        data = self.data or {}
        region_id = data.get("region") or getattr(self.instance, "region_id", None)
        self.fields["district"].queryset = (District.objects.filter(region_id=region_id)
                                            if region_id else District.objects.none())
        district_id = data.get("district") or getattr(self.instance, "district_id", None)
        self.fields["ward"].queryset = (Ward.objects.filter(district_id=district_id)
                                        if district_id else Ward.objects.none())
        self._style()


# ===========================================================================
#  MICHANGO YA UMMA NA AKAUNTI YA MHISANI
# ===========================================================================
class PublicDonationForm(BootstrapMixin, forms.ModelForm):
    """
    Fomu ya kuchangia bila kuwa na akaunti.

    Mchango unahifadhiwa kama `pending` — afisa wa michango ndiye
    anayethibitisha baada ya kuona pesa imeingia. Hakuna kitu kinachoingia
    kwenye leja mpaka hapo.
    """
    full_name = forms.CharField(label=_("Jina lako kamili"), max_length=160)
    phone = forms.CharField(label=_("Namba ya simu"), max_length=24)
    email = forms.EmailField(label=_("Barua pepe"), required=False)
    anonymous = forms.BooleanField(
        label=_("Nataka kuchangia bila jina langu kuonekana hadharani"),
        required=False)

    class Meta:
        model = Contribution
        fields = ["fund", "amount", "method", "reference", "note"]
        widgets = {"note": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fund"] = BilingualChoiceField(
            label=_("Mfuko"), queryset=Fund.objects.exclude(code="ada").order_by("order"),
            empty_label=None)
        self.fields["amount"].label = _("Kiasi (TSh)")
        self.fields["method"].label = _("Njia ya malipo")
        self.fields["reference"].label = _("Namba ya muamala")
        self.fields["reference"].help_text = _(
            "Ukiwa tayari umelipa, weka namba ya risiti ya M-Pesa, Airtel, "
            "Tigo Pesa, HaloPesa au benki. Inaharakisha uthibitisho.")
        self.fields["reference"].required = False
        self.fields["note"].label = _("Ujumbe (hiari)")
        self.fields["note"].required = False
        self._style()

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError(_("Kiasi lazima kiwe zaidi ya sifuri."))
        return amount

    def clean_phone(self):
        phone = "".join(ch for ch in self.cleaned_data["phone"] if ch.isdigit() or ch == "+")
        if len(phone.lstrip("+")) < 9:
            raise forms.ValidationError(_("Weka namba kamili ya simu."))
        return phone


class DonorSignupForm(BootstrapMixin, forms.Form):
    """
    Akaunti ya mhisani — huundwa BAADA ya kuchangia, si kabla.

    Lengo lake ni moja tu: kutunza kumbukumbu za michango ya mtu mmoja
    mahali pamoja. Haitoi ufikiaji wowote wa dashibodi za watumishi.
    """
    full_name = forms.CharField(label=_("Jina kamili"), max_length=160)
    email = forms.EmailField(label=_("Barua pepe"))
    phone = forms.CharField(label=_("Namba ya simu"), max_length=24)
    password1 = forms.CharField(label=_("Nenosiri"), widget=forms.PasswordInput,
                                min_length=8)
    password2 = forms.CharField(label=_("Rudia nenosiri"), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].help_text = _("Angalau herufi 8.")
        self._style()

    def clean_email(self):
        from django.contrib.auth import get_user_model
        email = self.cleaned_data["email"].strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                _("Barua pepe hii tayari ina akaunti. Tumia \"Ingia\" badala yake."))
        return email

    def clean(self):
        data = super().clean()
        if data.get("password1") and data.get("password1") != data.get("password2"):
            self.add_error("password2", _("Nenosiri hazifanani."))
        return data
