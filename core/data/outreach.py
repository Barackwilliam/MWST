"""Data ya Wadau & Wahisani, Matukio, Picha & Video, na tovuti ya umma."""
from .common import MONTHS, C, tzs, REGIONS


# ===========================================================================
#  WADAU NA WAHISANI
# ===========================================================================
def wadau():
    return {
        "kpis": [
            {"label": "Jumla ya Wadau Waliosajiliwa", "value": "1,248", "icon": "users", "tint": "green",
             "delta": "12.5%", "dir": "up", "note": "Wadau hai"},
            {"label": "Jumla ya Wahisani", "value": "2,563", "icon": "heart", "tint": "navy",
             "delta": "15.8%", "dir": "up", "note": "Wahisani hai"},
            {"label": "Jumla ya Michango Iliyopokelewa", "value": tzs(1_285_456_000), "icon": "wallet",
             "tint": "teal", "money": True, "delta": "18.4%", "dir": "up", "note": "Takwimu zote"},
            {"label": "Michango ya Mwezi Huu", "value": tzs(145_760_000), "icon": "calendar",
             "tint": "gold", "money": True, "delta": "21.7%", "dir": "up", "note": "Julai 2026"},
            {"label": "Kampeni Zinazoendelea", "value": "8", "icon": "target", "tint": "green",
             "delta": "2", "dir": "up", "note": "Kampeni hai"},
            {"label": "Asilimia ya Lengo Lililofikiwa", "value": "68%", "icon": "trophy",
             "tint": "gold", "progress": 68},
        ],
        "trend": {"labels": MONTHS,
                  "data": [78_000_000, 92_000_000, 85_000_000, 118_000_000, 104_000_000,
                           132_000_000, 145_760_000, 128_000_000, 138_000_000, 152_000_000,
                           141_000_000, 165_000_000]},
        "by_type": {
            "id": "chDonorType", "title": "Mgawanyo wa Michango kwa Aina",
            "center_value": "TZS 1.285B", "center_label": "",
            "rows": [
                {"label": "Zakat",              "value": 28, "display": "28%", "color": C["green"]},
                {"label": "Sadaqah",            "value": 22, "display": "22%", "color": C["blue"]},
                {"label": "Ufadhili wa Miradi", "value": 18, "display": "18%", "color": C["purple"]},
                {"label": "Waqf",               "value": 12, "display": "12%", "color": C["gold"]},
                {"label": "Fitrah",             "value": 8,  "display": "8%",  "color": C["teal"]},
                {"label": "Kafara",             "value": 6,  "display": "6%",  "color": C["orange"]},
                {"label": "Dharura",            "value": 6,  "display": "6%",  "color": C["red"]},
            ]},
        "campaigns": [
            {"title": "Ujenzi wa Shule ya Msingi", "raised": tzs(120_000_000),
             "goal": "200,000,000", "pct": 60, "days": "Siku 45"},
            {"title": "Maji Safi kwa Jamii", "raised": tzs(85_500_000),
             "goal": "150,000,000", "pct": 57, "days": "Siku 30"},
            {"title": "Wafadhili wa Yatima", "raised": tzs(72_300_000),
             "goal": "120,000,000", "pct": 60, "days": "Siku 52"},
            {"title": "Msaada wa Dharura", "raised": tzs(38_200_000),
             "goal": "80,000,000", "pct": 48, "days": "Siku 20"},
        ],
        "top_donors": [
            {"n": 1, "name": "Muslim Aid International", "value": tzs(328_500_000)},
            {"n": 2, "name": "Islamic Relief Worldwide", "value": tzs(245_700_000)},
            {"n": 3, "name": "Amaan Foundation",         "value": tzs(156_300_000)},
            {"n": 4, "name": "Hassan & Family Foundation", "value": tzs(98_650_000)},
            {"n": 5, "name": "Al-Barakah Charity Org.",  "value": tzs(76_400_000)},
        ],
        "recent": [
            {"name": "Alh. Said Salim", "type": "Sadaqah", "value": tzs(5_000_000),
             "date": "31/07/2026 - 10:45 AM", "tint": "red"},
            {"name": "Muslim Aid International", "type": "Ufadhili wa Miradi", "value": tzs(50_000_000),
             "date": "31/07/2026 - 09:30 AM", "tint": "red"},
            {"name": "Fatma Juma", "type": "Zakat", "value": tzs(2_500_000),
             "date": "31/07/2026 - 08:15 AM", "tint": "red"},
            {"name": "Amaan Foundation", "type": "Ufadhili wa Miradi", "value": tzs(25_000_000),
             "date": "30/07/2026 - 07:40 PM", "tint": "red"},
            {"name": "Abdallah Nassor", "type": "Sadaqah", "value": tzs(1_000_000),
             "date": "30/07/2026 - 06:20 PM", "tint": "red"},
        ],
        "regions": REGIONS,
        "region_share": [
            {"name": "Dar es Salaam", "pct": 35},
            {"name": "Arusha", "pct": 15},
            {"name": "Mwanza", "pct": 12},
            {"name": "Dodoma", "pct": 10},
            {"name": "Morogoro", "pct": 8},
            {"name": "Nyinginezo", "pct": 20},
        ],
        "alerts": [
            {"text": "Ahadi ya mchango kutoka Islamic Relief Worldwide inahitaji kuthibitishwa.",
             "time": "15 dakika iliyopita", "icon": "file", "tint": "navy"},
            {"text": "Kampeni ya Maji Safi kwa Jamii itamalizika baada ya siku 30.",
             "time": "1 saa iliyopita", "icon": "alert", "tint": "gold"},
            {"text": "Mdau mpya amesajiliwa: Baraka Group Ltd", "time": "2 saa iliyopita",
             "icon": "user-plus", "tint": "green"},
            {"text": "Michango 7 imethibitishwa leo.", "time": "3 saa iliyopita",
             "icon": "check-circle", "tint": "green"},
            {"text": "Ripoti ya mwezi Julai 2026 iko tayari.", "time": "4 saa iliyopita",
             "icon": "chart-bar", "tint": "purple"},
        ],
        "year_goal": {"goal": tzs(2_000_000_000), "raised": tzs(1_367_890_000), "pct": 68.39},
        "actions": [
            {"label": "Sajili Mdau Mpya", "icon": "user-plus", "tint": "green"},
            {"label": "Sajili Mhisani", "icon": "heart", "tint": "navy"},
            {"label": "Rekodi Mchango", "icon": "wallet", "tint": "teal"},
            {"label": "Fungua Kampeni Mpya", "icon": "target", "tint": "gold"},
            {"label": "Tengeneza Risiti", "icon": "receipt", "tint": "purple"},
            {"label": "Tuma Barua ya Shukrani", "icon": "mail", "tint": "orange"},
            {"label": "Pakua Ripoti", "icon": "download", "tint": "navy"},
        ],
    }


