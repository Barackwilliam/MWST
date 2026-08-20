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
        {"key": "miradi", "label": "Miradi", "icon": "building", "url": "/mfumo/miradi/"},
        {"key": "matukio", "label": "Matukio", "icon": "calendar", "url": "/matukio/"},
        {"key": "habari", "label": "Habari na Picha", "icon": "image", "url": "/media/"},
        {"key": "ripoti", "label": "Ripoti & Takwimu", "icon": "chart-bar", "children": [
            {"label": "Ripoti za Uanachama", "url": "/pakua/wanachama/"},
            {"label": "Ripoti za Fedha", "url": "/pakua/malipo/"},
        ]},
        {"key": "ujumbe", "label": "Ujumbe (SMS/Email)", "icon": "message", "url": "/ujumbe/"},
        {"key": "watumishi", "label": "Watumishi", "icon": "briefcase", "url": "/mfumo/watumiaji/"},
        {"key": "mipangilio", "label": "Mipangilio ya Mfumo", "icon": "settings", "url": "/mfumo/mipangilio/"},
        {"key": "nyaraka", "label": "Nyaraka", "icon": "file", "url": "/media/"},
        {"key": "msaada", "label": "Msaada", "icon": "help", "url": "/mawasiliano/"},
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
        {"key": "kadi", "label": "Kadi za Uanachama", "icon": "id-card", "url": "/mfumo/kadi/"},
        {"key": "kategoria", "label": "Kategoria za Uanachama", "icon": "star", "url": "/mfumo/kategoria/"},
        {"key": "pointi", "label": "Pointi za Uanachama", "icon": "trophy", "url": "/mfumo/pointi/"},
        {"section": "Malipo & Michango"},
        {"key": "malipo", "label": "Malipo ya Ada", "icon": "wallet", "url": "/malipo/"},
        {"key": "michango", "label": "Michango", "icon": "coins", "url": "/michango/"},
        {"key": "ripoti", "label": "Ripoti za Malipo", "icon": "chart-bar", "url": "/pakua/malipo/"},
        {"section": "Mawasiliano"},
        {"key": "ujumbe", "label": "Ujumbe (SMS/Email)", "icon": "mail", "url": "/ujumbe/"},
        {"key": "notisi", "label": "Notisi & Taarifa", "icon": "bell", "url": "/mfumo/arifa/"},
        {"section": "Mipangilio"},
        {"key": "watumishi", "label": "Watumishi", "icon": "briefcase", "url": "/mfumo/watumiaji/"},
        {"key": "mipangilio", "label": "Mipangilio ya Mfumo", "icon": "settings", "url": "/mfumo/mipangilio/"},
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
        {"key": "kadi", "label": "Kadi za Uanachama", "icon": "id-card", "url": "/mfumo/kadi/"},
        {"key": "pointi", "label": "Pointi za Uanachama", "icon": "star", "url": "/mfumo/pointi/"},
        {"key": "ripoti", "label": "Ripoti", "icon": "chart-bar", "url": "/pakua/malipo/"},
        {"key": "ujumbe", "label": "Ujumbe (SMS/Email)", "icon": "message", "url": "/ujumbe/"},
        {"key": "settings", "label": "Settings", "icon": "settings", "url": "/mfumo/mipangilio/"},
        {"key": "watumishi", "label": "Watumishi", "icon": "briefcase", "url": "/mfumo/watumiaji/"},
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
        {"key": "ripoti", "label": "Ripoti", "icon": "chart-bar", "url": "/pakua/malipo/"},
        {"key": "ujumbe", "label": "Ujumbe (SMS/Email)", "icon": "message", "url": "/ujumbe/"},
        {"key": "matukio", "label": "Matukio", "icon": "calendar", "url": "/matukio/"},
        {"key": "miradi", "label": "Miradi", "icon": "building", "url": "/mfumo/miradi/"},
        {"key": "mikoa", "label": "Mikoa na Wilaya", "icon": "map", "url": "/taifa/"},
        {"key": "watumishi", "label": "Watumishi", "icon": "briefcase", "url": "/mfumo/watumiaji/"},
        {"key": "settings", "label": "Settings", "icon": "settings", "url": "/mfumo/mipangilio/"},
    ], active)


