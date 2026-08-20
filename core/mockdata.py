"""
MWST MMS — Mock data layer
==========================

Kila function hapa itabadilishwa na ORM query wakati wa backend.
Majina ya key yamewekwa yakifanana na field za model zijazo, mfano:

    {"membership_no": ...}   ->  Member.membership_no
    {"receipt_no": ...}      ->  Payment.receipt_no
    {"amount": ...}          ->  Payment.amount  (Decimal)

Kanuni: hakuna namba iliyoandikwa moja kwa moja kwenye template.
Zote zinatoka hapa.
"""

MONTHS_SW = ["Jan", "Feb", "Mac", "Apr", "Mei", "Jun",
             "Jul", "Ago", "Sep", "Okt", "Nov", "Des"]

# Chart palette — inafanana na --c1..--c8 kwenye mwst.css
C = {
    "green": "#12864a", "navy": "#1b3b6f", "gold": "#d4af37",
    "purple": "#6d28d9", "teal": "#0891b2", "red": "#dc2626",
    "orange": "#ea580c", "mint": "#4cbd83", "slate": "#64748b",
    "bronze": "#b45309",
}


def tzs(n):
    """TZS 136,450,000"""
    return "TZS {:,}".format(n)


# ---------------------------------------------------------------------------
#  AYA ZA QUR'AN  ->  baadaye: DailyVerse.objects.active()
# ---------------------------------------------------------------------------
VERSES = [
    {
        "arabic": "وَتَعَاوَنُوا۟ عَلَى ٱلْبِرِّ وَٱلتَّقْوَىٰ",
        "swahili": "Na msaidiane katika heri na taqwa.",
        "reference": "Al-Ma'idah: 2",
    },
    {
        "arabic": "وَمَا تُقَدِّمُوا۟ لِأَنفُسِكُم مِّنْ خَيْرٍ تَجِدُوهُ عِندَ ٱللَّهِ",
        "swahili": "Na kheri yoyote mnayoitanguliza kwa ajili yenu, mtaikuta kwa Allah.",
        "reference": "Al-Baqarah: 110",
    },
]


def verse_of_day(i=0):
    return VERSES[i % len(VERSES)]


# ---------------------------------------------------------------------------
#  NAVIGATION  ->  baadaye: itatokana na role permissions
# ---------------------------------------------------------------------------
def nav_superadmin(active="dashboard"):
    return [
        {"label": "Dashibodi", "icon": "dashboard", "url": "/", "active": active == "dashboard"},
        {"section": "Usimamizi wa Mfumo"},
        {"label": "Wanachama", "icon": "users", "children": [
            {"label": "Orodha ya Wanachama"}, {"label": "Sajili Mwanachama"},
            {"label": "Kadi za Uanachama"}, {"label": "Familia & Wategemezi"},
        ]},
        {"label": "Uanachama", "icon": "id-card", "children": [
            {"label": "Maombi ya Uanachama", "url": "/maombi/"},
            {"label": "Kategoria za Uanachama"}, {"label": "Uhakiki wa Kadi"},
        ]},
        {"label": "Malipo & Michango", "icon": "wallet", "children": [
            {"label": "Malipo ya Ada", "url": "/malipo/"},
            {"label": "Michango", "url": "/michango/"},
            {"label": "Akaunti za Wanachama"}, {"label": "Risiti"},
        ]},
        {"label": "Pointi & Tuzo", "icon": "star", "children": [
            {"label": "Muhtasari wa Pointi"}, {"label": "Kanuni za Pointi"}, {"label": "Tuzo"},
        ]},
        {"label": "Huduma za Ustawi", "icon": "hand-heart", "children": [
            {"label": "Maombi ya Msaada"}, {"label": "Misaada Iliyotolewa"},
        ]},
        {"label": "Maombi ya Msaada", "icon": "heart", "url": "#"},
        {"label": "Matukio", "icon": "calendar", "url": "#"},
        {"label": "Mawasiliano", "icon": "message", "url": "#"},
        {"label": "Nyaraka", "icon": "file", "url": "#"},
        {"label": "Ripoti & Takwimu", "icon": "chart-bar", "url": "#"},
        {"label": "Watumiaji & Ruhusa", "icon": "shield", "url": "#"},
        {"label": "Mipangilio ya Mfumo", "icon": "settings", "url": "#"},
    ]


