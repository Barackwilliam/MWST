"""Wanachama, maombi ya uanachama, kadi na familia."""
import secrets

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.mixins import Bilingual, Sequence, TimeStamped, normalize_phone


#: Aina za vitambulisho vinavyokubalika. NIDA ndiyo ya kawaida, lakini
#: si kila mtu anayo — kuwabana wote kwenye NIDA kunazuia watu kujiunga.
ID_TYPES = [
    ("nida", _("NIDA")),
    ("driving", _("Leseni ya Udereva")),
    ("voter", _("Kadi ya Mpiga Kura")),
    ("passport", _("Pasipoti")),
    ("employee", _("Kitambulisho cha Kazi")),
    ("membership", _("Kitambulisho Kingine cha Uanachama")),
]


class Category(Bilingual):
    """Bronze, Silver, Gold, Diamond, Founder."""
    name = models.CharField(_("Jina"), max_length=40, unique=True)
    name_en = models.CharField(max_length=40, blank=True)
    code = models.CharField(_("Herufi"), max_length=1, unique=True,
                            help_text="B, S, G, P, F — inatumika kwenye namba ya uanachama")
    monthly_fee = models.DecimalField(_("Ada ya mwezi"), max_digits=12, decimal_places=2, default=0)
    # --- Mpangilio wa kifurushi (unaonyeshwa kwenye ukurasa wa Vifurushi) ---
    registration_fee = models.DecimalField(
        _("Ada ya usajili"), max_digits=12, decimal_places=2, default=0,
        help_text=_("Hulipwa mara moja tu wakati wa kujiunga."))
    annual_fee = models.DecimalField(
        _("Ada ya mwaka"), max_digits=12, decimal_places=2, default=0,
        help_text=_("Hulipwa kila mwaka."))
    duration_years = models.PositiveSmallIntegerField(_("Muda wa uanachama (miaka)"), default=3)
    recognition_points = models.PositiveIntegerField(_("Alama za utambuzi"), default=0)
    points_plus = models.BooleanField(
        _("Alama ni za chini kabisa"), default=False,
        help_text=_("Ikiwashwa, alama zitaonyeshwa kama \"2,000+\"."))
    has_card = models.BooleanField(_("Kadi ya uanachama"), default=True)
    has_events = models.BooleanField(_("Matukio na mafunzo"), default=True)
    has_reports = models.BooleanField(_("Ripoti na taarifa"), default=True)
    has_priority = models.BooleanField(_("Huduma za kipaumbele"), default=False)
    has_certificate = models.BooleanField(_("Cheti cha shukrani"), default=True)
    has_leadership = models.BooleanField(_("Fursa za uongozi"), default=False)
    points_per_payment = models.PositiveIntegerField(_("Pointi kwa malipo"), default=10)
    colour = models.CharField(max_length=20, default="#12864a")
    benefits = models.TextField(_("Faida"), blank=True, help_text="Mstari mmoja kwa kila faida")
    benefits_en = models.TextField(blank=True)
    is_featured = models.BooleanField(_("Maarufu"), default=False)
    is_selectable = models.BooleanField(
        _("Inaweza kuchaguliwa"), default=True,
        help_text=_("Ikizimwa, mwombaji hawezi kuichagua mwenyewe. Msimamizi "
                    "pekee ndiye anayeweza kumpandisha mwanachama kwenye daraja hili."))
    is_special = models.BooleanField(
        _("Daraja maalum"), default=False,
        help_text=_("Linaonyeshwa kwa heshima kwenye tovuti lakini si la kuomba."))
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "monthly_fee"]
        verbose_name = _("Kategoria ya Uanachama")
        verbose_name_plural = _("Kategoria za Uanachama")

    def __str__(self):
        return self.name

    @property
    def admin_only(self):
        """Daraja linalotolewa na msimamizi pekee."""
        return not self.is_selectable

    def benefit_list(self):
        raw = self.tx("benefits")
        return [b.strip() for b in raw.splitlines() if b.strip()]


class MemberStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    SUSPENDED = "suspended", _("Imesitishwa")
    EXPIRED = "expired", _("Imeisha muda")


