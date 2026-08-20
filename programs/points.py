"""
Pointi za MUWESTA — sera na hesabu.

Kila uamuzi wa sera upo hapa, si umetawanyika kwenye code. Bodi
ikibadilisha kiwango au kikomo, mahali pa kubadilisha ni hapa pekee.

MUUNDO
------
Kuna ngazi MBILI zinazojitegemea:

  1. Pointi za MUWESTA (`period`) — hupimwa kwa kipindi cha miaka mitatu
     kinachoendelea. Ndizo zinazoamua kiwango cha mwanachama SASA.
  2. Pointi za maisha (`lifetime`) — hazipungui kamwe. Ndizo za vyeti
     na heshima ya kudumu.

Mtu aliyefanya kazi kubwa 2019 anabaki na heshima yake, lakini kiwango
chake cha leo kinaonyesha ukweli wa leo.

KWA NINI KUNA KIKOMO CHA PESA
-----------------------------
Fedha hutoa pointi, lakini si zaidi ya `MONEY_CAP` kwa kipindi. Bila
kikomo, kiwango cha juu kingekuwa cha matajiri pekee: mtu anayejitolea
saa moja kila wiki kwa miaka mitatu hupata ~15,600, wakati mchango wa
TSh 50m hupata 50,000 kwa muamala mmoja.

Kikomo kinafanya kiwango kiseme "huyu yupo nasi", si "huyu ana pesa".
Waliotoa fedha nyingi hutambuliwa kwenye Orodha ya Heshima ya Wahisani
— mahali panapowastahili — badala ya kushinda ngazi ya ushiriki.

KWA NINI HAKUNA VIWANGO VYA KILA MRADI
--------------------------------------
Kiwango ni kimoja kwa michango yote. Kuweka "yatima mara 2, maji mara
1.5" kunga:
  - kunaandika tathmini ya thamani kwenye code (kwa nini wajane 2 na
    afya 1.5? hakuna jibu zuri),
  - kunashawishi watu kuchagua mradi wenye pointi nyingi badala ya
    wenye uhitaji mkubwa — mradi wa maji ungekauka,
  - kunakuwa mzigo: kila mradi mpya unahitaji uamuzi wa kiwango.

Badala yake kuna `PointBoost`: bonasi ya MUDA inayowekwa na afisa kwa
kampeni fulani ("mwezi huu, mafuriko mara mbili"). Inaisha kampeni
ikiisha. Hii inaipa Bodi uwezo wa kuelekeza michango pale
panapohitajika SASA, badala ya hukumu ya kudumu.
"""
from decimal import Decimal

from django.utils.translation import gettext_lazy as _

# ---------------------------------------------------------------------------
#  Vipimo vya msingi
# ---------------------------------------------------------------------------

#: Kila TSh 1,000 hutoa pointi 1. Kiwango kimoja kwa michango yote.
SHILLINGS_PER_POINT = Decimal("1000")

#: Pointi za juu kabisa zinazoweza kutokana na FEDHA kwa kipindi kimoja
#: cha miaka mitatu. Zilizozidi zinatambuliwa kwenye Orodha ya Heshima,
#: si kwenye kiwango.
MONEY_CAP = 4000

#: Kipindi cha kuhesabu pointi za kiwango — sawa na kipindi cha
#: uanachama (miaka 3), ili vitu viwili visitofautiane.
PERIOD_YEARS = 3

#: Ada ya uanachama hutoa pointi hizi bila kujali kiasi. Ni malipo ya
#: wajibu, si ukarimu — kwa hiyo haipimwi kwa ukubwa wake.
MEMBERSHIP_FEE_POINTS = 100


# ---------------------------------------------------------------------------
#  Viwango
# ---------------------------------------------------------------------------
#: Majina ni ya Kiswahili na hayagusi madini wala fedha. Bronze/Silver/
#: Gold hayakutumika kwa sababu tayari ni MADARAJA YA UANACHAMA
#: (`members.Category`) — mwanachama angeona "Daraja: Gold | Kiwango:
#: Silver" na asielewe tofauti.
#:
#: Namba ni ndogo kwa makusudi. Kiwango kisichofikika hakihamasishi,
#: kinavunja moyo.
TIERS = [
    {"key": "mshiriki",  "min": 0,    "icon": "user",
     "name": "Mshiriki",         "name_en": "Participant",
     "note": "Umeanza safari nasi",
     "note_en": "You have started the journey with us"},
    {"key": "mchangiaji", "min": 500, "icon": "hand-heart",
     "name": "Mchangiaji",       "name_en": "Contributor",
     "note": "Mchango wako unaonekana",
     "note_en": "Your contribution shows"},
    {"key": "mhudumu",   "min": 1500, "icon": "users",
     "name": "Mhudumu",          "name_en": "Servant of the Community",
     "note": "Huduma yako imekuwa ya kawaida",
     "note_en": "Your service has become steady"},
    {"key": "nguzo",     "min": 3500, "icon": "building",
     "name": "Nguzo",            "name_en": "Pillar",
     "note": "Jamii inakutegemea",
     "note_en": "The community leans on you"},
    {"key": "mhimili",   "min": 7000, "icon": "trophy",
     "name": "Mhimili wa Jamii", "name_en": "Foundation of the Community",
     "note": "Kiwango cha juu kabisa cha ushiriki",
     "note_en": "The highest level of participation"},
]


