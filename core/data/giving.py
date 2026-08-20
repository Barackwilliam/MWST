"""
Katalogi ya michango — aina, kurudia, watoa huduma na fedha.

Vyote vipo hapa ili fomu ya umma, muhtasari na dashibodi visome chanzo
kimoja. Bei za uanachama HAZIPO hapa; zinatoka `members.Category`.

`fund` ya kila aina ya mchango inaunganisha na `finance.Fund` iliyopo
kwenye database. Ikikosekana, mfuko wa jumla unatumika.
"""
from decimal import Decimal


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
#: Michango ya kudumu hulipwa KWA MWEZI. Anayelipia miezi kadhaa mapema
#: hupata punguzo — inampunguzia gharama, na inaipa MUWESTA uhakika wa
#: mapato badala ya kusubiri kila mwezi.
#:
#: `months` ni idadi ya miezi anayolipia mara moja; `discount` ni asilimia
#: inayopunguzwa kwenye jumla. Kiasi anachoingiza ni cha MWEZI MMOJA.
RECURRENCES = [
    {"key": "once",    "months": 1,  "discount": 0,
     "name": "Mara Moja",  "name_en": "One Time",
     "sub": "Mchango wa mara moja",  "sub_en": "A one-off gift"},
    {"key": "monthly", "months": 1,  "discount": 0,
     "name": "Kila Mwezi", "name_en": "Monthly",
     "sub": "Utakumbushwa kila mwezi", "sub_en": "You will be reminded each month"},
    {"key": "m3",      "months": 3,  "discount": 5,
     "name": "Miezi 3",    "name_en": "3 Months",
     "sub": "Punguzo la 5%",  "sub_en": "5% off"},
    {"key": "m6",      "months": 6,  "discount": 8,
     "name": "Miezi 6",    "name_en": "6 Months",
     "sub": "Punguzo la 8%",  "sub_en": "8% off"},
    {"key": "m9",      "months": 9,  "discount": 10,
     "name": "Miezi 9",    "name_en": "9 Months",
     "sub": "Punguzo la 10%", "sub_en": "10% off"},
    {"key": "m12",     "months": 12, "discount": 12,
     "name": "Mwaka 1",    "name_en": "1 Year",
     "sub": "Punguzo la 12%", "sub_en": "12% off"},
]


def recurrence(key):
    """Marudio kwa funguo yake. Isiyojulikana inarudi 'mara moja'."""
    return _pick(RECURRENCES, "key", key) or RECURRENCES[0]


def recurrence_total(amount, key):
    """
    Jumla halisi baada ya miezi na punguzo.

    Mtu anaingiza kiasi cha MWEZI MMOJA. Akichagua miezi 6, analipa
    mara sita, kasoro punguzo la asilimia 8.
    """
    spec = recurrence(key)
    gross = Decimal(str(amount or 0)) * spec["months"]
    net = gross * (Decimal(100) - Decimal(spec["discount"])) / Decimal(100)
    return int(net)

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
    #: hakuna sababu ya kumtaka achague mara mbili hapa.
    {"key": "pesapal",  "name": "Mobile Money na Kadi",
     "name_en": "Mobile Money and Card",
     "sub": "M-Pesa, Airtel, Mixx, HaloPesa, Visa, Mastercard",
     "sub_en": "M-Pesa, Airtel, Mixx, HaloPesa, Visa, Mastercard",
     "group": "online", "gateway": "pesapal", "icon": "wallet"},

    #: Selcom ina faida ya kutuma kidokezo moja kwa moja kwenye simu —
    #: mtu haondoki kwenye tovuti. Code yake iko tayari
    #: (`finance/gateways/selcom.py`), lakini funguo bado hazijakamilika.
    #: Ondoa `"soon": True` na ubadilishe `gateway` kuwa `"selcom"`
    #: zitakapokuwa tayari; hakuna kingine cha kubadilisha.
    {"key": "selcom",   "name": "Lipa kwa Simu (kidokezo)",
     "name_en": "Pay by Phone (prompt)",
     "sub": "Utapokea kidokezo simuni bila kuondoka hapa",
     "sub_en": "You will get a prompt on your phone without leaving this page",
     "group": "bank", "gateway": "", "icon": "phone", "soon": True},

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
#: MUDA WA UANACHAMA NI MIAKA MITATU, na hauhusiani na michango hii.
#: Michango ya mwezi ni mchango wa mwanachama kwa shirika — hairefushi
#: wala haifupishi uanachama. Kuhuisha ni malipo tofauti kabisa
#: (`PAY_KINDS` hapa chini).
#:
#: Mtu anachagua mwenyewe anataka kuchangia miezi mingapi — si kuchagua
#: kati ya vifurushi vilivyopangwa. Anayeweza kuchangia mwezi mmoja tu
#: asizuiwe, na anayetaka kuchangia miaka miwili aweze.
MIN_MONTHS = 1
MAX_MONTHS = 60          # miaka 5 — kikomo cha busara, si sheria

#: Vifungo vya haraka kwenye fomu. Ni njia ya mkato tu; mtu anaweza
#: kuandika namba yoyote kati ya MIN na MAX.
MONTH_SHORTCUTS = [1, 3, 6, 12, 24]

