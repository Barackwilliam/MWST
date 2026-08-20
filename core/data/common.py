"""Vitu vinavyotumika kwenye dashboards zote."""

MONTHS = ["Jan", "Feb", "Mac", "Apr", "Mei", "Jun", "Jul", "Ago", "Sep", "Okt", "Nov", "Des"]

C = {
    "green": "#12864a", "navy": "#1b3b6f", "gold": "#d4af37", "purple": "#6d28d9",
    "teal": "#0891b2", "red": "#dc2626", "orange": "#ea580c", "mint": "#4cbd83",
    "slate": "#64748b", "bronze": "#b45309", "blue": "#2563eb", "lime": "#65a30d",
}


def tzs(n):
    return "TZS {:,}".format(n)


VERSES = [
    {"arabic": "وَتَعَاوَنُوا۟ عَلَى ٱلْبِرِّ وَٱلتَّقْوَىٰ",
     "swahili": "Na msaidiane katika heri na taqwa.", "reference": "Al-Ma'idah: 2"},
    {"arabic": "وَمَا تُقَدِّمُوا۟ لِأَنفُسِكُم مِّنْ خَيْرٍ تَجِدُوهُ عِندَ ٱللَّهِ",
     "swahili": "Na kheri yoyote mnayoitanguliza kwa ajili yenu, mtaikuta kwa Allah.",
     "reference": "Al-Baqarah: 110"},
]


def verse(i=0):
    return VERSES[i % len(VERSES)]


QUOTE = {"text": "Imani kwa vitendo, Huduma na Maendeleo kwa binadamu"}

# Mikoa ya Tanzania Bara yenye idadi ya wanachama (mock)
REGIONS = [
    {"name": "Dar es Salaam", "members": 18745, "pct": 35, "x": 78, "y": 62},
    {"name": "Mwanza",        "members": 12830, "pct": 15, "x": 24, "y": 26},
    {"name": "Arusha",        "members": 11254, "pct": 12, "x": 52, "y": 22},
    {"name": "Mbeya",         "members": 9845,  "pct": 10, "x": 26, "y": 74},
    {"name": "Morogoro",      "members": 8967,  "pct": 8,  "x": 62, "y": 62},
    {"name": "Dodoma",        "members": 7552,  "pct": 7,  "x": 50, "y": 52},
    {"name": "Kilimanjaro",   "members": 6245,  "pct": 5,  "x": 64, "y": 20},
    {"name": "Tanga",         "members": 5893,  "pct": 4,  "x": 72, "y": 36},
    {"name": "Pwani",         "members": 6745,  "pct": 4,  "x": 74, "y": 56},
    {"name": "Kagera",        "members": 4512,  "pct": 3,  "x": 16, "y": 16},
    {"name": "Shinyanga",     "members": 4985,  "pct": 3,  "x": 32, "y": 36},
    {"name": "Tabora",        "members": 3654,  "pct": 3,  "x": 34, "y": 46},
    {"name": "Geita",         "members": 5128,  "pct": 3,  "x": 20, "y": 32},
    {"name": "Kigoma",        "members": 3845,  "pct": 2,  "x": 14, "y": 44},
    {"name": "Manyara",       "members": 4219,  "pct": 2,  "x": 56, "y": 34},
    {"name": "Singida",       "members": 3654,  "pct": 2,  "x": 44, "y": 44},
    {"name": "Katavi",        "members": 2350,  "pct": 1,  "x": 20, "y": 58},
    {"name": "Rukwa",         "members": 3210,  "pct": 1,  "x": 18, "y": 68},
    {"name": "Songwe",        "members": 2987,  "pct": 1,  "x": 24, "y": 80},
    {"name": "Njombe",        "members": 2156,  "pct": 1,  "x": 40, "y": 80},
    {"name": "Iringa",        "members": 3125,  "pct": 1,  "x": 44, "y": 68},
    {"name": "Lindi",         "members": 3245,  "pct": 1,  "x": 72, "y": 76},
    {"name": "Mtwara",        "members": 3125,  "pct": 1,  "x": 70, "y": 86},
    {"name": "Ruvuma",        "members": 2410,  "pct": 1,  "x": 52, "y": 88},
    {"name": "Simiyu",        "members": 3120,  "pct": 1,  "x": 36, "y": 26},
    {"name": "Mara",          "members": 3864,  "pct": 1,  "x": 34, "y": 16},
]
