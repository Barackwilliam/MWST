"""
Katalogi ya michango — aina, kurudia, watoa huduma na fedha.

Vyote vipo hapa ili fomu ya umma, muhtasari na dashibodi visome chanzo
kimoja. Bei za uanachama HAZIPO hapa; zinatoka `members.Category`.

`fund` ya kila aina ya mchango inaunganisha na `finance.Fund` iliyopo
kwenye database. Ikikosekana, mfuko wa jumla unatumika.
"""

# ---------------------------------------------------------------------------
#  Aina za michango (mockup: "1. CHAGUA AINA YA MCHANGO")
# ---------------------------------------------------------------------------
#: `group` inaunganisha na PURPOSE_GROUPS hapa chini. Aina ni 16 — nyingi
#: mno kuoneshwa kama kadi bila kumchosha mtu — kwa hiyo fomu inatumia
#: droplist yenye vichwa vya makundi badala ya gridi ya kadi.
PURPOSES = [
    {"key": "zakat",       "icon": "coins",      "fund": "jumla", "group": "ibada",
     "name": "Zakat",              "name_en": "Zakat",
     "note": "Faradhi ya mali kwa wenye kustahiki",
     "note_en": "The obligatory alms due on wealth"},
    {"key": "sadaqah",     "icon": "hand-heart", "fund": "jumla", "group": "ibada",
     "name": "Sadaqah (Hiari)",    "name_en": "Sadaqah (Voluntary)",
     "note": "Kusaidia shughuli na miradi ya MUWESTA",
     "note_en": "Supporting MUWESTA activities and projects"},
    {"key": "waqf",        "icon": "mosque",     "fund": "jumla", "group": "ibada",
     "name": "Waqf",               "name_en": "Waqf",
     "note": "Mchango wa kudumu wenye manufaa yanayoendelea",
     "note_en": "An endowment with continuing benefit"},
    {"key": "kafara",      "icon": "shield",     "fund": "jumla", "group": "ibada",
     "name": "Kafara",             "name_en": "Kafara",
     "note": "Fidia kwa mujibu wa Sharia",
     "note_en": "Expiation as prescribed by Sharia"},
    {"key": "iftar",       "icon": "gift",       "fund": "jumla", "group": "ibada",
     "name": "Futari / Iftar",     "name_en": "Iftar",
     "note": "Chakula cha futari kwa wanaofunga",
     "note_en": "Meals for those breaking their fast"},
    {"key": "qurbani",     "icon": "gift",       "fund": "jumla", "group": "ibada",
     "name": "Qurbani",            "name_en": "Qurbani",
     "note": "Kuchinja na kugawa nyama kwa wahitaji",
     "note_en": "Sacrifice and distribution of meat to those in need"},
    {"key": "elimu_dini",  "icon": "book",       "fund": "elimu", "group": "elimu",
     "name": "Elimu ya Kiislamu",  "name_en": "Islamic Education",
     "note": "Madrasa, walimu na vifaa vya kufundishia",
     "note_en": "Madrasas, teachers and teaching materials"},
    {"key": "scholarship", "icon": "trophy",     "fund": "elimu", "group": "elimu",
     "name": "Scholarship za Wanafunzi", "name_en": "Student Scholarships",
     "note": "Ada na vifaa kwa wanafunzi wanaostahili",
     "note_en": "Fees and supplies for deserving students"},
    {"key": "yatima",      "icon": "user",       "fund": "yatima", "group": "huduma",
     "name": "Yatima",             "name_en": "Orphans",
     "note": "Malezi, elimu na mahitaji ya yatima",
     "note_en": "Care, education and needs of orphans"},
    {"key": "afya",        "icon": "activity",   "fund": "afya", "group": "huduma",
     "name": "Afya na Matibabu",   "name_en": "Health and Treatment",
     "note": "Matibabu, dawa na kambi za afya",
     "note_en": "Treatment, medicines and health camps"},
    {"key": "maji",        "icon": "globe",      "fund": "maji", "group": "huduma",
     "name": "Mradi wa Visima",    "name_en": "Water Wells",
     "note": "Uchimbaji wa visima na maji safi",
     "note_en": "Borehole drilling and clean water"},
    {"key": "chakula",     "icon": "gift",       "fund": "jumla", "group": "huduma",
     "name": "Chakula kwa Wahitaji", "name_en": "Food for Those in Need",
     "note": "Vyakula kwa familia zenye uhitaji",
     "note_en": "Food parcels for families in need"},
    {"key": "misikiti",    "icon": "mosque",     "fund": "ujenzi", "group": "miradi",
     "name": "Ujenzi wa Misikiti", "name_en": "Mosque Construction",
     "note": "Ujenzi na ukarabati wa misikiti",
     "note_en": "Building and renovating mosques"},
    {"key": "maendeleo",   "icon": "building",   "fund": "jumla", "group": "miradi",
     "name": "Miradi ya Maendeleo", "name_en": "Development Projects",
     "note": "Miradi ya muda mrefu ya jamii",
     "note_en": "Long-term community projects"},
    {"key": "dharura",     "icon": "alert",      "fund": "dharura", "group": "nyingine",
     "name": "Misaada ya Dharura", "name_en": "Emergency Relief",
     "note": "Mafuriko, ukame na majanga mengine",
     "note_en": "Floods, drought and other disasters"},
    {"key": "jumla",       "icon": "heart",      "fund": "jumla", "group": "nyingine",
     "name": "Michango ya Jumla",  "name_en": "General Donation",
     "note": "MUWESTA itaelekeza pale panapohitajika zaidi",
     "note_en": "MUWESTA will direct it where it is needed most"},
]