#: Punguzo kwa anayelipa mapema kwa muda mrefu. Limepangwa kwa vipimo,
#: si kwa vifurushi — anayelipia miezi 7 anapata punguzo la miezi 6
#: badala ya kulazimishwa kuchagua 6 au 12.
#:
#: (miezi ya chini, asilimia) — husomwa kutoka juu kwenda chini.
DISCOUNT_TIERS = [
    (12, 15),
    (6,  10),
    (3,   5),
]


def clamp_months(months):
    """Rudisha idadi ya miezi iliyo ndani ya mipaka inayoruhusiwa."""
    try:
        n = int(months)
    except (TypeError, ValueError):
        return MIN_MONTHS
    return max(MIN_MONTHS, min(MAX_MONTHS, n))


def discount_for(months):
    """Asilimia ya punguzo kwa idadi ya miezi husika."""
    n = clamp_months(months)
    for floor, pct in DISCOUNT_TIERS:
        if n >= floor:
            return pct
    return 0


def months_label(months, lang="sw"):
    """Maelezo mafupi ya muda, mfano "Mwaka 1, miezi 6"."""
    n = clamp_months(months)
    english = str(lang).startswith("en")
    if n < 12:
        if english:
            return f"{n} month{'s' if n != 1 else ''}"
        return "Mwezi 1" if n == 1 else f"Miezi {n}"
    years, rest = divmod(n, 12)
    if english:
        out = f"{years} year{'s' if years != 1 else ''}"
        if rest:
            out += f", {rest} month{'s' if rest != 1 else ''}"
        return out
    out = "Mwaka 1" if years == 1 else f"Miaka {years}"
    if rest:
        out += f", miezi {rest}"
    return out


def months_price(monthly_fee, months):
    """
    Bei ya miezi husika baada ya punguzo, imezungushwa hadi shilingi 100.

    `monthly_fee` inatoka kwenye database kama `Decimal`, kwa hiyo tunaibadili
    kuwa `float` kabla ya hesabu — Decimal na float hazichanganyiki.
    """
    n = clamp_months(months)
    gross = float(monthly_fee or 0) * n
    net = gross * (100 - discount_for(n)) / 100.0
    return int(round(net / 100.0) * 100)



# ---------------------------------------------------------------------------
#  Aina ya malipo ya uanachama
#
#  Tofauti hii ni muhimu: moja inagusa muda wa uanachama, nyingine haigusi.
#  Ikichanganyika, mtu angeweza kununua miaka ya uanachama kwa kuchangia —
#  au kuchangia bila kujua kwamba muda wake unaisha.
# ---------------------------------------------------------------------------
TERM_YEARS = 3

PAY_KINDS = [
    {"key": "ada", "icon": "hand-heart",
     "name": "Mchango wa Mwezi", "name_en": "Monthly Contribution",
     "sub": "Mchango wako kama mwanachama. Hauongezi muda wa uanachama.",
     "sub_en": "Your contribution as a member. It does not extend your membership."},
    {"key": "uhuisho", "icon": "id-card",
     "name": "Kuhuisha Uanachama", "name_en": "Renew Membership",
     "sub": "Kipindi kingine cha miaka 3 na kadi mpya.",
     "sub_en": "Another 3-year term and a new card."},
]


def pay_kind(key):
    return _pick(PAY_KINDS, "key", key) or PAY_KINDS[0]

# ---------------------------------------------------------------------------
#  Vipindi vya zamani
#
#  Uanachama uliwahi kuwa wa vifurushi vilivyopangwa (mwezi, mwaka, kisha
#  miaka mitatu). Rekodi za nyuma bado zina funguo hizo, kwa hiyo
#  tunazihifadhi ili malipo ya zamani yasomeke kwa usahihi.
# ---------------------------------------------------------------------------
LEGACY_PERIODS = {
    "once":      {"key": "once",      "months": 0,   "name": "Mara moja"},
    "monthly":   {"key": "monthly",   "months": 1,   "name": "Kila mwezi"},
    "quarterly": {"key": "quarterly", "months": 3,   "name": "Robo mwaka"},
    "biannual":  {"key": "biannual",  "months": 6,   "name": "Nusu mwaka"},
    "annual":    {"key": "annual",    "months": 12,  "name": "Mwaka mmoja"},
    "term1":     {"key": "term1",     "months": 36,  "name": "Miaka 3"},
    "term2":     {"key": "term2",     "months": 72,  "name": "Miaka 6"},
    "term3":     {"key": "term3",     "months": 108, "name": "Miaka 9"},
}


def legacy_months(key):
    """
    Miezi ya rekodi ya zamani kwa funguo yake.

    Funguo isiyotambulika inarudisha sifuri, si kipindi kamili — kumpa
    mtu miezi asiyoilipia ni kosa baya kuliko kutompa chochote.
    """
    spec = LEGACY_PERIODS.get(key)
    return spec["months"] if spec else 0


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


def tx(row, field="name", lang=None):
    """
    Chukua `field` ya lugha inayotumika sasa kutoka kwenye dict.

    Inatumika kwa orodha zilizoandikwa kwenye code (viwango vya pointi,
    aina za michango) ambazo hazipo kwenye database, kwa hiyo haziwezi
    kutumia `Bilingual.tx()` ya modeli.
    """
    from django.utils.translation import get_language

    lang = lang or get_language() or "sw"
    if str(lang).startswith("en"):
        return row.get(f"{field}_en") or row.get(field, "")
    return row.get(field, "")