def tier_for(points):
    """Kiwango kinacholingana na pointi za kipindi."""
    chosen = TIERS[0]
    for row in TIERS:
        if points >= row["min"]:
            chosen = row
    return chosen


def next_tier(points):
    """Kiwango kinachofuata, au None kama tayari yupo cha juu kabisa."""
    for row in TIERS:
        if points < row["min"]:
            return row
    return None


# ---------------------------------------------------------------------------
#  Aina za pointi
# ---------------------------------------------------------------------------
class PointKind:
    """
    Chanzo cha pointi. Kinaamua nani anaweza kuzitoa na jinsi gani.

    MALIPO zinatolewa na mfumo wenyewe baada ya Pesapal kuthibitisha —
    hakuna binadamu anayehusika, kwa hiyo hazidanganyiki.

    USHIRIKI zinatolewa kwa mkono na afisa. Hapa ndipo hatari yote ya
    udanganyifu ilipo: "kujitolea saa 1 = pointi 100" ni sawa na
    mchango wa TSh 100,000, na afisa mmoja angeweza kumpandisha rafiki
    yake kwa kubofya mara chache. Ndiyo maana kuna vikomo na ukaguzi.
    """
    MONEY = "money"
    PARTICIPATION = "participation"
    BONUS = "bonus"
    REVERSAL = "reversal"

    CHOICES = [
        (MONEY, _("Michango na Ada")),
        (PARTICIPATION, _("Ushiriki")),
        (BONUS, _("Bonasi")),
        (REVERSAL, _("Marekebisho")),
    ]

    LABELS = {MONEY: _("Michango"), PARTICIPATION: _("Ushiriki"),
              BONUS: _("Bonasi"), REVERSAL: _("Marekebisho")}


# ---------------------------------------------------------------------------
#  Ulinzi dhidi ya udanganyifu
# ---------------------------------------------------------------------------

#: Pointi za juu ambazo afisa mmoja anaweza kutoa kwa siku bila idhini
#: ya pili. Ni takriban shughuli tatu kubwa — inatosha kwa siku ya kazi
#: ya kawaida, lakini haitoshi kumpandisha mtu kiwango kimya kimya.
OFFICER_DAILY_CAP = 300

#: Pointi za juu kwa tukio moja bila idhini ya pili.
SECOND_APPROVAL_ABOVE = 200


# ---------------------------------------------------------------------------
#  Shughuli za ushiriki (Awamu ya 2)
# ---------------------------------------------------------------------------
#: Hizi hazitolewi na mfumo wenyewe. Zinahitaji afisa kuzithibitisha,
#: na zinasubiri Bodi kupitisha kanuni kwamba pointi si haki ya
#: kifedha. Zimeandikwa hapa ili `seed` iweze kuziunda zikiwa tayari.
PARTICIPATION_ACTIVITIES = [
    ("kikao",       "Kuhudhuria kikao",            "Attending a meeting",             30),
    ("semina",      "Kuhudhuria semina",           "Attending a seminar",             50),
    ("charity",     "Kushiriki tukio la kheri",    "Taking part in a charity event",  50),
    ("kujitolea",   "Kujitolea (saa 1)",           "Volunteering (1 hour)",          100),
    ("kampeni",     "Kushiriki kampeni ya ustawi", "Taking part in a welfare campaign", 100),
    ("msiba",       "Kusaidia shughuli ya msiba",  "Helping at a funeral",           100),
    ("mwaliko",     "Kuleta mwanachama mpya",      "Bringing in a new member",       100),
    ("kuratibu",    "Kuratibu tukio",              "Coordinating an event",          150),
    ("kitaalamu",   "Kutoa huduma ya kitaalamu",   "Providing professional service", 200),
    ("mradi",       "Kuongoza mradi",              "Leading a project",              300),
]


# ---------------------------------------------------------------------------
#  Hesabu
# ---------------------------------------------------------------------------
def points_for_amount(amount, multiplier=1):
    """
    Pointi zinazotokana na kiasi cha fedha.

    Inarudisha namba kamili (int) — pointi za desimali zingeleta
    maswali yasiyo na faida ("kwa nini nina 12.5?").
    """
    if not amount:
        return 0
    base = Decimal(str(amount)) / SHILLINGS_PER_POINT
    return int(base * Decimal(str(multiplier)))