#: Vichwa vya droplist. Mpangilio hapa ndio unaoonekana kwenye fomu.
PURPOSE_GROUPS = [
    {"key": "ibada",    "name": "Faradhi na Ibada",   "name_en": "Obligatory & Worship"},
    {"key": "elimu",    "name": "Elimu",              "name_en": "Education"},
    {"key": "huduma",   "name": "Huduma za Jamii",    "name_en": "Community Services"},
    {"key": "miradi",   "name": "Ujenzi na Miradi",   "name_en": "Construction & Projects"},
    {"key": "nyingine", "name": "Nyingine",           "name_en": "Other"},
]

# ---------------------------------------------------------------------------
#  Kurudia (mockup: "3. RUDIA MCHANGO")
# ---------------------------------------------------------------------------
RECURRENCES = [
    {"key": "once",      "name": "Mara Moja",       "name_en": "One Time"},
    {"key": "weekly",    "name": "Kila Wiki",       "name_en": "Weekly"},
    {"key": "monthly",   "name": "Kila Mwezi",      "name_en": "Monthly"},
    {"key": "quarterly", "name": "Kila Robo Mwaka", "name_en": "Quarterly"},
    {"key": "biannual",  "name": "Kila Nusu Mwaka", "name_en": "Every Six Months"},
    {"key": "annual",    "name": "Kila Mwaka",      "name_en": "Annually"},
]

# ---------------------------------------------------------------------------
#  Viwango vya haraka (TZS)
# ---------------------------------------------------------------------------
PRESETS = [5000, 10000, 20000, 50000, 100000, 200000, 500000]

# ---------------------------------------------------------------------------
#  Watoa huduma wa malipo
#
#  Kila njia hapa INAFANYA KAZI. `gateway` inaeleza inavyokamilishwa:
#
#    "pesapal" -> mtu anapelekwa ukurasa wa Pesapal na kumalizia huko.
#                 Chaguo lake hapa ni dokezo tu; njia halisi anaichagua
#                 tena Pesapal, ambako ndiko malipo yanapofanyika.
#    "manual"  -> mtu anahamisha pesa mwenyewe. Mchango unabaki `pending`
#                 hadi afisa athibitishe kupokelewa. Hakuna kinachodai
#                 kwamba malipo yamekamilika kabla ya hapo.
#
#  Njia isiyo na njia ya kukamilishwa haiwekwi hapa. PayPal iliondolewa kwa
#  sababu hiyo — ilikuwa inaonekana kwenye fomu bila kuwa na kitu nyuma yake.
#
#  Namba za kadi HAZIKUSANYWI hapa wala popote (PCI-DSS).
# ---------------------------------------------------------------------------
#: `soon: True` inamaanisha njia inaonekana kwenye fomu lakini HAIWEZI
#: kuchaguliwa — mtu anaambiwa inakuja hivi punde. Hii ni bora kuliko
#: kuificha kabisa: mtu anayeitafuta anajua ipo njiani badala ya kudhani
#: MUWESTA haipokei kabisa. Fomu inakataa `soon` upande wa seva pia,
#: kwa hiyo hakuna anayeweza kuipitisha kwa kuhariri HTML.
PROVIDERS = [
    #: Pesapal inashughulikia mitandao YOTE ya simu na kadi kwa mara moja.
    #: Mtu anachagua mtandao wake akiwa kwenye ukurasa wa Pesapal, hivyo
    #: hakuna sababu ya kumtaka achague mara mbili.
    {"key": "pesapal",  "name": "Pesapal",  "name_en": "Pesapal",
     "sub": "M-Pesa, Airtel, Mixx, HaloPesa, Visa, Mastercard",
     "sub_en": "M-Pesa, Airtel, Mixx, HaloPesa, Visa, Mastercard",
     "group": "online", "gateway": "pesapal", "icon": "wallet"},

    {"key": "bank",     "name": "Uhamisho wa Benki", "name_en": "Bank Transfer",
     "sub": "CRDB, NMB, NBC, TPB, Exim",
     "sub_en": "CRDB, NMB, NBC, TPB, Exim",
     "group": "bank", "gateway": "manual", "icon": "building", "soon": True},

    {"key": "paypal",   "name": "PayPal", "name_en": "PayPal",
     "sub": "Kwa wachangiaji wa nje ya nchi",
     "sub_en": "For donors outside Tanzania",
     "group": "bank", "gateway": "", "icon": "globe", "soon": True},
]

