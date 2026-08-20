"""Maudhui ya kurasa za tovuti ya umma."""
from .common import tzs


def menu():
    """Menyu ya header na drawer."""
    return [
        {"key": "home",        "label": "Nyumbani",    "icon": "dashboard", "url": "/"},
        {"key": "uanachama",   "label": "Uanachama",   "icon": "id-card",   "url": "/uanachama/"},
        {"key": "huduma",      "label": "Huduma",      "icon": "hand-heart", "url": "/huduma/"},
        {"key": "vifurushi",   "label": "Vifurushi",   "icon": "wallet",    "url": "/vifurushi/"},
        #: Ukurasa wa nyaraka ndio unaoeleza MUWESTA ni nini, katiba yake
        #: na jinsi mfumo huu unavyofanya kazi — kwa hiyo "Kuhusu Sisi"
        #: inaelekeza hapo badala ya kuwa na ukurasa wa pili unaorudia.
        {"key": "kuhusu",      "label": "Kuhusu",      "icon": "info",      "url": "/kuhusu/"},
        {"key": "mawasiliano", "label": "Wasiliana",  "icon": "phone",     "url": "/mawasiliano/"},
        #: `cta` inavifanya vionekane kama vitufe vya dhahabu, si viungo
        #: vya kawaida. Hivi ndivyo tunavyotaka mtu abofye.
        {"key": "changia",     "label": "Changia",     "icon": "heart",     "url": "/changia/",
         "cta": True},
        {"key": "lipa",        "label": "Lipa",        "icon": "coins",     "url": "/lipa/",
         "cta": True},
    ]


def footer_menu():
    """Viungo vya footer - kurasa zote zinabaki zinapatikana."""
    return [
        {"label": "Nyumbani",    "url": "/"},
        {"label": "Kuhusu Sisi", "url": "/kuhusu/"},
        {"label": "Uanachama",   "url": "/uanachama/"},
        {"label": "Vifurushi na Ada", "url": "/vifurushi/"},
        {"label": "Changia",     "url": "/changia/"},
        {"label": "Lipa Ada",    "url": "/lipa/"},
        {"label": "Huduma Zetu", "url": "/huduma/"},
        {"label": "Habari",      "url": "/habari/"},
        {"label": "Matukio",     "url": "/matukio-yetu/"},
        {"label": "Picha na Video", "url": "/picha/"},
        {"label": "Mawasiliano", "url": "/mawasiliano/"},
    ]