class Member(TimeStamped):
    user = models.OneToOneField("accounts.User", null=True, blank=True,
                                on_delete=models.SET_NULL, related_name="member")
    membership_no = models.CharField(_("Namba ya Mwanachama"), max_length=32, unique=True, blank=True)
    account_no = models.CharField(_("Namba ya Akaunti"), max_length=20, unique=True, blank=True)

    full_name = models.CharField(_("Jina Kamili"), max_length=140)
    gender = models.CharField(_("Jinsia"), max_length=10, blank=True,
                              choices=[("male", _("Mwanaume")), ("female", _("Mwanamke"))])
    date_of_birth = models.DateField(_("Tarehe ya Kuzaliwa"), null=True, blank=True)
    id_type = models.CharField(_("Aina ya Kitambulisho"), max_length=16, blank=True,
                               choices=ID_TYPES, default="nida")
    national_id = models.CharField(_("Namba ya Kitambulisho"), max_length=32, blank=True)
    nationality = models.CharField(_("Uraia"), max_length=60, blank=True, default="Mtanzania")
    religion = models.CharField(_("Dini"), max_length=40, blank=True, default="Kiislamu")
    occupation = models.CharField(_("Kazi"), max_length=100, blank=True)
    photo = models.ImageField(upload_to="members/", blank=True, null=True)

    phone = models.CharField(_("Simu"), max_length=24)
    email = models.EmailField(_("Barua Pepe"), blank=True)
    region = models.ForeignKey("geo.Region", null=True, blank=True,
                               on_delete=models.SET_NULL, related_name="members")
    district = models.ForeignKey("geo.District", null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name="members")
    ward = models.ForeignKey("geo.Ward", null=True, blank=True,
                             on_delete=models.SET_NULL, related_name="members")
    street = models.CharField(_("Mtaa / Kijiji"), max_length=120, blank=True)
    address = models.TextField(_("Anuani Kamili"), blank=True)
    branch = models.ForeignKey("geo.Branch", null=True, blank=True,
                               on_delete=models.SET_NULL, related_name="members")

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="members")
    status = models.CharField(_("Hali"), max_length=12, choices=MemberStatus.choices,
                              default=MemberStatus.ACTIVE)
    joined_on = models.DateField(_("Tarehe ya Usajili"), default=timezone.localdate)
    expires_on = models.DateField(_("Tarehe ya Kuisha"), null=True, blank=True)

    class Meta:
        ordering = ["-joined_on", "-id"]
        verbose_name = _("Mwanachama")
        verbose_name_plural = _("Wanachama")
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["category"]),
            models.Index(fields=["region"]),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.membership_no})"

    # ------------------------------------------------------------------
    @property
    def initials(self):
        parts = [p for p in self.full_name.split() if p]
        if not parts:
            return "??"
        return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()

    @property
    def is_active_member(self):
        return self.status == MemberStatus.ACTIVE

    # -- Muda wa uanachama ---------------------------------------------------
    #: Uanachama hudumu MIAKA MITATU tangu kujiunga au kuhuishwa. Michango
    #: ya mwezi HAIREFUSHI wala haifupishi muda huu — ni michango ya
    #: mwanachama kwa shirika, si ununuzi wa muda. Kadi hufuata tarehe hii.
    TERM_YEARS = 3

    @property
    def days_left(self):
        """Siku zilizobaki kabla uanachama haujaisha. Hasi ikiisha."""
        if not self.expires_on:
            return None
        return (self.expires_on - timezone.localdate()).days

    @property
    def has_expired(self):
        left = self.days_left
        return left is not None and left < 0

    @staticmethod
    def _plus_years(base, years):
        """
        Ongeza miaka bila kuvunjika tarehe 29 Februari.

        `date(2028, 2, 29).replace(year=2031)` inatupa ValueError kwa
        sababu 2031 si mwaka wa mrukio. Tunashusha hadi 28 Februari.
        """
        try:
            return base.replace(year=base.year + years)
        except ValueError:
            return base.replace(year=base.year + years, day=28)

    def start_term(self, years=None):
        """
        Anzisha kipindi cha uanachama kuanzia leo. Huitwa mtu anapokubaliwa.
        """
        years = years or self.TERM_YEARS
        today = timezone.localdate()
        self.expires_on = self._plus_years(today, years)
        fields = ["expires_on"]
        if self.status == MemberStatus.EXPIRED:
            self.status = MemberStatus.ACTIVE
            fields.append("status")
        super().save(update_fields=fields)
        return self.expires_on

    def renew_term(self, years=None):
        """
        Huisha uanachama kwa kipindi kingine.

        Akihuisha kabla muda haujaisha, kipindi kipya kinaanzia tarehe ya
        kuisha iliyopo — hapotezi siku alizobakiwa nazo. Akichelewa,
        kinaanzia leo.
        """
        years = years or self.TERM_YEARS
        today = timezone.localdate()
        base = self.expires_on if (self.expires_on and self.expires_on > today) else today
        self.expires_on = self._plus_years(base, years)

        fields = ["expires_on"]
        # Kuhuisha kunamrudisha mtu kwenye hali ya kawaida. Aliyesitishwa
        # HAYARUDISHWI kimya kimya — hilo ni uamuzi wa afisa, si wa malipo.
        if self.status == MemberStatus.EXPIRED:
            self.status = MemberStatus.ACTIVE
            fields.append("status")
        super().save(update_fields=fields)

        # Kadi inafuata muda wa uanachama; ya zamani haitumiki tena.
        Card.issue(self, expires_on=self.expires_on)
        return self.expires_on

    def create_login(self, password=None):
        """
        Tengeneza akaunti ya kuingia kwa mwanachama huyu.

        Jina la mtumiaji ni namba ya uanachama. Mwanachama anaweza pia
        kuingia kwa barua pepe yake (angalia `login_view`).
        Rudisha nenosiri la muda ili afisa amwambie.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()

        if self.user_id:
            return None

        if not password:
            # Herufi zenye utata (0/O, 1/l/I) zimeondolewa ili nenosiri
            # liweze kusomwa kwa simu bila makosa.
            alphabet = "abcdefghjkmnpqrstuvwxyz23456789"
            password = "".join(secrets.choice(alphabet) for _ in range(10))
        parts = self.full_name.split()
        account = User.objects.create(
            username=self.membership_no,
            first_name=parts[0] if parts else "",
            last_name=parts[-1] if len(parts) > 1 else "",
            email=self.email or "",
            phone=self.phone,
            role="member",
            region=self.region,
            district=self.district,
            is_staff=False,
        )
        account.set_password(password)
        account.save()

        self.user = account
        super().save(update_fields=["user"])

        from content.models import Notification
        Notification.objects.create(
            member=self, user=account,
            title="Karibu MUWESTA",
            body=(f"Uanachama wako umeidhinishwa. Namba yako ni {self.membership_no}. "
                  f"Kadi yako ya kidijitali iko tayari."),
            icon="check-circle", tint="green", url="/mwanachama/kadi/",
        )
        return password

    def save(self, *args, **kwargs):
        self.phone = normalize_phone(self.phone)
        if not self.membership_no or not self.account_no:
            with transaction.atomic():
                year = self.joined_on.year if self.joined_on else timezone.localdate().year
                if not self.membership_no:
                    seq = Sequence.next(f"member:{self.category.code}:{year}")
                    self.membership_no = (f"{settings.ID_PREFIX}/{self.category.code}"
                                          f"/{seq:06d}/{year}")
                if not self.account_no:
                    acc = Sequence.next("account")
                    self.account_no = f"11{acc:08d}"
                super().save(*args, **kwargs)
            return
        super().save(*args, **kwargs)


class ApplicationStatus(models.TextChoices):
    PENDING = "pending", _("Inasubiri")
    REVIEW = "review", _("Kwenye Usahihishaji")
    #: Taarifa zimehakikiwa na afisa, lakini ada bado haijalipwa.
    #: Namba ya uanachama, kadi na akaunti ya kuingia HAVITOLEWI hapa —
    #: vinatolewa malipo yakithibitishwa (angalia `activate`).
    AWAITING_PAYMENT = "awaiting_payment", _("Inasubiri Malipo")
    APPROVED = "approved", _("Imepitishwa")
    REJECTED = "rejected", _("Imekataliwa")


class Application(TimeStamped):
    """Ombi la uanachama kabla halijaidhinishwa."""
    reference = models.CharField(_("Namba ya Maombi"), max_length=32, unique=True, blank=True)
    full_name = models.CharField(_("Jina Kamili"), max_length=140)
    gender = models.CharField(_("Jinsia"), max_length=10, blank=True,
                              choices=[("male", _("Mwanaume")), ("female", _("Mwanamke"))])
    date_of_birth = models.DateField(_("Tarehe ya Kuzaliwa"), null=True, blank=True)
    id_type = models.CharField(_("Aina ya Kitambulisho"), max_length=16, blank=True,
                               choices=ID_TYPES, default="nida")
    national_id = models.CharField(_("Namba ya Kitambulisho"), max_length=32, blank=True)
    nationality = models.CharField(_("Uraia"), max_length=60, blank=True, default="Mtanzania")
    religion = models.CharField(_("Dini"), max_length=40, blank=True, default="Kiislamu")
    phone = models.CharField(_("Namba ya Simu"), max_length=24)
    email = models.EmailField(_("Barua Pepe"), blank=True)
    region = models.ForeignKey("geo.Region", verbose_name=_("Mkoa"), null=True, blank=True,
                               on_delete=models.SET_NULL)
    district = models.ForeignKey("geo.District", verbose_name=_("Halmashauri"), null=True,
                                 blank=True, on_delete=models.SET_NULL)
    ward = models.ForeignKey("geo.Ward", verbose_name=_("Kata"), null=True, blank=True,
                             on_delete=models.SET_NULL)
    street = models.CharField(_("Mtaa / Kijiji"), max_length=120, blank=True)
    address = models.TextField(_("Anuani ya Posta"), blank=True)
    photo = models.ImageField(_("Picha ya Pasipoti"), upload_to="applications/",
                              blank=True, null=True)
    category = models.ForeignKey(Category, verbose_name=_("Aina ya Uanachama"),
                                 on_delete=models.PROTECT, related_name="applications")
    status = models.CharField(max_length=20, choices=ApplicationStatus.choices,
                              default=ApplicationStatus.PENDING)
    note = models.TextField(_("Maelezo"), blank=True)
    reviewed_by = models.ForeignKey("accounts.User", null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name="reviewed_applications")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    member = models.OneToOneField(Member, null=True, blank=True,
                                  on_delete=models.SET_NULL, related_name="application")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Ombi la Uanachama")
        verbose_name_plural = _("Maombi ya Uanachama")

    def __str__(self):
        return f"{self.reference} — {self.full_name}"

    def save(self, *args, **kwargs):
        self.phone = normalize_phone(self.phone)
        if not self.reference:
            with transaction.atomic():
                year = timezone.localdate().year
                seq = Sequence.next(f"application:{year}")
                self.reference = f"APP/{settings.ID_PREFIX}/{year}/{seq:04d}"
                super().save(*args, **kwargs)
            return
        super().save(*args, **kwargs)

    @property
    def badge(self):
        return {"pending": "warn", "review": "info", "awaiting_payment": "warn",
                "approved": "ok", "rejected": "danger"}.get(self.status, "muted")

    @property
    def awaiting_payment(self):
        return self.status == ApplicationStatus.AWAITING_PAYMENT

    def amount_due(self, months=1):
        """
        Kiasi cha chini kabisa cha kuanzisha uanachama.

        Ni ada ya usajili + mwezi mmoja. Mwombaji anaweza kulipia miezi
        zaidi akitaka — hii ni kiwango cha chini tu, si bei iliyowekwa.
        """
        from core.data import giving
        return int(self.category.registration_fee or 0) + \
            giving.months_price(self.category.monthly_fee, months)

    @transaction.atomic
    def approve(self, user=None):
        """
        Hakiki ombi — HAIMFANYI kuwa mwanachama bado.

        Hapo awali hatua hii ilitoa namba ya uanachama, kadi na akaunti ya
        kuingia mara moja. Sasa uanachama unaanza pale ada inapolipwa
        (`activate`), kwa hiyo hapa tunathibitisha taarifa pekee na
        kumpa mwombaji ruhusa ya kulipa.
        """
        if self.member_id:
            return self.member
        self.status = ApplicationStatus.AWAITING_PAYMENT
        self.reviewed_by = user
        self.reviewed_at = timezone.now()
        self.save(update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"])
        return None

    @transaction.atomic
    def activate(self):
        """
        Geuza ombi kuwa mwanachama kamili. Huitwa MALIPO YAKITHIBITISHWA.

        Hatua zinazofanyika kwa pamoja (zote au hakuna):
          1. Rekodi ya mwanachama + namba ya uanachama + namba ya akaunti
          2. Akaunti ya fedha (leja)
          3. Kadi yenye QR
          4. Akaunti ya kuingia + nenosiri la muda
          5. Arifa ya kumkaribisha

        Nenosiri la muda linahifadhiwa kwenye `member.temp_password` ili
        afisa aweze kumpa mwanachama. Halihifadhiwi kwenye database.

        Ni salama kuiita mara nyingi — ikishaunda mwanachama, inarudisha
        yule yule badala ya kuunda mwingine. Muhimu, kwa sababu Pesapal
        huweza kupiga IPN zaidi ya mara moja kwa muamala mmoja.
        """
        if self.member_id:
            return self.member

        member = Member.objects.create(
            full_name=self.full_name, gender=self.gender, date_of_birth=self.date_of_birth,
            id_type=self.id_type, national_id=self.national_id,
            nationality=self.nationality, religion=self.religion,
            phone=self.phone, email=self.email, region=self.region, district=self.district,
            ward=self.ward, street=self.street, address=self.address, category=self.category,
        )

        # Akaunti ya fedha — bila hii leja haina pa kuingia
        from finance.models import Account
        Account.objects.get_or_create(member=member)

        # Kipindi cha miaka mitatu kinaanza hapa, si malipo ya kwanza
        # yanapofanyika. Michango ya mwezi haitakigusa.
        member.start_term()
        Card.issue(member, expires_on=member.expires_on)
        member.temp_password = member.create_login()

        self.member = member
        self.status = ApplicationStatus.APPROVED
        if not self.reviewed_at:
            self.reviewed_at = timezone.now()
        self.save(update_fields=["member", "status", "reviewed_at", "updated_at"])
        return member


class Card(TimeStamped):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="cards")
    serial = models.CharField(max_length=40, unique=True, blank=True)
    issued_on = models.DateField(default=timezone.localdate)
    expires_on = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    printed = models.BooleanField(_("Imechapishwa"), default=False)

    class Meta:
        ordering = ["-issued_on"]
        verbose_name = _("Kadi ya Uanachama")
        verbose_name_plural = _("Kadi za Uanachama")

    def __str__(self):
        return self.serial

    def save(self, *args, **kwargs):
        if not self.serial:
            with transaction.atomic():
                year = timezone.localdate().year
                seq = Sequence.next(f"card:{year}")
                self.serial = (f"{settings.ID_PREFIX}/{self.member.category.code}"
                               f"/{seq:05d}/{year}")
                super().save(*args, **kwargs)
            return
        super().save(*args, **kwargs)

    @classmethod
    def issue(cls, member, years=3, expires_on=None):
        """
        Toa kadi mpya. Ya zamani inasitishwa.

        Kadi hufuata muda wa uanachama — ndiyo maana `expires_on`
        inaweza kupitishwa. Bila hiyo, inahesabiwa miaka mitatu tangu
        leo, ambayo ni sawa kwa mwanachama anayeanza.
        """
        today = timezone.localdate()
        if expires_on is None:
            expires_on = Member._plus_years(today, years)
        cls.objects.filter(member=member, is_active=True).update(is_active=False)
        return cls.objects.create(
            member=member, issued_on=today, expires_on=expires_on,
        )

    @property
    def verify_path(self):
        return f"/hakiki/{self.serial.replace('/', '-')}/"


class FamilyMember(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="family")
    full_name = models.CharField(_("Jina"), max_length=140)
    relationship = models.CharField(_("Uhusiano"), max_length=60)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=24, blank=True)

    class Meta:
        verbose_name = _("Mwanafamilia")
        verbose_name_plural = _("Familia")

    def __str__(self):
        return self.full_name


class Beneficiary(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="beneficiaries")
    full_name = models.CharField(_("Jina"), max_length=140)
    relationship = models.CharField(_("Uhusiano"), max_length=60)
    phone = models.CharField(max_length=24, blank=True)
    percentage_share = models.DecimalField(_("Asilimia"), max_digits=5, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("Mnufaika")
        verbose_name_plural = _("Wanufaika")

    def __str__(self):
        return self.full_name