PROVIDER_GROUPS = [
    {"key": "online", "name": "Inapatikana sasa",  "name_en": "Available now", "icon": "wallet"},
    {"key": "bank",   "name": "Zinakuja hivi punde", "name_en": "Coming soon", "icon": "clock"},
]


def active_providers():
    """Njia zinazoweza kuchaguliwa sasa hivi (bila zile za `soon`)."""
    return [p for p in PROVIDERS if not p.get("soon")]


def is_soon(key):
    spec = provider(key)
    return bool(spec and spec.get("soon"))

# ---------------------------------------------------------------------------
#  Fedha
#
#  Viwango ni vya MFANO tu na havisasishwi. Vinatumika kubadilisha kiasi
#  kwenda TZS ili kumbukumbu zote ziwe kwa sarafu moja. Ukiunganisha
#  gateway halisi, chukua kiwango kutoka kwake badala ya hapa.
# ---------------------------------------------------------------------------
CURRENCIES = [
    {"code": "TZS", "name": "Tanzanian Shilling", "symbol": "TSh", "rate": 1},
    {"code": "USD", "name": "US Dollar",          "symbol": "$",   "rate": 2615},
    {"code": "EUR", "name": "Euro",               "symbol": "\u20ac", "rate": 2840},
    {"code": "GBP", "name": "British Pound",      "symbol": "\u00a3", "rate": 3320},
    {"code": "AED", "name": "UAE Dirham",         "symbol": "AED", "rate": 712},
    {"code": "SAR", "name": "Saudi Riyal",        "symbol": "SAR", "rate": 697},
    {"code": "KES", "name": "Kenyan Shilling",    "symbol": "KSh", "rate": 20},
]


def _pick(items, key, value):
    for item in items:
        if item[key] == value:
            return item
    return None


def localise(items, lang):
    """
    Rudisha nakala zenye `name`/`note`/`sub` za lugha husika.

    Ikikosekana tafsiri ya Kiingereza, Kiswahili kinabaki — bora mtu aone
    neno la Kiswahili kuliko sehemu tupu.
    """
    english = str(lang).startswith("en")
    out = []
    for item in items:
        row = dict(item)
        if english:
            for field in ("name", "note", "sub"):
                if field in item and f"{field}_en" in item:
                    row[field] = item[f"{field}_en"]
        out.append(row)
    return out


def purpose(key):
    return _pick(PURPOSES, "key", key)


def provider(key):
    return _pick(PROVIDERS, "key", key)


def gateway_for(key):
    """
    Njia inayotumika kukamilisha malipo ya mtoa huduma huyu.

    Hurudisha "pesapal", "manual", au "" kama ufunguo hautambuliki.
    Kutorudisha kitu kwa ufunguo usiojulikana ni makusudi — bora malipo
    yakatae kuanza kuliko yaende njia isiyo sahihi kimya kimya.
    """
    spec = provider(key)
    return spec.get("gateway", "") if spec else ""


def currency(code):
    return _pick(CURRENCIES, "code", code) or CURRENCIES[0]


def to_tzs(amount, code):
    """Badilisha kiasi kwenda TZS kwa kiwango cha mfano."""
    return (amount or 0) * currency(code)["rate"]