# ===========================================================================
#  MATUKIO
# ===========================================================================
def matukio():
    return {
        "kpis": [
            {"label": "Jumla ya Matukio", "value": "28", "icon": "calendar", "tint": "green",
             "delta": "21.7%", "dir": "up", "note": "Mwezi huu"},
            {"label": "Matukio Yaliyofanyika", "value": "16", "icon": "calendar-check", "tint": "navy",
             "delta": "23.1%", "dir": "up", "note": "Mwezi huu"},
            {"label": "Matukio Yanayokuja", "value": "10", "icon": "clock", "tint": "purple",
             "delta": "9.1%", "dir": "down", "note": "Mwezi huu"},
            {"label": "Jumla ya Washiriki", "value": "4,256", "icon": "users", "tint": "gold",
             "delta": "28.4%", "dir": "up", "note": "Mwezi huu"},
            {"label": "Mikoa Inayohusika", "value": "12", "icon": "map-pin", "tint": "teal",
             "note": "Mwezi huu"},
            {"label": "Asilimia ya Utekelezaji", "value": "78%", "icon": "pie", "tint": "gold",
             "progress": 78},
        ],
        "trend": {"labels": MONTHS,
                  "data_done": [8, 12, 10, 15, 13, 18, 16, 14, 11, 9, 12, 10],
                  "data_up":   [5, 7, 6, 9, 8, 11, 10, 12, 13, 15, 14, 16]},
        "by_type": {
            "id": "chEvType", "title": "Matukio kwa Aina",
            "center_value": "28", "center_label": "Jumla",
            "rows": [
                {"label": "Kongamano",          "value": 8, "display": "8",  "pct": "28.6", "color": C["green"]},
                {"label": "Mafunzo",            "value": 6, "display": "6",  "pct": "21.4", "color": C["blue"]},
                {"label": "Mikutano",           "value": 5, "display": "5",  "pct": "17.9", "color": C["purple"]},
                {"label": "Semina",             "value": 4, "display": "4",  "pct": "14.3", "color": C["gold"]},
                {"label": "Shughuli za Kijamii","value": 3, "display": "3",  "pct": "10.7", "color": C["teal"]},
                {"label": "Mahusiano na Jamii", "value": 2, "display": "2",  "pct": "7.1",  "color": C["orange"]},
            ]},
        "upcoming": [
            {"title": "Kongamano la Elimu ya Kiislamu", "date": "05/08/2026", "place": "Dodoma", "in": "Siku 5"},
            {"title": "Mafunzo ya Uongozi wa Utawala", "date": "12/08/2026", "place": "Arusha", "in": "Siku 12"},
            {"title": "Shughuli ya Kuwasaidia Yatima", "date": "18/08/2026", "place": "Dar es Salaam", "in": "Siku 18"},
            {"title": "Semina ya Uwezeshaji Kiuchumi", "date": "25/08/2026", "place": "Mwanza", "in": "Siku 25"},
            {"title": "Mkutano Mkuu wa MWST", "date": "30/08/2026", "place": "Zanzibar", "in": "Siku 30"},
        ],
        "recent": [
            {"title": "Ziara ya Miradi - Pwani", "date": "30/07/2026", "place": "Pwani", "status": "Imefanyika"},
            {"title": "Mkutano na Wadau - Dodoma", "date": "28/07/2026", "place": "Dodoma", "status": "Imefanyika"},
            {"title": "Mafunzo ya Afya ya Jamii", "date": "26/07/2026", "place": "Kilimanjaro", "status": "Imefanyika"},
            {"title": "Semina ya Elimu ya Wasichana", "date": "24/07/2026", "place": "Morogoro", "status": "Imefanyika"},
            {"title": "Shughuli ya Msaada wa Chakula", "date": "20/07/2026", "place": "Arusha", "status": "Imefanyika"},
        ],
        "participants": [
            {"n": 1, "name": "Dar es Salaam", "value": "1,125", "pct": 100, "color": C["green"]},
            {"n": 2, "name": "Arusha",        "value": "825",   "pct": 73,  "color": C["blue"]},
            {"n": 3, "name": "Mwanza",        "value": "645",   "pct": 57,  "color": C["gold"]},
            {"n": 4, "name": "Dodoma",        "value": "585",   "pct": 52,  "color": C["purple"]},
            {"n": 5, "name": "Morogoro",      "value": "425",   "pct": 38,  "color": C["teal"]},
        ],
        "participants_total": "3,605",
        "status_mix": {
            "id": "chEvStatus", "title": "Matukio kwa Hali",
            "center_value": "28", "center_label": "",
            "rows": [
                {"label": "Imefanyika",   "value": 16, "display": "16", "pct": "57.1", "color": C["green"]},
                {"label": "Imepangwa",    "value": 10, "display": "10", "pct": "35.7", "color": C["blue"]},
                {"label": "Imeahirishwa", "value": 1,  "display": "1",  "pct": "3.6",  "color": C["gold"]},
                {"label": "Imeghairiwa",  "value": 1,  "display": "1",  "pct": "3.6",  "color": C["red"]},
            ]},
        "alerts": [
            {"text": "Kongamano la Elimu ya Kiislamu lipo baada ya siku 5.", "time": "1 saa iliyopita",
             "icon": "bell", "tint": "green"},
            {"text": "Mkutano Mkuu wa MWST upo baada ya siku 30.", "time": "3 saa iliyopita",
             "icon": "calendar", "tint": "navy"},
            {"text": "Matukio 3 mapya yameongezwa kwenye kalenda.", "time": "5 saa iliyopita",
             "icon": "users", "tint": "purple"},
            {"text": "Mafunzo ya Uongozi yamehamishwa tarehe.", "time": "1 siku iliyopita",
             "icon": "alert", "tint": "gold"},
        ],
        "calendar": {
            "title": "Julai 2026",
            "dow": ["Jum", "Jtn", "Jat", "Alh", "Ijm", "Jum", "Jum"],
            "days": [
                [None, None, None, 1, 2, 3, 4],
                [5, 6, 7, 8, 9, 10, 11],
                [12, 13, 14, 15, 16, 17, 18],
                [19, 20, 21, 22, 23, 24, 25],
                [26, 27, 28, 29, 30, 31, None],
            ],
            "marks": {16: "ev", 25: "ev2", 30: "ev3"},
        },
        "month_summary": [
            {"label": "Kongamano", "value": 5, "pct": 100, "color": C["green"]},
            {"label": "Mafunzo",   "value": 4, "pct": 80,  "color": C["blue"]},
            {"label": "Mikutano",  "value": 3, "pct": 60,  "color": C["gold"]},
            {"label": "Semina",    "value": 2, "pct": 40,  "color": C["purple"]},
            {"label": "Shughuli za Kijamii", "value": 2, "pct": 40, "color": C["teal"]},
        ],
        "month_total": "16",
        "actions": [
            {"label": "Ongeza Tukio", "icon": "calendar", "tint": "green"},
            {"label": "Panga Matukio", "icon": "clock", "tint": "navy"},
            {"label": "Orodha ya Washiriki", "icon": "users", "tint": "gold"},
            {"label": "Tuma Ualikaji", "icon": "mail", "tint": "purple"},
            {"label": "Kalenda Kamili", "icon": "calendar-check", "tint": "teal"},
            {"label": "Tengeneza Ripoti", "icon": "chart-bar", "tint": "orange"},
        ],
    }


