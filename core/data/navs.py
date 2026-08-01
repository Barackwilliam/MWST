"""
Menyu za sidebar — moja kwa kila role.
Kila menyu inafanana na picha ya dashboard husika.
"""


def _mark(items, active):
    """Weka is-active kwenye kipengele kimoja."""
    for it in items:
        if it.get("key") == active:
            it["active"] = True
        for sub in it.get("children", []):
            if sub.get("key") == active:
                sub["active"] = True
                it["active"] = True
                it["open"] = True
    return items


# ---------------------------------------------------------------------------
#  MSIMAMIZI MKUU — TAIFA
# ---------------------------------------------------------------------------
def national(active="dashboard"):
    return _mark([
        {"key": "dashboard", "label": "Dashboard", "icon": "dashboard", "url": "/taifa/"},
        {"key": "mikoa", "label": "Mikoa na Wilaya", "icon": "map", "children": [
            {"label": "Mikoa Yote", "url": "/taifa/"},
            {"label": "Wilaya", "url": "/taifa/"},
            {"label": "Ripoti za Mikoa", "url": "/taifa/"},
        ]},
        {"key": "wanachama", "label": "Wanachama", "icon": "users", "children": [
            {"label": "Orodha ya Wanachama", "url": "/wanachama/"},
            {"label": "Kadi za Uanachama", "url": "/wanachama/"},
        ]},
        {"key": "maombi", "label": "Maombi ya Uanachama", "icon": "user-check",
         "url": "/maombi/", "badge": "128"},
        {"key": "malipo", "label": "Malipo ya Ada", "icon": "wallet", "url": "/malipo/"},
        {"key": "michango", "label": "Michango", "icon": "coins", "url": "/michango/"},
        {"key": "miradi", "label": "Miradi", "icon": "building", "url": "#"},
        {"key": "matukio", "label": "Matukio", "icon": "calendar", "url": "/matukio/"},
        {"key": "habari", "label": "Habari na Picha", "icon": "image", "url": "/media/"},
        {"key": "ripoti", "label": "Ripoti & Takwimu", "icon": "chart-bar", "children": [
            {"label": "Ripoti za Uanachama"}, {"label": "Ripoti za Fedha"},
        ]},
        {"key": "ujumbe", "label": "Ujumbe (SMS/Email)", "icon": "message", "url": "#"},
        {"key": "watumishi", "label": "Watumishi", "icon": "briefcase", "url": "#"},
        {"key": "mipangilio", "label": "Mipangilio ya Mfumo", "icon": "settings", "url": "#"},
        {"key": "nyaraka", "label": "Nyaraka", "icon": "file", "url": "#"},
        {"key": "msaada", "label": "Msaada", "icon": "help", "url": "#"},
    ], active)


# ---------------------------------------------------------------------------
#  AFISA USAJILI
# ---------------------------------------------------------------------------
def usajili(active="usajili"):
    return _mark([
        {"key": "dashboard", "label": "Dashboard", "icon": "dashboard", "url": "/taifa/"},
        {"section": "Usajili & Wanachama"},
        {"key": "usajili", "label": "Usajili Mwanachama", "icon": "user-plus", "url": "/usajili/"},
        {"key": "maombi", "label": "Maombi ya Uanachama", "icon": "user-check",
         "url": "/maombi/", "badge": "18"},
        {"key": "wanachama", "label": "Wanachama", "icon": "users", "url": "/wanachama/"},
        {"key": "kadi", "label": "Kadi za Uanachama", "icon": "id-card", "url": "#"},
        {"key": "kategoria", "label": "Kategoria za Uanachama", "icon": "star", "url": "#"},
        {"key": "pointi", "label": "Pointi za Uanachama", "icon": "trophy", "url": "#"},
        {"section": "Malipo & Michango"},
        {"key": "malipo", "label": "Malipo ya Ada", "icon": "wallet", "url": "/malipo/"},
        {"key": "michango", "label": "Michango", "icon": "coins", "url": "/michango/"},
        {"key": "ripoti", "label": "Ripoti za Malipo", "icon": "chart-bar", "url": "#"},
        {"section": "Mawasiliano"},
        {"key": "ujumbe", "label": "Ujumbe (SMS/Email)", "icon": "mail", "url": "#"},
        {"key": "notisi", "label": "Notisi & Taarifa", "icon": "bell", "url": "#"},
        {"section": "Mipangilio"},
        {"key": "watumishi", "label": "Watumishi", "icon": "briefcase", "url": "#"},
        {"key": "mipangilio", "label": "Mipangilio ya Mfumo", "icon": "settings", "url": "#"},
    ], active)