# ---------------------------------------------------------------------------
#  Vipindi vya kulipa ada ya uanachama
#
#  Kila kipindi kinatokana na ada ya mwezi ya daraja (`Category.monthly_fee`),
#  si namba zilizoandikwa mkononi — hivyo bei ikibadilika sehemu moja tu
#  ndiyo inayobadilika. Punguzo linahamasisha malipo ya muda mrefu.
# ---------------------------------------------------------------------------
#: Uanachama hudumu MIAKA MITATU. Mtu hulipa kipindi kimoja au zaidi;
#: hakuna malipo ya mwezi mmoja au mwaka mmoja, kwa sababu uanachama
#: wenyewe hauishi kwa muda huo.
TERM_YEARS = 3
TERM_MONTHS = TERM_YEARS * 12

PERIODS = [
    {"key": "term1", "months": 36,  "terms": 1, "discount": 0,
     "name": "Miaka 3",  "name_en": "3 Years",
     "sub": "Kipindi kimoja",  "sub_en": "One term"},
    {"key": "term2", "months": 72,  "terms": 2, "discount": 5,
     "name": "Miaka 6",  "name_en": "6 Years",
     "sub": "Vipindi 2 — punguzo 5%",  "sub_en": "2 terms — 5% off"},
    {"key": "term3", "months": 108, "terms": 3, "discount": 10,
     "name": "Miaka 9",  "name_en": "9 Years",
     "sub": "Vipindi 3 — punguzo 10%", "sub_en": "3 terms — 10% off"},
]

#: Vipindi vya zamani (mwezi, robo mwaka, mwaka) viliondolewa uanachama
#: ulipowekwa kuwa wa miaka mitatu. Rekodi za nyuma bado zina funguo
#: hizi, kwa hiyo tunazihifadhi hapa ili `period()` isizihesabu kama
#: kipindi kamili cha miaka mitatu na kumpa mtu miaka asiyoilipia.
LEGACY_PERIODS = {
    "once":      {"key": "once",      "months": 0,  "terms": 0, "discount": 0,
                  "name": "Mara moja",   "name_en": "One time"},
    "monthly":   {"key": "monthly",   "months": 1,  "terms": 0, "discount": 0,
                  "name": "Kila mwezi",  "name_en": "Monthly"},
    "quarterly": {"key": "quarterly", "months": 3,  "terms": 0, "discount": 5,
                  "name": "Robo mwaka",  "name_en": "Quarterly"},
    "biannual":  {"key": "biannual",  "months": 6,  "terms": 0, "discount": 10,
                  "name": "Nusu mwaka",  "name_en": "Half year"},
    "annual":    {"key": "annual",    "months": 12, "terms": 0, "discount": 15,
                  "name": "Mwaka mmoja", "name_en": "One year"},
}


def period(key):
    """
    Kipindi cha malipo kwa funguo yake.

    Funguo isiyotambulika HAIRUDISHI kipindi kamili — hiyo ingempa mtu
    miaka mitatu kwa rekodi ya zamani ya mwezi mmoja. Badala yake
    tunaangalia vipindi vya zamani, kisha tunarudisha sifuri.
    """
    spec = _pick(PERIODS, "key", key)
    if spec:
        return spec
    return LEGACY_PERIODS.get(key, LEGACY_PERIODS["once"])


def period_price(monthly_fee, key):
    """
    Bei ya kipindi baada ya punguzo, imezungushwa hadi shilingi 100.

    `monthly_fee` inatoka kwenye database kama `Decimal`, kwa hiyo tunaibadili
    kuwa `float` kabla ya hesabu — Decimal na float hazichanganyiki.
    """
    spec = period(key)
    gross = float(monthly_fee or 0) * spec["months"]
    net = gross * (100 - spec["discount"]) / 100.0
    return int(round(net / 100.0) * 100)


# ---------------------------------------------------------------------------
#  Aina ya mwanachama / mtoaji (mockup: "MEMBER / DONOR TYPE")
# ---------------------------------------------------------------------------
#: Ada hulipwa na watu wa aina mbili tu. "Mhisani" na "Taasisi" ziliondolewa
#: kwa sababu hazina uanachama wa kusogeza — wanaotaka kutoa pesa bila
#: uanachama wanatumia ukurasa wa michango (/changia/).
PAYER_TYPES = [
    {"key": "new",    "name": "Mwanachama mpya", "name_en": "New member",
     "sub": "Nina namba ya ombi (APP/...)", "sub_en": "I have an application number (APP/...)"},
    {"key": "member", "name": "Mwanachama",      "name_en": "Existing member",
     "sub": "Nina namba ya uanachama",     "sub_en": "I have a membership number"},
]