# ===========================================================================
#  PICHA NA VIDEO
# ===========================================================================
def media():
    return {
        "kpis": [
            {"label": "Jumla ya Picha", "value": "2,458", "icon": "image", "tint": "green",
             "delta": "18.7%", "dir": "up", "note": "Mwezi huu"},
            {"label": "Jumla ya Video", "value": "356", "icon": "video", "tint": "navy",
             "delta": "15.3%", "dir": "up", "note": "Mwezi huu"},
            {"label": "Pakiwa Mwezi Huu", "value": "487", "icon": "upload", "tint": "purple",
             "delta": "22.6%", "dir": "up", "note": "Mwezi huu"},
            {"label": "Pakuliwa (Downloads)", "value": "1,245", "icon": "download", "tint": "gold",
             "delta": "17.5%", "dir": "up", "note": "Mwezi huu"},
            {"label": "Albamu", "value": "48", "icon": "folder", "tint": "teal",
             "note": "Mkusanyiko wa albamu"},
            {"label": "Hifadhi Inayopatikana", "value": "76.4 GB", "icon": "database", "tint": "navy",
             "note": "ya 100 GB (76%)", "progress": 76},
        ],
        "trend": {"labels": MONTHS,
                  "photos": [120, 145, 138, 165, 180, 172, 210, 195, 160, 148, 155, 168],
                  "videos": [22, 28, 25, 34, 30, 38, 32, 40, 36, 42, 38, 45]},
        "photo_cat": {
            "id": "chPhotoCat", "title": "Picha kwa Kategoria",
            "center_value": "2,458", "center_label": "Jumla",
            "rows": [
                {"label": "Miradi",     "value": 870, "display": "35.4%", "color": C["green"]},
                {"label": "Matukio",    "value": 617, "display": "25.1%", "color": C["blue"]},
                {"label": "Mafunzo",    "value": 359, "display": "14.6%", "color": C["gold"]},
                {"label": "Misaada",    "value": 251, "display": "10.2%", "color": C["purple"]},
                {"label": "Ziara",      "value": 179, "display": "7.3%",  "color": C["teal"]},
                {"label": "Nyinginezo", "value": 182, "display": "7.4%",  "color": C["red"]},
            ]},
        "video_cat": {
            "id": "chVideoCat", "title": "Video kwa Kategoria",
            "center_value": "356", "center_label": "Jumla",
            "rows": [
                {"label": "Miradi",     "value": 114, "display": "32.0%", "color": C["green"]},
                {"label": "Matukio",    "value": 101, "display": "28.4%", "color": C["blue"]},
                {"label": "Mafunzo",    "value": 57,  "display": "16.0%", "color": C["gold"]},
                {"label": "Misaada",    "value": 41,  "display": "11.5%", "color": C["purple"]},
                {"label": "Ziara",      "value": 22,  "display": "6.2%",  "color": C["teal"]},
                {"label": "Nyinginezo", "value": 21,  "display": "5.9%",  "color": C["red"]},
            ]},
        "storage": {"used": "76.4 GB", "total": "100 GB", "pct": 76,
                    "rows": [{"label": "Picha", "value": "58.6 GB"},
                             {"label": "Video", "value": "17.8 GB"},
                             {"label": "Nyaraka Nyingine", "value": "0.0 GB"}]},
        "photos": [
            {"title": "Mkutano Mkuu wa MWST 2026", "date": "01/08/2026", "views": "36", "size": "2.4 MB"},
            {"title": "Ujenzi wa Zahanati - Dodoma", "date": "31/07/2026", "views": "28", "size": "1.9 MB"},
            {"title": "Semina ya Uwezeshaji Kiuchumi", "date": "31/07/2026", "views": "42", "size": "2.1 MB"},
            {"title": "Misaada kwa Yatima - Arusha", "date": "30/07/2026", "views": "31", "size": "1.7 MB"},
            {"title": "Usafi wa Mazingira - Mwanza", "date": "30/07/2026", "views": "26", "size": "1.6 MB"},
        ],
        "videos": [
            {"title": "Ujenzi wa Shule Mpya - Pwani.mp4", "date": "01/08/2026", "dur": "04:32", "size": "24.6 MB"},
            {"title": "Mkutano Mkuu wa MWST 2026.mp4", "date": "31/07/2026", "dur": "03:18", "size": "15.3 MB"},
            {"title": "Semina ya Uongozi - Dodoma.mp4", "date": "30/07/2026", "dur": "05:07", "size": "22.1 MB"},
            {"title": "Ziara ya Miradi - Morogoro.mp4", "date": "29/07/2026", "dur": "03:45", "size": "18.7 MB"},
            {"title": "Misaada ya Dharura - Pwani.mp4", "date": "28/07/2026", "dur": "04:11", "size": "20.4 MB"},
        ],
        "uploads": [
            {"name": "Mkutano Mkuu wa MWST 2026.jpg", "meta": "01/08/2026  10:30 AM", "size": "2.4 MB"},
            {"name": "Ujenzi wa Zahanati - Dodoma.mp4", "meta": "01/08/2026  09:15 AM", "size": "24.6 MB"},
            {"name": "Semina ya Uwezeshaji Kiuchumi.jpg", "meta": "31/07/2026  04:45 PM", "size": "1.8 MB"},
            {"name": "Misaada ya Kifedha - Morogoro.jpg", "meta": "30/07/2026  02:20 PM", "size": "2.1 MB"},
            {"name": "Ziara ya Mashirika Washirika.mp4", "meta": "28/07/2026  11:10 AM", "size": "18.7 MB"},
        ],
        "actions": [
            {"label": "Pakia Picha", "icon": "image", "tint": "green"},
            {"label": "Pakia Video", "icon": "video", "tint": "navy"},
            {"label": "Unda Albamu", "icon": "folder", "tint": "purple"},
            {"label": "Panga Faili", "icon": "settings", "tint": "gold"},
        ],
    }