# ---------------------------------------------------------------------------
#  AFISA MALIPO YA ADA
# ---------------------------------------------------------------------------
def malipo(active="malipo"):
    return _mark([
        {"key": "dashboard", "label": "Dashboard", "icon": "dashboard", "url": "/taifa/"},
        {"key": "wanachama", "label": "Wanachama", "icon": "users", "children": [
            {"label": "Orodha ya Wanachama", "url": "/wanachama/"},
            {"label": "Sajili Mwanachama", "url": "/usajili/"},
        ]},
        {"key": "maombi", "label": "Maombi ya Uanachama", "icon": "user-check",
         "url": "/maombi/", "badge": "18"},
        {"key": "malipo", "label": "Malipo ya Ada", "icon": "wallet", "children": [
            {"key": "malipo-muhtasari", "label": "Muhtasari wa Malipo", "url": "/malipo/"},
            {"label": "Rekodi Malipo", "url": "/malipo/"},
            {"label": "Malipo kwa Mwanachama", "url": "/malipo/"},
            {"label": "Malipo kwa Aina", "url": "/malipo/"},
            {"label": "Malipo Yaliyokosekana", "url": "/malipo/"},
        ]},
        {"key": "michango", "label": "Michango", "icon": "coins", "url": "/michango/"},
        {"key": "kadi", "label": "Kadi za Uanachama", "icon": "id-card", "url": "#"},
        {"key": "pointi", "label": "Pointi za Uanachama", "icon": "star", "url": "#"},
        {"key": "ripoti", "label": "Ripoti", "icon": "chart-bar", "url": "#"},
        {"key": "ujumbe", "label": "Ujumbe (SMS/Email)", "icon": "message", "url": "#"},
        {"key": "settings", "label": "Settings", "icon": "settings", "url": "#"},
        {"key": "watumishi", "label": "Watumishi", "icon": "briefcase", "url": "#"},
    ], active)


# ---------------------------------------------------------------------------
#  AFISA MICHANGO
# ---------------------------------------------------------------------------
def michango(active="michango"):
    return _mark([
        {"key": "dashboard", "label": "Dashboard", "icon": "dashboard", "url": "/taifa/"},
        {"key": "wanachama", "label": "Wanachama", "icon": "users", "url": "/wanachama/"},
        {"key": "maombi", "label": "Maombi ya Uanachama", "icon": "user-check",
         "url": "/maombi/", "badge": "18"},
        {"key": "malipo", "label": "Malipo ya Ada", "icon": "wallet", "children": [
            {"label": "Muhtasari wa Malipo", "url": "/malipo/"},
            {"label": "Rekodi Malipo", "url": "/malipo/"},
        ]},
        {"key": "michango", "label": "Michango", "icon": "coins", "children": [
            {"key": "michango-muhtasari", "label": "Muhtasari wa Michango", "url": "/michango/"},
            {"label": "Rekodi za Michango", "url": "/michango/"},
            {"label": "Michango kwa Mwanachama", "url": "/michango/"},
            {"label": "Michango kwa Aina", "url": "/michango/"},
            {"label": "Michango kwa Mradi", "url": "/michango/"},
            {"label": "Wadau na Wahisani", "url": "/wadau/"},
        ]},
        {"key": "ripoti", "label": "Ripoti", "icon": "chart-bar", "url": "#"},
        {"key": "ujumbe", "label": "Ujumbe (SMS/Email)", "icon": "message", "url": "#"},
        {"key": "matukio", "label": "Matukio", "icon": "calendar", "url": "/matukio/"},
        {"key": "miradi", "label": "Miradi", "icon": "building", "url": "#"},
        {"key": "mikoa", "label": "Mikoa na Wilaya", "icon": "map", "url": "/taifa/"},
        {"key": "watumishi", "label": "Watumishi", "icon": "briefcase", "url": "#"},
        {"key": "settings", "label": "Settings", "icon": "settings", "url": "#"},
    ], active)