# ===========================================================================
#  KUHUSU SISI
# ===========================================================================
def kuhusu():
    return {
        "hero": {
            "eyebrow": "Kuhusu Sisi", "scene": "msikiti",
            "title": "Historia, Dira na Dhamira ya MUWESTA",
            "text": "Muslim Welfare Society of Tanzania ni jumuiya ya kijamii inayolenga "
                    "kuinua hali ya maisha ya jamii kupitia elimu, afya, ustawi na miradi "
                    "ya maendeleo endelevu.",
        },
        "pillars": [
            {"title": "Dira Yetu", "icon": "target", "tint": "green",
             "text": "Kuwa jumuiya kinara ya huduma za kijamii Tanzania, inayoaminika na "
                     "kuchangia maendeleo endelevu ya binadamu."},
            {"title": "Dhamira Yetu", "icon": "heart", "tint": "navy",
             "text": "Kutoa huduma za elimu, afya, ustawi na uwezeshaji kiuchumi kwa mujibu "
                     "wa maadili ya Kiislamu, bila ubaguzi."},
            {"title": "Maadili Yetu", "icon": "shield", "tint": "gold",
             "text": "Imani, Huruma, Huduma na Maendeleo. Haya ndiyo yanayoongoza kila "
                     "uamuzi na kila huduma tunayoitoa."},
        ],
        "counters": [
            {"value": 142718, "label": "Wanachama Nchini Kote"},
            {"value": 26,     "label": "Mikoa Tunayofanya Kazi"},
            {"value": 184,    "label": "Wilaya Tulizofikia"},
            {"value": 48,     "label": "Miradi Inayoendelea"},
        ],
        "timeline": [
            {"year": "2015", "title": "Kuanzishwa kwa MUWESTA",
             "text": "Jumuiya ilianzishwa Dodoma na wanachama waanzilishi 42 wenye lengo la kusaidia jamii."},
            {"year": "2018", "title": "Upanuzi wa Kitaifa",
             "text": "MUWESTA ilifungua matawi katika mikoa 12 na kuanzisha mfumo wa uanachama wa kudumu."},
            {"year": "2021", "title": "Miradi ya Elimu na Afya",
             "text": "Ujenzi wa shule tatu na vituo viwili vya afya ulikamilika katika mikoa ya kati."},
            {"year": "2024", "title": "Mpango wa Ustawi wa Yatima",
             "text": "Mpango wa kudumu wa kusaidia yatima na wajane ulizinduliwa katika mikoa yote."},
            {"year": "2026", "title": "Mfumo wa Kidijitali",
             "text": "Uzinduzi wa mfumo wa kidijitali wa usimamizi wa uanachama, malipo na michango."},
        ],
        "leaders": [
            {"initials": "MK", "name": "Mohammed Omari Kapera", "role": "Mwenyekiti"},
            {"initials": "AS", "name": "Ali H. Suleiman", "role": "Katibu Mkuu"},
            {"initials": "FH", "name": "Fatma H. Ali", "role": "Mweka Hazina"},
            {"initials": "JK", "name": "Juma K. Abdallah", "role": "Afisa Miradi"},
        ],
        "faqs": [
            {"q": "MUWESTA ni nini?",
             "a": "MUWESTA ni jumuiya ya kijamii isiyo ya kiserikali inayotoa huduma za elimu, "
                  "afya, ustawi na uwezeshaji kiuchumi kwa jamii ya Watanzania."},
            {"q": "Je, ni lazima uwe Mwislamu kupata huduma?",
             "a": "Hapana. Huduma zetu zinatolewa kwa kila mwenye uhitaji bila kujali dini, "
                  "kabila au eneo analotoka."},
            {"q": "Fedha za jumuiya zinatoka wapi?",
             "a": "Kutoka ada za wanachama, michango ya hiari, Zaka, Sadaqa, Waqf na "
                  "ufadhili wa mashirika washirika ya ndani na kimataifa."},
            {"q": "Nawezaje kufuatilia matumizi ya michango yangu?",
             "a": "Kila mwanachama ana akaunti kwenye mfumo inayoonyesha michango yake yote "
                  "na ripoti za matumizi zinachapishwa kila mwaka."},
        ],
    }