# ---------------------------------------------------------------------------
#  WADAU & WAHISANI / MEDIA / MATUKIO  (menyu moja ya Msimamizi Mkuu)
# ---------------------------------------------------------------------------
def outreach(active="dashboard"):
    return _mark([
        {"key": "dashboard", "label": "Dashboard", "icon": "dashboard", "url": "/wadau/"},
        {"key": "wadau", "label": "Wadau & Wahisani", "icon": "users", "url": "/wadau/"},
        {"key": "michango", "label": "Michango", "icon": "coins", "url": "/michango/"},
        {"key": "kampeni", "label": "Kampeni", "icon": "target", "url": "/mfumo/kampeni/"},
        {"key": "miradi", "label": "Miradi", "icon": "building", "url": "/mfumo/miradi/"},
        {"key": "matukio", "label": "Matukio", "icon": "calendar", "url": "/matukio/"},
        {"key": "ripoti", "label": "Ripoti", "icon": "chart-bar", "url": "/pakua/malipo/"},
        {"key": "ujumbe", "label": "Ujumbe (SMS)", "icon": "message", "url": "/ujumbe/"},
        {"key": "barua", "label": "Barua Pepe", "icon": "mail", "url": "/ujumbe/"},
        {"key": "media", "label": "Picha & Video", "icon": "image", "url": "/media/"},
        {"key": "arifa", "label": "Arifa", "icon": "bell", "url": "/mfumo/arifa/"},
        {"key": "mawasiliano", "label": "Mawasiliano", "icon": "phone", "url": "/mfumo/ujumbe-mawasiliano/"},
        {"key": "mipangilio", "label": "Mipangilio", "icon": "settings", "url": "/mfumo/mipangilio/"},
        {"key": "msaada", "label": "Msaada", "icon": "help", "url": "/mawasiliano/"},
    ], active)


# ---------------------------------------------------------------------------
#  MWANACHAMA
# ---------------------------------------------------------------------------
def member(active="dashboard"):
    """Menyu ya mwanachama — kurasa zake mwenyewe, si za usimamizi."""
    return _mark([
        {"key": "dashboard", "label": "Dashboard", "icon": "dashboard", "url": "/mwanachama/"},
        {"key": "wasifu", "label": "Wasifu Wangu", "icon": "user", "url": "/mwanachama/wasifu/"},
        {"key": "kadi", "label": "Kadi Yangu", "icon": "id-card", "url": "/mwanachama/kadi/"},
        {"key": "malipo", "label": "Malipo Yangu", "icon": "wallet", "url": "/mwanachama/malipo/"},
        {"key": "michango", "label": "Michango Yangu", "icon": "coins",
         "url": "/mwanachama/michango/"},
        {"key": "pointi", "label": "Pointi & Faida", "icon": "star", "url": "/mwanachama/pointi/"},
        {"key": "msaada", "label": "Msaada & Maombi", "icon": "hand-heart",
         "url": "/mwanachama/msaada/"},
        {"key": "familia", "label": "Familia & Wanufaika", "icon": "users",
         "url": "/mwanachama/familia/"},
        {"key": "matukio", "label": "Matukio", "icon": "calendar", "url": "/mwanachama/matukio/"},
        {"key": "taarifa", "label": "Taarifa & Matangazo", "icon": "megaphone",
         "url": "/mwanachama/taarifa/"},
        {"key": "habari", "label": "Habari", "icon": "file", "url": "/habari/"},
        {"key": "mawasiliano", "label": "Wasiliana Nasi", "icon": "phone", "url": "/mawasiliano/"},
    ], active)


