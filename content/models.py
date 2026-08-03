"""Maudhui ya tovuti: habari, picha, huduma, maswali, mipangilio."""
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.mixins import Bilingual, TimeStamped


class SiteSetting(Bilingual):
    """Mipangilio ya jumla — rekodi moja tu."""
    org_name = models.CharField(max_length=140, default="Muslim Welfare Society of Tanzania")
    tagline = models.CharField(max_length=200, default="Imani kwa Vitendo, Huduma na Maendeleo kwa Binadamu")
    tagline_en = models.CharField(max_length=200, blank=True)
    about = models.TextField(blank=True)
    about_en = models.TextField(blank=True)
    phone = models.CharField(max_length=24, default="+255 769 600 102")
    phone_alt = models.CharField(max_length=24, blank=True)
    email = models.EmailField(default="info@muslimwelfare.or.tz")
    email_alt = models.EmailField(blank=True)
    address = models.CharField(max_length=200, default="Nkuhungu, Dodoma, Tanzania")
    address_en = models.CharField(max_length=200, blank=True)
    working_hours = models.CharField(max_length=120, default="Jumatatu - Ijumaa: 08:00 - 17:00")
    working_hours_en = models.CharField(max_length=120, blank=True)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    whatsapp = models.CharField(max_length=40, blank=True)
    storage_quota_gb = models.PositiveIntegerField(default=100)
    fundraising_target = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        verbose_name = _("Mipangilio ya Mfumo")
        verbose_name_plural = _("Mipangilio ya Mfumo")

    def __str__(self):
        return self.org_name

    @classmethod
    def get(cls):
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create()
        return obj


class Verse(Bilingual):
    arabic = models.TextField(_("Kiarabu"))
    swahili = models.CharField(_("Kiswahili"), max_length=240)
    swahili_en = models.CharField(max_length=240, blank=True)
    reference = models.CharField(max_length=60)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Aya ya Qur'an")
        verbose_name_plural = _("Aya za Qur'an")

    def __str__(self):
        return self.reference


class NewsCategory(Bilingual):
    name = models.CharField(max_length=60, unique=True)
    name_en = models.CharField(max_length=60, blank=True)
    slug = models.SlugField(max_length=40, unique=True)

    class Meta:
        verbose_name = _("Kategoria ya Habari")
        verbose_name_plural = _("Kategoria za Habari")

    def __str__(self):
        return self.name


class News(Bilingual, TimeStamped):
    title = models.CharField(_("Kichwa"), max_length=200)
    title_en = models.CharField(max_length=200, blank=True)
    summary = models.TextField(_("Muhtasari"))
    summary_en = models.TextField(blank=True)
    body = models.TextField(_("Maudhui"), blank=True)
    body_en = models.TextField(blank=True)
    category = models.ForeignKey(NewsCategory, null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name="news")
    scene = models.CharField(max_length=20, default="mkutano")
    image = models.ImageField(upload_to="news/", blank=True, null=True)
    published_on = models.DateField(default=timezone.localdate)
    is_featured = models.BooleanField(_("Habari kuu"), default=False)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-published_on", "-id"]
        verbose_name = _("Habari")
        verbose_name_plural = _("Habari")

    def __str__(self):
        return self.title


class Announcement(Bilingual, TimeStamped):
    title = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    body_en = models.TextField(blank=True)
    icon = models.CharField(max_length=30, default="megaphone")
    tint = models.CharField(max_length=16, default="green")
    audience = models.CharField(max_length=16, default="all",
                                choices=[("all", _("Wote")), ("members", _("Wanachama")),
                                         ("staff", _("Watumishi"))])
    published_on = models.DateField(default=timezone.localdate)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-published_on", "-id"]
        verbose_name = _("Tangazo")
        verbose_name_plural = _("Matangazo")

    def __str__(self):
        return self.title


class Album(Bilingual, TimeStamped):
    name = models.CharField(max_length=140)
    name_en = models.CharField(max_length=140, blank=True)
    scene = models.CharField(max_length=20, default="sadaka")
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Albamu")
        verbose_name_plural = _("Albamu")

    def __str__(self):
        return self.name

    def item_count(self):
        return self.items.count()