# ===========================================================================
#  UANACHAMA
# ===========================================================================
def uanachama():
    return {
        "hero": {
            "eyebrow": "Uanachama", "scene": "jamii",
            "title": "Jiunge na Familia ya MUWESTA",
            "text": "Uanachama wa MUWESTA unakupa fursa ya kushiriki katika huduma za kijamii, "
                    "kupata msaada wa ustawi, na kujenga jamii bora kwa pamoja.",
        },
        "benefits": [
            {"title": "Kadi ya Kidijitali", "icon": "id-card", "tint": "green",
             "text": "Kadi yenye QR code inayothibitisha uanachama wako popote."},
            {"title": "Msaada wa Ustawi", "icon": "hand-heart", "tint": "navy",
             "text": "Fursa ya kuomba msaada wa dharura, matibabu au elimu."},
            {"title": "Pointi na Tuzo", "icon": "star", "tint": "gold",
             "text": "Pata pointi kwa kila mchango na ushiriki, kisha ubadilishe na tuzo."},
            {"title": "Akaunti Yako", "icon": "wallet", "tint": "purple",
             "text": "Akaunti binafsi inayoonyesha michango, malipo na salio lako."},
            {"title": "Matukio na Mafunzo", "icon": "calendar", "tint": "teal",
             "text": "Alika kwenye semina, mafunzo na mikutano ya jumuiya."},
            {"title": "Sauti kwenye Maamuzi", "icon": "users", "tint": "orange",
             "text": "Haki ya kupiga kura kwenye Mkutano Mkuu wa mwaka."},
        ],
        # ONYO: hizi ni thamani za akiba tu. Bei halisi zinatoka
        # `members.Category` kupitia `queries.public_uanachama()`.
        # Kama unabadilisha bei, ibadilishe kwenye database/migration,
        # si hapa.
        "tiers": [
            {"name": "Bronze", "price": tzs(10_000), "per": "kwa mwezi", "featured": False,
             "items": ["Kadi ya kidijitali", "Akaunti binafsi",
                       "Taarifa na matangazo", "Pointi 10 kwa kila malipo"]},
            {"name": "Silver", "price": tzs(25_000), "per": "kwa mwezi", "featured": False,
             "items": ["Faida zote za Bronze", "Msaada wa ustawi", "Alika kwenye mafunzo",
                       "Pointi 25 kwa kila malipo"]},
            {"name": "Gold", "price": tzs(50_000), "per": "kwa mwezi", "featured": True,
             "items": ["Faida zote za Silver", "Kipaumbele kwenye misaada",
                       "Cheti cha uanachama", "Pointi 50 kwa kila malipo",
                       "Haki ya kupiga kura"]},
            {"name": "Diamond", "price": tzs(100_000), "per": "kwa mwezi", "featured": False,
             "items": ["Faida zote za Gold", "Utambulisho kwenye ripoti ya mwaka",
                       "Ushauri wa kifedha", "Pointi 150 kwa kila malipo",
                       "Nafasi kwenye kamati"]},
            {"name": "Tanzanite", "price": tzs(200_000), "per": "kwa mwezi", "featured": False,
             "items": ["Faida zote za Diamond", "Utambulisho wa kudumu",
                       "Nafasi kwenye Bodi ya Wadhamini", "Kadi maalum ya Tanzanite"]},
        ],
        "steps": [
            {"n": 1, "title": "Jaza Fomu", "text": "Jaza taarifa zako binafsi na za mawasiliano mtandaoni.",
             "icon": "file"},
            {"n": 2, "title": "Chagua Aina", "text": "Chagua aina ya uanachama inayokufaa: Bronze hadi Diamond.",
             "icon": "star"},
            {"n": 3, "title": "Lipa Ada", "text": "Lipa kwa M-Pesa, Airtel Money, Tigo Pesa au benki.",
             "icon": "wallet"},
            {"n": 4, "title": "Pokea Kadi", "text": "Pokea namba ya uanachama na kadi ya kidijitali yenye QR.",
             "icon": "id-card"},
        ],
        "points_rules": [
            {"activity": "Kulipa ada kwa wakati", "points": "10"},
            {"activity": "Mwaka mmoja bila kukatiza", "points": "100"},
            {"activity": "Mchango wa hiari", "points": "1 kwa kila TZS 10,000"},
            {"activity": "Kujitolea kwenye shughuli", "points": "20 - 100"},
            {"activity": "Kuhudhuria Mkutano Mkuu", "points": "20"},
            {"activity": "Kumleta mwanachama mpya", "points": "50"},
            {"activity": "Kuhudhuria mafunzo au semina", "points": "15"},
        ],
    }