# ===========================================================================
#  TOVUTI YA UMMA
# ===========================================================================
def public_site():
    return {
        "contacts": {"phone": "+255 769 600 102", "email": "info@muslimwelfare.or.tz",
                     "address": "Nkuhungu, Dodoma, Tanzania"},
        "menu": [
            {"label": "Nyumbani", "active": True}, {"label": "Kuhusu Sisi"},
            {"label": "Uanachama"}, {"label": "Huduma Zetu"}, {"label": "Habari"},
            {"label": "Matukio"}, {"label": "Mawasiliano"},
        ],
        "hero": {
            "eyebrow": "Karibu kwenye Mfumo wa Usimamizi wa Uanachama wa MWST",
            "title": "Imani kwa Vitendo,<br>Huduma na Maendeleo<br>kwa Binadamu",
            "text": "Tunatekeleza huduma za kijamii, kiuchumi na kiimani kwa mujibu wa "
                    "maadili ya Kiislamu kwa maendeleo ya jamii na ustawi wa binadamu.",
        },
        "roles": [
            {"label": "Mwanachama", "icon": "user", "url": "/mwanachama/", "tint": "green"},
            {"label": "Afisa", "icon": "briefcase", "url": "/usajili/", "tint": "navy"},
            {"label": "Mratibu", "icon": "map", "url": "/wadau/", "tint": "purple"},
            {"label": "Msimamizi", "icon": "shield", "url": "/taifa/", "tint": "red"},
        ],
        "stats": [
            {"value": "6,842", "label": "Jumla ya Wanachama", "icon": "users",
             "delta": "↑ 12.5% kutoka mwezi jana"},
            {"value": "5,931", "label": "Wanachama Hai", "icon": "user-check",
             "delta": "86.7% ya jumla"},
            {"value": tzs(136_450_000), "label": "Jumla ya Michango", "icon": "wallet",
             "delta": "↑ 18.4% kutoka mwezi jana"},
            {"value": "248,590", "label": "Pointi Zilizotolewa", "icon": "coins",
             "delta": "↑ 15.7% kutoka mwezi jana"},
            {"value": tzs(42_770_000), "label": "Misaada Iliyotolewa", "icon": "hand-heart",
             "delta": "↓ 5.3% kutoka mwezi jana"},
        ],
        "services": [
            {"label": "Uanachama", "icon": "users", "url": "/usajili/"},
            {"label": "Malipo & Michango", "icon": "wallet", "url": "/malipo/"},
            {"label": "Pointi & Tuzo", "icon": "star", "url": "#"},
            {"label": "Huduma za Ustawi", "icon": "hand-heart", "url": "#"},
            {"label": "Matukio", "icon": "calendar", "url": "/matukio/"},
            {"label": "Habari", "icon": "megaphone", "url": "/media/"},
            {"label": "Nyaraka", "icon": "file", "url": "#"},
            {"label": "Mawasiliano", "icon": "phone", "url": "#"},
        ],
        "events": [
            {"d": "15", "m": "MEI", "y": "2026", "title": "Semina ya Uongozi na Maadili ya Kiislamu",
             "venue": "Ukumbi wa MWST - Dodoma", "time": "08:00 AM - 02:00 PM",
             "status": "Inajayo", "badge": "ok"},
            {"d": "28", "m": "MEI", "y": "2026", "title": "Mkutano Mkuu wa MWST",
             "venue": "JNICC Hall - Dodoma", "time": "09:00 AM - 01:00 PM",
             "status": "Umealikwa", "badge": "warn"},
            {"d": "10", "m": "JUN", "y": "2026", "title": "Zozi la Upimaji Afya Bure",
             "venue": "Kituo cha Afya - Nkuhungu", "time": "08:00 AM - 04:00 PM",
             "status": "Inajayo", "badge": "ok"},
        ],
        "news": [
            {"scene": "sadaka", "title": "MWST yatoa msaada kwa familia zilizoathiriwa na mafuriko Dodoma",
             "date": "30 Jul 2026",
             "text": "MWST imekabidhi msaada wa vyakula, mavazi na vifaa vya muhimu kwa familia 120 zilizoathirika na mafuriko."},
            {"scene": "elimu", "title": "Programu ya Scholarship 2026/2027", "date": "28 Jul 2026",
             "text": "Maombi ya scholarship kwa wanafunzi wa Kidato na Vyuo yanakaribishwa hadi 31 Agosti 2026."},
            {"scene": "mkutano", "title": "Semina ya Uongozi na Maadili ya Kiislamu", "date": "20 Jul 2026",
             "text": "Semina hii inalenga kuwajengea uwezo viongozi waamini katika uongozi bora na maadili ya Kiislamu."},
        ],
        "gallery": [
            {"scene": "sadaka", "cap": "Misaada kwa Wenye Mahitaji", "count": "32 Picha"},
            {"scene": "elimu", "cap": "Elimu na Mafunzo", "count": "28 Picha"},
            {"scene": "mkutano", "cap": "Matukio na Mikutano", "count": "45 Picha"},
            {"scene": "afya", "cap": "Huduma za Afya", "count": "19 Picha"},
            {"scene": "ujenzi", "cap": "Miradi ya Maendeleo", "count": "24 Picha"},
            {"scene": "maji", "cap": "Mazingira na Uhamasishaji", "count": "17 Picha"},
        ],
        "bottom_stats": [
            {"label": "Matukio Yaliyofanyika Mwezi Huu", "value": "8 Matukio",
             "icon": "calendar", "tint": "gold", "delta": "↑ 33% kutoka mwezi jana"},
            {"label": "Habari Zilizochapishwa Mwezi Huu", "value": "12 Habari",
             "icon": "file", "tint": "green", "delta": "↑ 20% kutoka mwezi jana"},
            {"label": "Picha Zilizohudumiwa Mwezi Huu", "value": "165 Picha",
             "icon": "image", "tint": "navy", "delta": "↑ 28% kutoka mwezi jana"},
            {"label": "Wanufaika Mwezi Huu", "value": "2,450 Watu",
             "icon": "users", "tint": "teal", "delta": "↑ 15% kutoka mwezi jana"},
        ],
    }
