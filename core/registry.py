"""
Usajili wa vitu vinavyosimamiwa ndani ya dashibodi ya MWST.

Lengo: kila kitu kifanyike ndani ya mfumo. Django admin ya kawaida
haitumiki wala hairejewi popote kwenye menyu.

Kila kipengele kinaeleza:
    model     — model inayosimamiwa
    label     — jina la wingi linaloonekana
    columns   — safu za jedwali: (field, kichwa)
    fields    — fields za fomu (None = zote zinazoweza kuhaririwa)
    search    — fields za kutafuta
    filters   — fields za kuchuja
    roles     — majukumu yanayoruhusiwa (None = watumishi wote)
    singleton — True kwa model yenye rekodi moja (mipangilio)
    readonly  — True kwa data zisizohaririwa (leja, kumbukumbu)
    group     — kikundi kwenye ukurasa wa faharasa
"""
from accounts.models import Role

ADMINS = [Role.SUPER_ADMIN, Role.ADMIN]
ADMINS_PLUS = ADMINS + [Role.MANAGEMENT]

REGISTRY = {
    # ---------------- Uanachama ----------------
    "kategoria": {
        "model": "members.Category", "label": "Kategoria za Uanachama", "group": "Uanachama",
        "icon": "star", "columns": [("name", "Jina"), ("code", "Herufi"),
                                    ("monthly_fee", "Ada ya Mwezi"),
                                    ("points_per_payment", "Pointi"),
                                    ("is_selectable", "Inachaguliwa"),
                                    ("is_special", "Maalum"), ("order", "Mpangilio")],
        "fields": ["name", "name_en", "code", "monthly_fee", "points_per_payment",
                   "colour", "benefits", "benefits_en", "is_featured",
                   "is_selectable", "is_special", "order"],
        "search": ["name", "code"], "roles": ADMINS,
    },
    "kadi": {
        "model": "members.Card", "label": "Kadi za Uanachama", "group": "Uanachama",
        "icon": "id-card", "columns": [("serial", "Namba ya Kadi"), ("member", "Mwanachama"),
                                       ("issued_on", "Ilitolewa"), ("expires_on", "Halali Hadi"),
                                       ("is_active", "Hai"), ("printed", "Imechapishwa")],
        "fields": ["member", "issued_on", "expires_on", "is_active", "printed"],
        "search": ["serial", "member__full_name", "member__membership_no"],
        "filters": ["is_active", "printed"],
    },
    "familia": {
        "model": "members.FamilyMember", "label": "Wanafamilia", "group": "Uanachama",
        "icon": "users", "columns": [("full_name", "Jina"), ("member", "Mwanachama"),
                                     ("relationship", "Uhusiano"), ("phone", "Simu")],
        "search": ["full_name", "member__full_name"],
    },
    "wanufaika": {
        "model": "members.Beneficiary", "label": "Wanufaika", "group": "Uanachama",
        "icon": "heart", "columns": [("full_name", "Jina"), ("member", "Mwanachama"),
                                     ("relationship", "Uhusiano"),
                                     ("percentage_share", "Asilimia")],
        "search": ["full_name", "member__full_name"],
    },

    # ---------------- Fedha ----------------
    "mifuko": {
        "model": "finance.Fund", "label": "Mifuko ya Fedha", "group": "Fedha",
        "icon": "wallet", "columns": [("name", "Jina"), ("code", "Msimbo"),
                                      ("is_restricted", "Ina Masharti"),
                                      ("annual_target", "Lengo la Mwaka"), ("order", "Mpangilio")],
        "fields": ["name", "name_en", "code", "is_restricted", "colour", "icon",
                   "annual_target", "order"],
        "search": ["name", "code"], "roles": ADMINS,
    },
    "leja": {
        "model": "finance.LedgerEntry", "label": "Leja", "group": "Fedha",
        "icon": "receipt", "readonly": True,
        "columns": [("entry_date", "Tarehe"), ("account", "Akaunti"), ("fund", "Mfuko"),
                    ("amount", "Kiasi"), ("description", "Maelezo")],
        "search": ["description", "account__member__full_name"], "filters": ["fund"],
    },
    "matumizi": {
        "model": "finance.Expense", "label": "Matumizi", "group": "Fedha",
        "icon": "cash", "columns": [("spent_on", "Tarehe"), ("title", "Maelezo"),
                                    ("fund", "Mfuko"), ("amount", "Kiasi"),
                                    ("project", "Mradi")],
        "fields": ["fund", "project", "title", "amount", "spent_on"],
        "search": ["title"], "filters": ["fund"],
    },
    "miradi": {
        "model": "finance.Project", "label": "Miradi", "group": "Fedha",
        "icon": "building", "columns": [("title", "Mradi"), ("region", "Mkoa"),
                                        ("status", "Hali"), ("target_amount", "Lengo")],
        "fields": ["title", "title_en", "summary", "summary_en", "region", "status",
                   "target_amount", "scene", "start_date", "end_date"],
        "search": ["title"], "filters": ["status", "region"],
    },
    "kampeni": {
        "model": "finance.Campaign", "label": "Kampeni", "group": "Fedha",
        "icon": "target", "columns": [("title", "Kampeni"), ("fund", "Mfuko"),
                                      ("target_amount", "Lengo"), ("end_date", "Inaisha"),
                                      ("is_active", "Hai")],
        "fields": ["title", "title_en", "summary", "summary_en", "fund", "project",
                   "target_amount", "start_date", "end_date", "scene", "is_active"],
        "search": ["title"], "filters": ["is_active"],
    },
    "wahisani": {
        "model": "finance.Donor", "label": "Wahisani na Wadau", "group": "Fedha",
        "icon": "hand-heart", "columns": [("name", "Jina"), ("donor_type", "Aina"),
                                          ("region", "Mkoa"), ("phone", "Simu"),
                                          ("is_partner", "Mdau"), ("is_active", "Hai")],
        "fields": ["name", "donor_type", "member", "region", "country", "phone",
                   "email", "is_partner", "is_active"],
        "search": ["name", "email", "phone"], "filters": ["donor_type", "is_partner"],
    },

    # ---------------- Programu ----------------
    "kanuni-pointi": {
        "model": "programs.PointRule", "label": "Kanuni za Pointi", "group": "Programu",
        "icon": "star", "columns": [("activity", "Shughuli"), ("code", "Msimbo"),
                                    ("points", "Pointi"), ("is_active", "Hai")],
        "fields": ["code", "activity", "activity_en", "points", "note", "note_en",
                   "is_active", "order"],
        "search": ["activity", "code"], "roles": ADMINS,
    },
    "pointi": {
        "model": "programs.PointTransaction", "label": "Miamala ya Pointi", "group": "Programu",
        "icon": "trophy", "readonly": True,
        "columns": [("awarded_on", "Tarehe"), ("member", "Mwanachama"),
                    ("points", "Pointi"), ("reason", "Sababu"), ("source", "Chanzo")],
        "search": ["member__full_name", "reason", "source"],
    },
    "tuzo": {
        "model": "programs.Reward", "label": "Tuzo", "group": "Programu",
        "icon": "gift", "columns": [("title", "Tuzo"), ("points_required", "Pointi"),
                                    ("is_active", "Hai")],
        "fields": ["title", "title_en", "description", "description_en",
                   "points_required", "is_active"],
        "search": ["title"],
    },
    "aina-msaada": {
        "model": "programs.AssistanceType", "label": "Aina za Msaada", "group": "Programu",
        "icon": "hand-heart", "columns": [("name", "Jina"), ("icon", "Ikoni")],
        "fields": ["name", "name_en", "icon"], "search": ["name"],
    },
    "aina-matukio": {
        "model": "programs.EventType", "label": "Aina za Matukio", "group": "Programu",
        "icon": "calendar", "columns": [("name", "Jina"), ("slug", "Msimbo"),
                                        ("scene", "Mchoro")],
        "fields": ["name", "name_en", "slug", "colour", "scene"], "search": ["name"],
    },
    "matukio": {
        "model": "programs.Event", "label": "Matukio", "group": "Programu",
        "icon": "calendar", "columns": [("title", "Tukio"), ("event_type", "Aina"),
                                        ("start_at", "Kuanza"), ("region", "Mkoa"),
                                        ("status", "Hali"), ("is_public", "Hadharani")],
        "fields": ["title", "title_en", "summary", "summary_en", "event_type", "venue",
                   "venue_en", "region", "start_at", "end_at", "status", "is_public",
                   "capacity"],
        "search": ["title", "venue"], "filters": ["status", "event_type", "region"],
    },
    "usajili-matukio": {
        "model": "programs.EventRegistration", "label": "Usajili wa Matukio",
        "group": "Programu", "icon": "calendar-check",
        "columns": [("event", "Tukio"), ("member", "Mwanachama"), ("full_name", "Jina"),
                    ("phone", "Simu"), ("attended", "Alihudhuria")],
        "fields": ["event", "member", "full_name", "phone", "email", "attended"],
        "search": ["full_name", "member__full_name"], "filters": ["attended", "event"],
    },

    # ---------------- Maudhui ----------------
    "habari": {
        "model": "content.News", "label": "Habari", "group": "Maudhui",
        "icon": "file", "columns": [("title", "Kichwa"), ("category", "Kategoria"),
                                    ("published_on", "Tarehe"), ("is_featured", "Kuu"),
                                    ("is_published", "Imechapishwa")],
        "fields": ["title", "title_en", "summary", "summary_en", "body", "body_en",
                   "category", "scene", "image", "published_on", "is_featured",
                   "is_published"],
        "search": ["title", "summary"], "filters": ["category", "is_published"],
    },
    "kategoria-habari": {
        "model": "content.NewsCategory", "label": "Kategoria za Habari", "group": "Maudhui",
        "icon": "folder", "columns": [("name", "Jina"), ("slug", "Msimbo")],
        "fields": ["name", "name_en", "slug"], "search": ["name"],
    },
    "matangazo": {
        "model": "content.Announcement", "label": "Matangazo", "group": "Maudhui",
        "icon": "megaphone", "columns": [("title", "Kichwa"), ("audience", "Wapokeaji"),
                                         ("published_on", "Tarehe"), ("is_active", "Hai")],
        "fields": ["title", "title_en", "body", "body_en", "icon", "tint",
                   "audience", "published_on", "is_active"],
        "search": ["title"], "filters": ["audience", "is_active"],
    },
    "albamu": {
        "model": "content.Album", "label": "Albamu", "group": "Maudhui",
        "icon": "folder", "columns": [("name", "Jina"), ("scene", "Mchoro"),
                                      ("is_public", "Hadharani")],
        "fields": ["name", "name_en", "scene", "is_public"], "search": ["name"],
    },
    "media": {
        "model": "content.MediaItem", "label": "Picha na Video", "group": "Maudhui",
        "icon": "image", "columns": [("title", "Kichwa"), ("kind", "Aina"),
                                     ("category", "Kategoria"), ("album", "Albamu"),
                                     ("size_mb", "MB"), ("uploaded_on", "Tarehe")],
        "fields": ["title", "title_en", "kind", "category", "album", "file",
                   "scene", "duration"],
        "search": ["title"], "filters": ["kind", "category", "album"],
    },
    "huduma": {
        "model": "content.Service", "label": "Huduma Zetu", "group": "Maudhui",
        "icon": "hand-heart", "columns": [("title", "Huduma"), ("category", "Kundi"),
                                          ("order", "Mpangilio"), ("is_active", "Hai")],
        "fields": ["title", "title_en", "summary", "summary_en", "stats_line",
                   "stats_line_en", "icon", "tint", "scene", "category", "order",
                   "is_active"],
        "search": ["title"],
    },
    "maswali": {
        "model": "content.Faq", "label": "Maswali Yanayoulizwa", "group": "Maudhui",
        "icon": "info", "columns": [("question", "Swali"), ("page", "Ukurasa"),
                                    ("order", "Mpangilio"), ("is_active", "Hai")],
        "fields": ["question", "question_en", "answer", "answer_en", "page",
                   "order", "is_active"],
        "search": ["question"], "filters": ["page"],
    },
    "viongozi": {
        "model": "content.Leader", "label": "Viongozi", "group": "Maudhui",
        "icon": "user", "columns": [("full_name", "Jina"), ("role", "Wadhifa"),
                                    ("order", "Mpangilio"), ("is_active", "Hai")],
        "fields": ["full_name", "role", "role_en", "photo", "order", "is_active"],
        "search": ["full_name"],
    },
    "historia": {
        "model": "content.Milestone", "label": "Historia ya MWST", "group": "Maudhui",
        "icon": "clock", "columns": [("year", "Mwaka"), ("title", "Kichwa"),
                                     ("order", "Mpangilio")],
        "fields": ["year", "title", "title_en", "body", "body_en", "order"],
        "search": ["title", "year"],
    },
    "nguzo": {
        "model": "content.Pillar", "label": "Dira, Dhamira na Maadili", "group": "Maudhui",
        "icon": "target", "columns": [("title", "Nguzo"), ("icon", "Ikoni"),
                                      ("order", "Mpangilio")],
        "fields": ["title", "title_en", "body", "body_en", "icon", "tint", "order"],
        "search": ["title"],
    },
    "aya": {
        "model": "content.Verse", "label": "Aya za Qur'an", "group": "Maudhui",
        "icon": "book", "columns": [("reference", "Rejea"), ("swahili", "Kiswahili"),
                                    ("is_active", "Hai"), ("order", "Mpangilio")],
        "fields": ["arabic", "swahili", "swahili_en", "reference", "is_active", "order"],
        "search": ["reference", "swahili"],
    },

    # ---------------- Mawasiliano ----------------
    "ujumbe-mawasiliano": {
        "model": "content.ContactMessage", "label": "Ujumbe wa Mawasiliano",
        "group": "Mawasiliano", "icon": "mail",
        "columns": [("created_at", "Tarehe"), ("full_name", "Jina"),
                    ("subject", "Mada"), ("phone", "Simu"), ("is_read", "Imesomwa"),
                    ("replied", "Imejibiwa")],
        "fields": ["is_read", "replied"],
        "search": ["full_name", "email", "phone", "body"],
        "filters": ["is_read", "replied"],
    },
    "arifa": {
        "model": "content.Notification", "label": "Arifa", "group": "Mawasiliano",
        "icon": "bell", "columns": [("created_at", "Tarehe"), ("title", "Kichwa"),
                                    ("member", "Mwanachama"), ("is_read", "Imesomwa")],
        "fields": ["user", "member", "title", "body", "icon", "tint", "url", "is_read"],
        "search": ["title", "body"], "filters": ["is_read"],
    },
    "kumbukumbu-ujumbe": {
        "model": "content.MessageLog", "label": "Kumbukumbu za Ujumbe",
        "group": "Mawasiliano", "icon": "message", "readonly": True,
        "columns": [("created_at", "Tarehe"), ("channel", "Njia"), ("subject", "Mada"),
                    ("recipients", "Wapokeaji"), ("status", "Hali"), ("sent_by", "Aliyetuma")],
        "search": ["subject", "body"], "filters": ["channel", "status"],
    },

    # ---------------- Jiografia ----------------
    "kanda": {
        "model": "geo.Zone", "label": "Kanda", "group": "Jiografia",
        "icon": "globe", "columns": [("name", "Kanda"), ("code", "Msimbo"),
                                     ("coordinator", "Mratibu"), ("office", "Ofisi"),
                                     ("order", "Mpangilio")],
        "fields": ["name", "name_en", "code", "coordinator", "office", "order"],
        "search": ["name", "code"], "roles": ADMINS,
    },
    "mikoa": {
        "model": "geo.Region", "label": "Mikoa", "group": "Jiografia",
        "icon": "map", "columns": [("name", "Mkoa"), ("zone", "Kanda"),
                                   ("map_x", "X"), ("map_y", "Y"), ("order", "Mpangilio")],
        "fields": ["name", "zone", "code", "map_x", "map_y", "order"],
        "search": ["name"], "filters": ["zone"], "roles": ADMINS,
    },
    "halmashauri": {
        "model": "geo.District", "label": "Halmashauri", "group": "Jiografia",
        "icon": "map-pin", "columns": [("name", "Halmashauri"), ("kind", "Aina"),
                                       ("region", "Mkoa")],
        "fields": ["region", "name", "kind"], "search": ["name"],
        "filters": ["region", "kind"], "roles": ADMINS,
    },
    "kata": {
        "model": "geo.Ward", "label": "Kata", "group": "Jiografia",
        "icon": "map-pin", "columns": [("name", "Kata"), ("district", "Halmashauri")],
        "fields": ["district", "name"], "search": ["name"], "roles": ADMINS,
    },
    "matawi": {
        "model": "geo.Branch", "label": "Matawi", "group": "Jiografia",
        "icon": "briefcase", "columns": [("name", "Tawi"), ("region", "Mkoa"),
                                         ("phone", "Simu"), ("is_head_office", "Ofisi Kuu")],
        "fields": ["name", "region", "district", "address", "phone", "email",
                   "contact_person", "is_head_office"],
        "search": ["name", "address"], "filters": ["region"],
    },

    # ---------------- Mfumo ----------------
    "watumiaji": {
        "model": "accounts.User", "label": "Watumiaji wa Mfumo", "group": "Mfumo",
        "icon": "user", "columns": [("username", "Jina la Mtumiaji"),
                                    ("get_full_name", "Jina Kamili"), ("role", "Jukumu"),
                                    ("phone", "Simu"), ("is_active", "Hai")],
        "fields": ["username", "first_name", "last_name", "email", "phone", "role",
                   "region", "district", "branch", "is_active", "two_factor"],
        "search": ["username", "first_name", "last_name", "email"],
        "filters": ["role", "is_active"], "roles": ADMINS,
    },
    "kumbukumbu": {
        "model": "accounts.AuditLog", "label": "Kumbukumbu za Matendo", "group": "Mfumo",
        "icon": "shield", "readonly": True,
        "columns": [("created_at", "Tarehe"), ("user", "Mtumiaji"), ("action", "Kitendo"),
                    ("table_affected", "Jedwali"), ("ip_address", "IP")],
        "search": ["action", "detail"], "filters": ["action"], "roles": ADMINS_PLUS,
    },
    "mipangilio": {
        "model": "content.SiteSetting", "label": "Mipangilio ya Mfumo", "group": "Mfumo",
        "icon": "settings", "singleton": True, "columns": [],
        "fields": ["org_name", "tagline", "tagline_en", "about", "about_en",
                   "phone", "phone_alt", "email", "email_alt", "address", "address_en",
                   "working_hours", "working_hours_en", "facebook", "twitter",
                   "instagram", "youtube", "whatsapp", "storage_quota_gb",
                   "fundraising_target"],
        "roles": ADMINS,
    },
}


def get_entry(slug):
    return REGISTRY.get(slug)


def allowed(entry, user):
    roles = entry.get("roles")
    return roles is None or user.role in [r.value if hasattr(r, "value") else r
                                          for r in roles]


def groups(user):
    """Vipengele vilivyopangwa kwa vikundi, kwa mtumiaji huyu."""
    out = {}
    for slug, entry in REGISTRY.items():
        if not allowed(entry, user):
            continue
        out.setdefault(entry.get("group", "Nyingine"), []).append({
            "slug": slug, "label": entry["label"], "icon": entry.get("icon", "file"),
            "readonly": entry.get("readonly", False),
            "singleton": entry.get("singleton", False),
        })
    return out