# ===========================================================================
#  HUDUMA ZETU
# ===========================================================================
def huduma():
    return {
        "hero": {
            "eyebrow": "Huduma Zetu", "scene": "jamii",
            "title": "Huduma Zinazogusa Maisha",
            "text": "Tunatoa huduma katika maeneo sita makuu yanayolenga kuinua hali ya "
                    "maisha ya jamii kwa njia endelevu.",
        },
        "services": [
            {"title": "Elimu na Mafunzo", "icon": "book", "tint": "green", "cat": "elimu", "scene": "elimu",
             "text": "Ufadhili wa masomo, ujenzi wa madarasa, vifaa vya shule na mafunzo ya ufundi kwa vijana.",
             "stats": "1,240 wanafunzi wamefadhiliwa"},
            {"title": "Huduma za Afya", "icon": "heart", "tint": "red", "cat": "afya", "scene": "afya",
             "text": "Kambi za upimaji afya bure, msaada wa matibabu, na ujenzi wa vituo vya afya vijijini.",
             "stats": "18 kambi za afya mwaka huu"},
            {"title": "Ustawi wa Jamii", "icon": "hand-heart", "tint": "navy", "cat": "ustawi", "scene": "yatima",
             "text": "Msaada kwa yatima, wajane, wazee na familia zilizoathirika na majanga.",
             "stats": "2,450 wanufaika kwa mwezi"},
            {"title": "Maji Safi na Salama", "icon": "globe", "tint": "teal", "cat": "miradi", "scene": "maji",
             "text": "Uchimbaji wa visima na ujenzi wa miundombinu ya maji katika maeneo yenye uhaba.",
             "stats": "34 visima vimechimbwa"},
            {"title": "Uwezeshaji Kiuchumi", "icon": "briefcase", "tint": "gold", "cat": "uchumi", "scene": "uchumi",
             "text": "Mikopo midogo, mafunzo ya ujasiriamali na vikundi vya akiba kwa wanawake na vijana.",
             "stats": "860 wajasiriamali wamewezeshwa"},
            {"title": "Ujenzi wa Vituo vya Ibada", "icon": "mosque", "tint": "purple", "cat": "miradi", "scene": "msikiti",
             "text": "Ujenzi na ukarabati wa misikiti, madrasa na vituo vya elimu ya dini.",
             "stats": "12 miradi imekamilika"},
        ],
        "filters": [
            {"key": "all", "label": "Zote"}, {"key": "elimu", "label": "Elimu"},
            {"key": "afya", "label": "Afya"}, {"key": "ustawi", "label": "Ustawi"},
            {"key": "miradi", "label": "Miradi"}, {"key": "uchumi", "label": "Uchumi"},
        ],
        "projects": [
            {"title": "Ujenzi wa Shule ya Msingi", "place": "Dodoma", "pct": 60, "scene": "ujenzi",
             "raised": tzs(120_000_000), "goal": "200,000,000"},
            {"title": "Maji Safi kwa Jamii", "place": "Singida", "pct": 57, "scene": "maji",
             "raised": tzs(85_500_000), "goal": "150,000,000"},
            {"title": "Wafadhili wa Yatima", "place": "Mikoa yote", "pct": 60, "scene": "yatima",
             "raised": tzs(72_300_000), "goal": "120,000,000"},
        ],
        "impact": [
            {"value": 2450, "label": "Wanufaika kwa Mwezi"},
            {"value": 48,   "label": "Miradi Inayoendelea"},
            {"value": 34,   "label": "Visima vya Maji"},
            {"value": 1240, "label": "Wanafunzi Waliofadhiliwa"},
        ],
    }


# ===========================================================================
#  HABARI
# ===========================================================================
def habari():
    return {
        "hero": {
            "eyebrow": "Habari", "scene": "mkutano",
            "title": "Habari na Taarifa za MUWESTA",
            "text": "Fuatilia shughuli, miradi, matangazo na fursa mbalimbali kutoka MUWESTA.",
        },
        "featured": {
            "title": "MUWESTA yatoa msaada kwa familia zilizoathiriwa na mafuriko Dodoma",
            "date": "30 Julai 2026", "cat": "Misaada",
            "text": "MUWESTA imekabidhi msaada wa vyakula, mavazi na vifaa muhimu kwa familia 120 "
                    "zilizoathirika na mafuriko katika wilaya za Chamwino na Bahi. Msaada huu "
                    "una thamani ya zaidi ya TZS 85 milioni na umetolewa kwa ushirikiano na "
                    "wadau wa ndani na kimataifa.",
        },
        "filters": [
            {"key": "all", "label": "Zote"}, {"key": "misaada", "label": "Misaada"},
            {"key": "elimu", "label": "Elimu"}, {"key": "miradi", "label": "Miradi"},
            {"key": "matangazo", "label": "Matangazo"},
        ],
        "items": [
            {"title": "Programu ya Scholarship 2026/2027", "date": "28 Julai 2026",
             "cat": "elimu", "cat_label": "Elimu", "scene": "elimu",
             "text": "Maombi ya scholarship kwa wanafunzi wa Kidato na Vyuo yanakaribishwa hadi 31 Agosti 2026."},
            {"title": "Semina ya Uongozi na Maadili ya Kiislamu", "date": "20 Julai 2026",
             "cat": "matangazo", "cat_label": "Matangazo", "scene": "mkutano",
             "text": "Semina hii inalenga kuwajengea uwezo viongozi waamini katika uongozi bora na maadili."},
            {"title": "Ujenzi wa Zahanati Dodoma waingia hatua ya mwisho", "date": "18 Julai 2026",
             "cat": "miradi", "cat_label": "Miradi", "scene": "ujenzi",
             "text": "Ujenzi wa zahanati ya Nkuhungu umefikia asilimia 85 na unatarajiwa kukamilika Oktoba."},
            {"title": "Ugawaji wa vifaa vya elimu kwa shule 15", "date": "15 Julai 2026",
             "cat": "elimu", "cat_label": "Elimu", "scene": "elimu",
             "text": "Vitabu, madawati na vifaa vya maabara vimekabidhiwa kwa shule 15 mkoani Mwanza."},
            {"title": "Kambi ya upimaji afya bure Nkuhungu", "date": "10 Julai 2026",
             "cat": "misaada", "cat_label": "Misaada", "scene": "sadaka",
             "text": "Zaidi ya watu 800 walipimwa shinikizo la damu, kisukari na macho bila malipo."},
            {"title": "Mkutano wa wadau kuhusu miradi ya maji", "date": "05 Julai 2026",
             "cat": "miradi", "cat_label": "Miradi", "scene": "ujenzi",
             "text": "Wadau kutoka mashirika manne walikutana kujadili upanuzi wa miradi ya visima."},
        ],
        "gallery": [
            {"scene": "sadaka", "cap": "Misaada kwa Wenye Mahitaji", "count": "32 Picha"},
            {"scene": "elimu", "cap": "Elimu na Mafunzo", "count": "28 Picha"},
            {"scene": "mkutano", "cap": "Matukio na Mikutano", "count": "45 Picha"},
            {"scene": "afya", "cap": "Huduma za Afya", "count": "19 Picha"},
            {"scene": "ujenzi", "cap": "Miradi ya Maendeleo", "count": "24 Picha"},
            {"scene": "maji", "cap": "Mazingira na Uhamasishaji", "count": "17 Picha"},
        ],
    }