def coordinator(active="dashboard"):
    """Menyu ya mratibu wa kanda."""
    return _mark([
        {"key": "dashboard", "label": "Dashibodi ya Kanda", "icon": "dashboard",
         "url": "/kanda/"},
        {"key": "mikoa", "label": "Mikoa na Halmashauri", "icon": "map",
         "url": "/kanda/mikoa/"},
        {"key": "wanachama", "label": "Wanachama wa Kanda", "icon": "users",
         "url": "/kanda/wanachama/"},
        {"key": "maombi", "label": "Maombi ya Uanachama", "icon": "file", "url": "/maombi/"},
        {"key": "matukio", "label": "Matukio", "icon": "calendar", "url": "/matukio/"},
        {"key": "media", "label": "Picha na Video", "icon": "image", "url": "/media/"},
        {"key": "ujumbe", "label": "Ujumbe kwa Wanachama", "icon": "message", "url": "/ujumbe/"},
        {"key": "ripoti", "label": "Ripoti", "icon": "chart-bar", "url": "/pakua/wanachama/"},
        {"key": "taifa", "label": "Muhtasari wa Taifa", "icon": "globe", "url": "/taifa/"},
    ], active)


# ---------------------------------------------------------------------------
#  SUPER ADMIN (Dashibodi Kuu ya awali)
# ---------------------------------------------------------------------------
def superadmin(active="dashboard"):
    return _mark([
        {"key": "mfumo", "label": "Usimamizi wa Mfumo", "icon": "settings", "url": "/mfumo/"},
        {"key": "dashboard", "label": "Dashibodi", "icon": "dashboard", "url": "/"},
        {"section": "Usimamizi wa Mfumo"},
        {"key": "wanachama", "label": "Wanachama", "icon": "users", "children": [
            {"label": "Orodha ya Wanachama", "url": "/wanachama/"},
            {"label": "Sajili Mwanachama", "url": "/usajili/"},
            {"label": "Kadi za Uanachama", "url": "/mfumo/kadi/"},
            {"label": "Familia & Wategemezi", "url": "/mfumo/familia/"},
        ]},
        {"key": "uanachama", "label": "Uanachama", "icon": "id-card", "children": [
            {"label": "Maombi ya Uanachama", "url": "/maombi/"},
            {"label": "Kategoria za Uanachama", "url": "/mfumo/kategoria/"},
            {"label": "Uhakiki wa Kadi", "url": "/mfumo/kadi/"},
        ]},
        {"key": "malipo", "label": "Malipo & Michango", "icon": "wallet", "children": [
            {"label": "Malipo ya Ada", "url": "/malipo/"},
            {"label": "Michango", "url": "/michango/"},
            {"label": "Wadau & Wahisani", "url": "/wadau/"},
        ]},
        {"key": "pointi", "label": "Pointi & Tuzo", "icon": "star", "children": [
            {"label": "Muhtasari wa Pointi", "url": "/mfumo/pointi/"}, {"label": "Kanuni za Pointi", "url": "/mfumo/kanuni-pointi/"}, {"label": "Tuzo", "url": "/mfumo/tuzo/"},
        ]},
        {"key": "ustawi", "label": "Huduma za Ustawi", "icon": "hand-heart", "children": [
            {"label": "Maombi ya Msaada", "url": "/ustawi/"}, {"label": "Misaada Iliyotolewa", "url": "/ustawi/?status=paid"},
        ]},
        {"key": "matukio", "label": "Matukio", "icon": "calendar", "url": "/matukio/"},
        {"key": "media", "label": "Picha & Video", "icon": "image", "url": "/media/"},
        {"key": "mawasiliano", "label": "Mawasiliano", "icon": "message", "url": "/mfumo/ujumbe-mawasiliano/"},
        {"key": "nyaraka", "label": "Nyaraka", "icon": "file", "url": "/media/"},
        {"key": "ripoti", "label": "Ripoti & Takwimu", "icon": "chart-bar", "url": "/pakua/mikoa/"},
        {"key": "watumiaji", "label": "Watumiaji & Ruhusa", "icon": "shield", "url": "/mfumo/watumiaji/"},
        {"key": "mipangilio", "label": "Mipangilio ya Mfumo", "icon": "settings", "url": "/mfumo/mipangilio/"},
    ], active)