# ---------------------------------------------------------------------------
#  WADAU & WAHISANI / MEDIA / MATUKIO  (menyu moja ya Msimamizi Mkuu)
# ---------------------------------------------------------------------------
def outreach(active="dashboard"):
    return _mark([
        {"key": "dashboard", "label": "Dashboard", "icon": "dashboard", "url": "/wadau/"},
        {"key": "wadau", "label": "Wadau & Wahisani", "icon": "users", "url": "/wadau/"},
        {"key": "michango", "label": "Michango", "icon": "coins", "url": "/michango/"},
        {"key": "kampeni", "label": "Kampeni", "icon": "target", "url": "#"},
        {"key": "miradi", "label": "Miradi", "icon": "building", "url": "#"},
        {"key": "matukio", "label": "Matukio", "icon": "calendar", "url": "/matukio/"},
        {"key": "ripoti", "label": "Ripoti", "icon": "chart-bar", "url": "#"},
        {"key": "ujumbe", "label": "Ujumbe (SMS)", "icon": "message", "url": "#"},
        {"key": "barua", "label": "Barua Pepe", "icon": "mail", "url": "#"},
        {"key": "media", "label": "Picha & Video", "icon": "image", "url": "/media/"},
        {"key": "arifa", "label": "Arifa", "icon": "bell", "url": "#"},
        {"key": "mawasiliano", "label": "Mawasiliano", "icon": "phone", "url": "#"},
        {"key": "mipangilio", "label": "Mipangilio", "icon": "settings", "url": "#"},
        {"key": "msaada", "label": "Msaada", "icon": "help", "url": "#"},
    ], active)


# ---------------------------------------------------------------------------
#  MWANACHAMA
# ---------------------------------------------------------------------------
def member(active="dashboard"):
    return _mark([
        {"key": "dashboard", "label": "Dashboard", "icon": "dashboard", "url": "/mwanachama/"},
        {"key": "wasifu", "label": "Wasifu Wangu", "icon": "user", "url": "#"},
        {"key": "malipo", "label": "Malipo", "icon": "wallet", "url": "#"},
        {"key": "pointi", "label": "Pointi & Faida", "icon": "star", "url": "#"},
        {"key": "matukio", "label": "Matukio", "icon": "calendar", "url": "#"},
        {"key": "msaada", "label": "Msaada & Maombi", "icon": "hand-heart", "url": "#"},
        {"key": "familia", "label": "Familia & Wategemezi", "icon": "users", "url": "#"},
        {"key": "nyaraka", "label": "Nyaraka", "icon": "file", "url": "#"},
        {"key": "taarifa", "label": "Taarifa & Matangazo", "icon": "megaphone", "url": "#"},
        {"key": "mawasiliano", "label": "Mawasiliano", "icon": "phone", "url": "#"},
        {"key": "mipangilio", "label": "Mipangilio", "icon": "settings", "url": "#"},
    ], active)


# ---------------------------------------------------------------------------
#  SUPER ADMIN (Dashibodi Kuu ya awali)
# ---------------------------------------------------------------------------
def superadmin(active="dashboard"):
    return _mark([
        {"key": "dashboard", "label": "Dashibodi", "icon": "dashboard", "url": "/"},
        {"section": "Usimamizi wa Mfumo"},
        {"key": "wanachama", "label": "Wanachama", "icon": "users", "children": [
            {"label": "Orodha ya Wanachama", "url": "/wanachama/"},
            {"label": "Sajili Mwanachama", "url": "/usajili/"},
            {"label": "Kadi za Uanachama"},
            {"label": "Familia & Wategemezi"},
        ]},
        {"key": "uanachama", "label": "Uanachama", "icon": "id-card", "children": [
            {"label": "Maombi ya Uanachama", "url": "/maombi/"},
            {"label": "Kategoria za Uanachama"},
            {"label": "Uhakiki wa Kadi"},
        ]},
        {"key": "malipo", "label": "Malipo & Michango", "icon": "wallet", "children": [
            {"label": "Malipo ya Ada", "url": "/malipo/"},
            {"label": "Michango", "url": "/michango/"},
            {"label": "Wadau & Wahisani", "url": "/wadau/"},
        ]},
        {"key": "pointi", "label": "Pointi & Tuzo", "icon": "star", "children": [
            {"label": "Muhtasari wa Pointi"}, {"label": "Kanuni za Pointi"}, {"label": "Tuzo"},
        ]},
        {"key": "ustawi", "label": "Huduma za Ustawi", "icon": "hand-heart", "children": [
            {"label": "Maombi ya Msaada"}, {"label": "Misaada Iliyotolewa"},
        ]},
        {"key": "matukio", "label": "Matukio", "icon": "calendar", "url": "/matukio/"},
        {"key": "media", "label": "Picha & Video", "icon": "image", "url": "/media/"},
        {"key": "mawasiliano", "label": "Mawasiliano", "icon": "message", "url": "#"},
        {"key": "nyaraka", "label": "Nyaraka", "icon": "file", "url": "#"},
        {"key": "ripoti", "label": "Ripoti & Takwimu", "icon": "chart-bar", "url": "#"},
        {"key": "watumiaji", "label": "Watumiaji & Ruhusa", "icon": "shield", "url": "#"},
        {"key": "mipangilio", "label": "Mipangilio ya Mfumo", "icon": "settings", "url": "#"},
    ], active)