# ===========================================================================
#  MATUKIO (umma)
# ===========================================================================
def matukio_umma():
    return {
        "hero": {
            "eyebrow": "Matukio", "scene": "tukio",
            "title": "Matukio na Shughuli za MUWESTA",
            "text": "Jiunge nasi kwenye semina, mikutano, mafunzo na shughuli za kijamii "
                    "zinazofanyika nchini kote.",
        },
        "upcoming": [
            {"d": "15", "m": "MEI", "y": "2026", "title": "Semina ya Uongozi na Maadili ya Kiislamu",
             "venue": "Ukumbi wa MUWESTA - Dodoma", "time": "08:00 AM - 02:00 PM",
             "status": "Inajayo", "badge": "ok", "scene": "mkutano", "cat": "semina", "cat_label": "Semina",
             "text": "Semina ya siku moja kwa viongozi wa matawi na wanachama wanaotaka kuongoza."},
            {"d": "28", "m": "MEI", "y": "2026", "title": "Mkutano Mkuu wa MUWESTA",
             "venue": "JNICC Hall - Dodoma", "time": "09:00 AM - 01:00 PM",
             "status": "Umealikwa", "badge": "warn", "scene": "mkutano", "cat": "mkutano", "cat_label": "Mkutano",
             "text": "Mkutano Mkuu wa mwaka wenye taarifa ya utendaji, ripoti ya fedha na uchaguzi."},
            {"d": "10", "m": "JUN", "y": "2026", "title": "Zoezi la Upimaji Afya Bure",
             "venue": "Kituo cha Afya - Nkuhungu", "time": "08:00 AM - 04:00 PM",
             "status": "Inajayo", "badge": "ok", "scene": "afya", "cat": "afya", "cat_label": "Afya",
             "text": "Upimaji wa shinikizo la damu, kisukari, macho na ushauri wa lishe bila malipo."},
            {"d": "05", "m": "AGO", "y": "2026", "title": "Kongamano la Elimu ya Kiislamu",
             "venue": "Ukumbi wa AICC - Dodoma", "time": "09:00 AM - 05:00 PM",
             "status": "Inajayo", "badge": "ok", "scene": "tukio", "cat": "kongamano", "cat_label": "Kongamano",
             "text": "Kongamano la kitaifa linalowaleta pamoja wasomi na walimu wa dini."},
            {"d": "12", "m": "AGO", "y": "2026", "title": "Mafunzo ya Uongozi kwa Vijana",
             "venue": "Ukumbi wa CCM - Arusha", "time": "09:00 AM - 04:00 PM",
             "status": "Inajayo", "badge": "ok", "scene": "elimu", "cat": "mafunzo", "cat_label": "Mafunzo",
             "text": "Mafunzo ya siku mbili kwa vijana wenye umri wa miaka 18 hadi 35."},
            {"d": "18", "m": "AGO", "y": "2026", "title": "Shughuli ya Kuwasaidia Yatima",
             "venue": "Dar es Salaam", "time": "08:00 AM - 02:00 PM",
             "status": "Inajayo", "badge": "ok", "scene": "yatima", "cat": "ustawi", "cat_label": "Ustawi",
             "text": "Ugawaji wa mahitaji ya shule na chakula kwa yatima 300."},
        ],
        "filters": [
            {"key": "all", "label": "Zote"}, {"key": "semina", "label": "Semina"},
            {"key": "mkutano", "label": "Mikutano"}, {"key": "mafunzo", "label": "Mafunzo"},
            {"key": "afya", "label": "Afya"}, {"key": "ustawi", "label": "Ustawi"},
        ],
        "past": [
            {"title": "Ziara ya Miradi - Pwani", "date": "30 Julai 2026", "place": "Pwani"},
            {"title": "Mkutano na Wadau - Dodoma", "date": "28 Julai 2026", "place": "Dodoma"},
            {"title": "Mafunzo ya Afya ya Jamii", "date": "26 Julai 2026", "place": "Kilimanjaro"},
            {"title": "Semina ya Elimu ya Wasichana", "date": "24 Julai 2026", "place": "Morogoro"},
        ],
        "stats": [
            {"value": 28,   "label": "Matukio Mwaka Huu"},
            {"value": 4256, "label": "Washiriki Jumla"},
            {"value": 12,   "label": "Mikoa Iliyofikiwa"},
            {"value": 16,   "label": "Matukio Yaliyofanyika"},
        ],
    }