class MediaItem(Bilingual, TimeStamped):
    KIND = [("photo", _("Picha")), ("video", _("Video"))]
    CATEGORY = [("miradi", _("Miradi")), ("matukio", _("Matukio")), ("mafunzo", _("Mafunzo")),
                ("misaada", _("Misaada")), ("ziara", _("Ziara")), ("nyingine", _("Nyinginezo"))]

    title = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200, blank=True)
    kind = models.CharField(max_length=8, choices=KIND, default="photo")
    category = models.CharField(max_length=16, choices=CATEGORY, default="matukio")
    album = models.ForeignKey(Album, null=True, blank=True, on_delete=models.SET_NULL,
                              related_name="items")
    file = models.FileField(upload_to="media_center/", blank=True, null=True)
    scene = models.CharField(max_length=20, default="tukio")
    size_mb = models.DecimalField(max_digits=8, decimal_places=1, default=0)
    duration = models.CharField(max_length=10, blank=True, help_text="mm:ss kwa video")
    views = models.PositiveIntegerField(default=0)
    downloads = models.PositiveIntegerField(default=0)
    uploaded_on = models.DateField(default=timezone.localdate)
    uploaded_by = models.ForeignKey("accounts.User", null=True, blank=True,
                                    on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-uploaded_on", "-id"]
        verbose_name = _("Picha / Video")
        verbose_name_plural = _("Picha na Video")

    def __str__(self):
        return self.title


class Service(Bilingual):
    title = models.CharField(max_length=140)
    title_en = models.CharField(max_length=140, blank=True)
    summary = models.TextField()
    summary_en = models.TextField(blank=True)
    stats_line = models.CharField(max_length=120, blank=True)
    stats_line_en = models.CharField(max_length=120, blank=True)
    icon = models.CharField(max_length=30, default="hand-heart")
    tint = models.CharField(max_length=16, default="green")
    scene = models.CharField(max_length=20, default="jamii")
    category = models.SlugField(max_length=30, default="ustawi")
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Huduma")
        verbose_name_plural = _("Huduma Zetu")

    def __str__(self):
        return self.title


class Faq(Bilingual):
    PAGES = [("kuhusu", "Kuhusu Sisi"), ("mawasiliano", "Mawasiliano")]
    question = models.CharField(max_length=240)
    question_en = models.CharField(max_length=240, blank=True)
    answer = models.TextField()
    answer_en = models.TextField(blank=True)
    page = models.CharField(max_length=20, choices=PAGES, default="kuhusu")
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Swali")
        verbose_name_plural = _("Maswali Yanayoulizwa Sana")

    def __str__(self):
        return self.question


class Leader(Bilingual):
    full_name = models.CharField(max_length=140)
    role = models.CharField(max_length=100)
    role_en = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to="leaders/", blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Kiongozi")
        verbose_name_plural = _("Viongozi")

    def __str__(self):
        return self.full_name

    @property
    def initials(self):
        p = [x for x in self.full_name.split() if x]
        return (p[0][0] + p[-1][0]).upper() if len(p) > 1 else self.full_name[:2].upper()


class Milestone(Bilingual):
    year = models.CharField(max_length=8)
    title = models.CharField(max_length=160)
    title_en = models.CharField(max_length=160, blank=True)
    body = models.TextField()
    body_en = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "year"]
        verbose_name = _("Hatua ya Historia")
        verbose_name_plural = _("Historia ya MWST")

    def __str__(self):
        return f"{self.year} — {self.title}"


class Pillar(Bilingual):
    title = models.CharField(max_length=120)
    title_en = models.CharField(max_length=120, blank=True)
    body = models.TextField()
    body_en = models.TextField(blank=True)
    icon = models.CharField(max_length=30, default="target")
    tint = models.CharField(max_length=16, default="green")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Nguzo")
        verbose_name_plural = _("Dira, Dhamira na Maadili")

    def __str__(self):
        return self.title


class ContactMessage(TimeStamped):
    full_name = models.CharField(_("Jina Kamili"), max_length=140)
    phone = models.CharField(_("Simu"), max_length=24)
    email = models.EmailField(_("Barua Pepe"))
    subject = models.CharField(_("Mada"), max_length=120)
    body = models.TextField(_("Ujumbe"))
    is_read = models.BooleanField(default=False)
    replied = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Ujumbe wa Mawasiliano")
        verbose_name_plural = _("Ujumbe wa Mawasiliano")

    def __str__(self):
        return f"{self.full_name} — {self.subject}"


class Notification(TimeStamped):
    user = models.ForeignKey("accounts.User", null=True, blank=True,
                             on_delete=models.CASCADE, related_name="notifications")
    member = models.ForeignKey("members.Member", null=True, blank=True,
                               on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=180)
    body = models.TextField(blank=True)
    icon = models.CharField(max_length=30, default="bell")
    tint = models.CharField(max_length=16, default="green")
    url = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Arifa")
        verbose_name_plural = _("Arifa")

    def __str__(self):
        return self.title


class MessageLog(TimeStamped):
    CHANNEL = [("sms", "SMS"), ("email", _("Barua Pepe")), ("whatsapp", "WhatsApp")]
    STATUS = [("queued", _("Kwenye foleni")), ("sent", _("Imetumwa")),
              ("delivered", _("Imefika")), ("failed", _("Haikufanikiwa"))]

    channel = models.CharField(max_length=10, choices=CHANNEL, default="sms")
    subject = models.CharField(max_length=180, blank=True)
    body = models.TextField()
    recipients = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=12, choices=STATUS, default="queued")
    sent_by = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Kumbukumbu ya Ujumbe")
        verbose_name_plural = _("Kumbukumbu za Ujumbe")

    def __str__(self):
        return f"{self.get_channel_display()} — {self.subject or self.body[:40]}"