def nav_member(active="dashboard"):
    return [
        {"label": "Dashibodi", "icon": "dashboard", "url": "/mwanachama/", "active": active == "dashboard"},
        {"label": "Wasifu Wangu", "icon": "user", "url": "#"},
        {"label": "Malipo", "icon": "wallet", "url": "#"},
        {"label": "Pointi & Faida", "icon": "star", "url": "#"},
        {"label": "Matukio", "icon": "calendar", "url": "#"},
        {"label": "Msaada & Maombi", "icon": "hand-heart", "url": "#"},
        {"label": "Familia & Wategemezi", "icon": "users", "url": "#"},
        {"label": "Nyaraka", "icon": "file", "url": "#"},
        {"label": "Taarifa & Matangazo", "icon": "megaphone", "url": "#"},
        {"label": "Mawasiliano", "icon": "phone", "url": "#"},
        {"label": "Mipangilio", "icon": "settings", "url": "#"},
    ]


# ---------------------------------------------------------------------------
#  DASHIBODI KUU (Super Admin)
# ---------------------------------------------------------------------------
def superadmin_dashboard():
    return {
        # -- KPI cards -------------------------------------------------------
        "kpis": [
            {"label": "Jumla ya Wanachama", "value": "6,842", "icon": "users",
             "tint": "green", "delta": "12.5%", "dir": "up", "note": "kutoka mwezi jana"},
            {"label": "Wanachama Hai", "value": "5,931", "icon": "user-check",
             "tint": "navy", "note": "86.7% ya jumla ya wanachama"},
            {"label": "Jumla ya Michango", "value": tzs(136_450_000), "icon": "coins",
             "tint": "gold", "money": True, "delta": "18.4%", "dir": "up", "note": "kutoka mwezi jana"},
            {"label": "Pointi Zilizotolewa", "value": "248,590", "icon": "star",
             "tint": "purple", "delta": "15.7%", "dir": "up", "note": "kutoka mwezi jana"},
            {"label": "Misaada Iliyotolewa", "value": tzs(42_770_000), "icon": "hand-heart",
             "tint": "teal", "money": True, "delta": "5.3%", "dir": "down", "note": "kutoka mwezi jana"},
        ],

        # -- Ukuaji wa Wanachama (line) --------------------------------------
        "growth": {
            "labels": MONTHS_SW,
            "data": [980, 1520, 2180, 2760, 3340, 3780, 4260, 4820, 5310, 5760, 6310, 6842],
        },

        # -- Wanachama kwa Kategoria (donut) ---------------------------------
        "by_category": {
            "id": "chCategory", "title": "Wanachama kwa Kategoria",
            "center_value": "6,842", "center_label": "Jumla",
            "rows": [
                {"label": "Founder",  "value": 156,   "display": "156",   "pct": "2.3",  "color": C["green"]},
                {"label": "Diamond", "value": 312,   "display": "312",   "pct": "4.6",  "color": C["purple"]},
                {"label": "Gold",     "value": 1245,  "display": "1,245", "pct": "18.2", "color": C["gold"]},
                {"label": "Silver",   "value": 2156,  "display": "2,156", "pct": "31.5", "color": C["slate"]},
                {"label": "Bronze",   "value": 2973,  "display": "2,973", "pct": "43.4", "color": C["orange"]},
            ],
        },

        # -- Usajili wa Hivi Karibuni ---------------------------------------
        "recent_members": [
            {"full_name": "Abdulrahman Juma",  "initials": "AJ", "category": "Gold",   "joined": "30 Jul 2026"},
            {"full_name": "Aisha Salum",       "initials": "AS", "category": "Silver", "joined": "30 Jul 2026"},
            {"full_name": "Mohammed Ali",      "initials": "MA", "category": "Bronze", "joined": "29 Jul 2026"},
            {"full_name": "Fatma Said",        "initials": "FS", "category": "Gold",   "joined": "29 Jul 2026"},
            {"full_name": "Yusuf Omary",       "initials": "YO", "category": "Silver", "joined": "28 Jul 2026"},
        ],

        # -- Muhtasari wa Mapato (bar) ---------------------------------------
        "revenue": {
            "labels": MONTHS_SW,
            "data": [18_500_000, 24_200_000, 21_800_000, 27_400_000, 31_200_000, 19_600_000,
                     33_800_000, 25_100_000, 28_900_000, 30_400_000, 36_700_000, 22_300_000],
        },

        # -- Muhtasari wa Malipo (donut) -------------------------------------
        "payment_mix": {
            "id": "chPayments", "title": "Muhtasari wa Malipo", "control": "Mwezi Huu",
            "center_value": "TZS 18,450,000", "center_label": "Jumla",
            "rows": [
                {"label": "Ada za Uanachama", "value": 12_450_000, "display": "12,450,000", "pct": "67.5", "color": C["green"]},
                {"label": "Michango",         "value": 3_250_000,  "display": "3,250,000",  "pct": "17.6", "color": C["navy"]},
                {"label": "Misaada",          "value": 2_150_000,  "display": "2,150,000",  "pct": "11.7", "color": C["gold"]},
                {"label": "Ada Nyingine",     "value": 600_000,    "display": "600,000",    "pct": "3.2",  "color": C["purple"]},
            ],
        },

        # -- Vitendo vya Haraka ----------------------------------------------
        "quick_actions": {
            "title": "Vitendo vya Haraka", "cols": 4,
            "items": [
                {"label": "Ongeza Mwanachama", "icon": "user-plus", "tint": "green"},
                {"label": "Rekodi Malipo",     "icon": "cash",      "tint": "navy"},
                {"label": "Ongeza Mchango",    "icon": "hand-heart","tint": "teal"},
                {"label": "Maombi ya Msaada",  "icon": "heart",     "tint": "purple"},
                {"label": "Ongeza Tukio",      "icon": "calendar",  "tint": "gold"},
                {"label": "Tuma Ujumbe",       "icon": "message",   "tint": "green"},
                {"label": "Pakua Ripoti",      "icon": "download",  "tint": "orange"},
                {"label": "Mipangilio",        "icon": "settings",  "tint": "navy"},
            ],
        },

        # -- Malipo ya Hivi Karibuni -----------------------------------------
        "recent_payments": [
            {"date": "30 Jul 2026", "member": "Mohammed Omari Kapera", "desc": "Ada ya Uanachama",
             "amount": "20,000",  "method": "Mobile Money", "receipt_no": "MUWESTA-R-000245", "status": "Limelipwa"},
            {"date": "30 Jul 2026", "member": "Aisha Salum", "desc": "Mchango",
             "amount": "100,000", "method": "Bank Transfer", "receipt_no": "MUWESTA-R-000244", "status": "Limelipwa"},
            {"date": "29 Jul 2026", "member": "Yusuf Omary", "desc": "Mchango wa Ustawi",
             "amount": "50,000",  "method": "Mobile Money", "receipt_no": "MUWESTA-R-000243", "status": "Limelipwa"},
            {"date": "29 Jul 2026", "member": "Fatma Said", "desc": "Ada ya Uanachama",
             "amount": "20,000",  "method": "Mobile Money", "receipt_no": "MUWESTA-R-000242", "status": "Limelipwa"},
            {"date": "28 Jul 2026", "member": "Abdulrahman Juma", "desc": "Ada ya Uanachama",
             "amount": "20,000",  "method": "Airtel Money", "receipt_no": "MUWESTA-R-000241", "status": "Limelipwa"},
        ],

        # -- Matangazo na Taarifa --------------------------------------------
        "announcements": [
            {"title": "Mkutano Mkuu wa MUWESTA", "icon": "megaphone", "tint": "green",
             "body": "Wote mnakaribishwa kwenye Mkutano Mkuu utakaofanyika Dodoma tarehe 30 Agosti 2026.",
             "date": "30 Jul 2026"},
            {"title": "Fursa za Scholarship 2026", "icon": "book", "tint": "navy",
             "body": "Maombi ya scholarship kwa wanafunzi wa kidato na vyuo yanapokelewa hadi 15 Agosti.",
             "date": "28 Jul 2026"},
            {"title": "Wito wa Misaada", "icon": "hand-heart", "tint": "gold",
             "body": "Tuendelee kusaidia ndugu zetu wenye uhitaji katika mikoa iliyoathirika na mafuriko.",
             "date": "25 Jul 2026"},
        ],
    }