# ===========================================================================
#  MAWASILIANO
# ===========================================================================
def mawasiliano():
    """
    Ukurasa wa Mawasiliano — muundo na taarifa kama zilivyo kwenye bango
    rasmi la MUWESTA (COMMUNICATION).

    Anwani ni ya Dodoma kama alivyothibitisha mteja, si ile ya Dar es Salaam
    iliyokuwa kwenye bango la mfano.
    """
    return {
        "hero": {
            "eyebrow": "Mawasiliano", "scene": "mawasiliano",
            "title": "Wasiliana Nasi",
            "text": "Tuko hapa kukuhudumia. Tufikie kupitia njia zifuatazo.",
        },
        "helpline": {
            "icon": "headset",
            "title": "Tuko hapa kukusaidia!",
            "text": "Piga simu, tuandikie au tutembelee ofisini.",
        },

        # ---- Anwani ya makazi ----
        "address": {
            "title": "Anwani ya Makazi",
            "icon": "map-pin",
            "org": "Muslim Welfare Society of Tanzania (MUWESTA)",
            "office": "Ofisi Kuu",
            "lines": [
                "Shariff PBZ House",
                "Kiwanja Na. 4, Kitalu M — Ghorofa ya Tatu",
                "Mkabala na Viwanja vya Nyerere Square",
                "S.L.P 450, Dodoma, Tanzania",
            ],
            "scene": "msikiti",
        },

        # ---- Namba za simu ----
        "phones": {
            "title": "Namba za Simu",
            "icon": "phone",
            "lines": [
                {"number": "+255 769 600 102", "label": "Ofisi"},
                {"number": "+255 684 123 456", "label": "Maswali ya Jumla"},
                {"number": "+255 754 123 456", "label": "Uanachama"},
                {"number": "+255 713 123 456", "label": "Michango na Msaada"},
                {"number": "+255 762 123 456", "label": "Dharura na Misaada"},
            ],
            "whatsapp": "+255 684 123 456",
        },

        # ---- Barua pepe ----
        "emails": {
            "title": "Barua Pepe",
            "icon": "mail",
            "lines": [
                "info@mwst.or.tz",
                "membership@mwst.or.tz",
                "donations@mwst.or.tz",
                "projects@mwst.or.tz",
                "care@mwst.or.tz",
            ],
            "note": "Tunalenga kujibu ndani ya saa 24.",
        },

        # ---- Saa za kazi ----
        "hours": {
            "title": "Saa za Kazi",
            "icon": "clock",
            "rows": [
                {"day": "Jumatatu - Alhamisi", "time": "08:00 - 16:30"},
                {"day": "Ijumaa", "time": "08:00 - 12:00"},
                {"day": "Jumamosi", "time": "09:00 - 13:00"},
                {"day": "Jumapili", "time": "Imefungwa", "closed": True},
                {"day": "Sikukuu za Taifa", "time": "Imefungwa", "closed": True},
            ],
            "note": "Huduma zetu pia zinapatikana wakati wa programu na matukio maalum.",
        },

        # ---- Ramani ----
        "map": {
            "title": "Tupate Hapa",
            "icon": "map",
            "label": "Muslim Welfare Society of Tanzania",
            "url": "https://www.google.com/maps/search/?api=1&query="
                   "Nyerere+Square+Dodoma+Tanzania",
            "cta": "Fungua kwenye Google Maps",
        },

        # ---- Mitandao ya kijamii ----
        "socials": {
            "title": "Tufuate Kwenye Mitandao",
            "icon": "megaphone",
            "rows": [
                {"icon": "facebook", "name": "Facebook", "handle": "@MWSTanzania"},
                {"icon": "x-social", "name": "X (Twitter)", "handle": "@MWSTanzania"},
                {"icon": "instagram", "name": "Instagram", "handle": "@mwstanzania"},
                {"icon": "youtube", "name": "YouTube",
                 "handle": "Muslim Welfare Society of Tanzania"},
            ],
        },

        # ---- Ayah ya chini ----
        "ayah": {
            "thanks": "Asante kwa kuwa sehemu ya dhamira yetu.",
            "together": "Pamoja kwa Imani, Huduma na Maendeleo.",
            "arabic": "\u0648\u062a\u0639\u0627\u0648\u064e\u0646\u064f\u0648\u0627 "
                      "\u0639\u064e\u0644\u064e\u0649 \u0627\u0644\u0652\u0628\u0650\u0631\u0651\u0650 "
                      "\u0648\u064e\u0627\u0644\u062a\u0651\u064e\u0642\u0652\u0648\u064e\u0649\u0670",
            "translation": "Na tushirikiane katika wema na uchaji.",
            "ref": "(Al-Qur'an 5:2)",
        },

        "subjects": ["Uanachama", "Michango na Malipo", "Msaada wa Ustawi",
                     "Ushirikiano na Udhamini", "Malalamiko", "Nyingine"],
        "faqs": [
            {"q": "Nawezaje kujiunga na MUWESTA?",
             "a": "Tembelea ukurasa wa Uanachama, jaza fomu ya mtandaoni, chagua aina ya "
                  "uanachama na ulipe ada. Utapokea namba ya uanachama na kadi ya kidijitali."},
            {"q": "Naomba msaada wa ustawi, nifanyeje?",
             "a": "Wanachama wanaweza kuomba kupitia akaunti zao. Wasio wanachama wanaweza "
                  "kuwasiliana na ofisi kuu."},
            {"q": "Nataka kuchangia mradi maalum, inawezekana?",
             "a": "Ndiyo. Unaweza kuchagua mradi unaotaka kuufadhili wakati wa kutoa mchango, "
                  "na utapokea ripoti ya matumizi."},
            {"q": "Mnapokea wafadhili wa kimataifa?",
             "a": "Ndiyo. Tunashirikiana na mashirika ya kimataifa. Wasiliana na ofisi kuu "
                  "kwa taratibu za makubaliano."},
        ],
    }


# ===========================================================================
#  JIUNGE (fomu ya umma)
# ===========================================================================
def jiunge():
    return {
        "hero": {
            "eyebrow": "Usajili", "scene": "elimu",
            "title": "Jiunge na MUWESTA Leo",
            "text": "Jaza fomu hii kuanza safari yako ya uanachama. Itachukua dakika chache tu.",
        },
        "tiers": uanachama()["tiers"],
        "steps": uanachama()["steps"],
    }