# ---------------------------------------------------------------------------
#  DASHIBODI YA MWANACHAMA
# ---------------------------------------------------------------------------
def member_dashboard():
    return {
        "member": {
            "full_name": "Mohammed Omari Kapera",
            "initials": "MK",
            "membership_no": "MWST/F/000001/2026",
            "account_no": "1100000123",
            "category": "Founder",
            "category_label": "Founder Member",
            "national_id": "19901234567890",
            "phone": "0769 600 102",
            "email": "mohammed.kapera@gmail.com",
            "issued": "30 Aug 2026",
            "valid_range": "2026 - 2031",
            "registered": "30 Aug 2026",
        },

        "kpis": [
            {"label": "Hali ya Uanachama", "value": "Active", "icon": "check-circle",
             "tint": "green", "note": "Uanachama wako ni hai"},
            {"label": "Muda wa Uanachama", "value": "30 Ago 2031", "icon": "calendar",
             "tint": "navy", "money": True, "note": "Uanachama unamalizika"},
            {"label": "Pointi Zako", "value": "4,250", "icon": "star",
             "tint": "gold", "note": "Jumla ya pointi"},
            {"label": "Ada ya Mwezi", "value": tzs(20_000), "icon": "wallet",
             "tint": "orange", "money": True, "note": "Mchango wa kila mwezi"},
            {"label": "Malipo Yanayofuata", "value": "05 Ago 2026", "icon": "clock",
             "tint": "purple", "money": True, "note": "Tarehe ya malipo ijayo"},
            {"label": "Jumla ya Michango", "value": tzs(2_450_000), "icon": "chart-bar",
             "tint": "teal", "money": True, "note": "Michango yote hadi sasa"},
        ],

        "wallet": {
            "balance": tzs(380_000),
            "rows": [
                {"label": "Akiba / Savings",   "value": tzs(250_000)},
                {"label": "Michango ya Ustawi", "value": tzs(80_000)},
                {"label": "Michango Mengine",   "value": tzs(150_000)},
                {"label": "Malipo Yanayosubiri", "value": "TZS 0", "danger": True},
            ],
        },

        "points": {
            "current": "4,250",
            "earned_this_month": "+250",
            "level": "Founder",
            "next_reward_remaining": "750",
            "progress": 85,
        },

        "quick_actions": {
            "title": "Hatua za Haraka", "cols": 4,
            "items": [
                {"label": "Sajili Mwanafamilia", "icon": "users",      "tint": "green"},
                {"label": "Lipa Ada",            "icon": "cash",       "tint": "navy"},
                {"label": "Omba Msaada",         "icon": "hand-heart", "tint": "teal"},
                {"label": "Changia / Donate",    "icon": "heart",      "tint": "red"},
                {"label": "Pakua Cheti",         "icon": "receipt",    "tint": "gold"},
                {"label": "Soma Katiba",         "icon": "book",       "tint": "purple"},
                {"label": "Tuma Maoni",          "icon": "message",    "tint": "orange"},
                {"label": "Sasisha Wasifu",      "icon": "settings",   "tint": "navy"},
            ],
        },

        "transactions": [
            {"date": "30 Jul 2026", "desc": "Ada ya Uanachama (Mwezi)", "amount": "20,000",  "status": "Imelipwa"},
            {"date": "15 Jul 2026", "desc": "Chango la Ustawi",          "amount": "100,000", "status": "Imelipwa"},
            {"date": "01 Jul 2026", "desc": "Mchango wa Kawaida",        "amount": "50,000",  "status": "Imelipwa"},
            {"date": "20 Jun 2026", "desc": "Ada ya Uanachama (Mwezi)",  "amount": "20,000",  "status": "Imelipwa"},
        ],

        "events": [
            {"title": "Semina ya Kiislamu", "when": "09 Ago 2026  |  09:00 AM",
             "venue": "Ukumbi wa MUWESTA - Dodoma", "icon": "mosque", "tint": "green"},
            {"title": "Mkutano Mkuu", "when": "30 Ago 2026  |  10:00 AM",
             "venue": "JNICC Hall - Dodoma", "icon": "users", "tint": "navy"},
            {"title": "Kampeni ya Sadaka", "when": "25 Ago 2026  |  08:00 AM",
             "venue": "Dodoma & Mkoa Mbalimbali", "icon": "hand-heart", "tint": "purple"},
        ],

        "announcements": [
            {"title": "Mradi Mpya wa MUWESTA", "icon": "building", "tint": "green",
             "body": "Mradi wa ujenzi wa shule mpya unaendelea kwa kasi.", "date": "30 Jul 2026"},
            {"title": "Fursa za Masomo", "icon": "book", "tint": "navy",
             "body": "Tuma maombi kwa ajili ya ufadhili wa masomo kabla ya tarehe ya mwisho.", "date": "28 Jul 2026"},
            {"title": "Wito wa Msaada", "icon": "heart", "tint": "gold",
             "body": "Tunaomba mchango kwa ajili ya familia zilizoathirika.", "date": "25 Jul 2026"},
        ],
    }
