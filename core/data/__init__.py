"""
Maudhui yasiyo ya database.

Yaliyokuwa hapa awali — `dashboards.py`, `outreach.py`, `common.REGIONS`,
`mockdata.py` — yalikuwa namba za kubuni zilizotoka kwenye picha za
muundo (wanachama 142,718, TZS 136,450,000, majina ya wafadhili
wasiokuwepo). Hazikuwa zikitumika na ukurasa wowote, lakini zilikuwa
mtego: mtu akitafuta namba kwenye msimbo angeziamini.

Zimeondolewa. Kila namba inayoonekana kwenye tovuti sasa inatoka
kwenye database.
"""
import json
from pathlib import Path

from . import common, navs, pages  # noqa: F401
from .common import MONTHS, C, tzs  # noqa: F401

_MAP = json.loads((Path(__file__).parent / "tzmap.json").read_text())

#: Mipaka ya rangi, ikiwa ni SEHEMU ya mkoa mkubwa kabisa. Rangi ni
#: ya ulinganisho, si ya idadi kamili — ndiyo maana legend nayo
#: lazima ihesabiwe kutoka kwenye data, si kuandikwa mkononi.
_BANDS = [(.60, "#0d5433"), (.35, "#12864a"), (.18, "#4cbd83")]
_BASE_SHADE = "#c9e8d5"


def tz_map(regions):
    """Rudisha mikoa ikiwa na path ya SVG + rangi kulingana na idadi."""
    if not regions:
        return []
    top = max(r["members"] for r in regions) or 1
    out = []
    for r in regions:
        ratio = r["members"] / top
        shade = next((c for edge, c in _BANDS if ratio > edge), _BASE_SHADE)
        out.append({**r, "path": _MAP.get(r["name"], ""), "shade": shade})
    return out


def tz_legend(regions):
    """
    Maelezo ya rangi za ramani, yaliyohesabiwa kutoka kwenye data halisi.

    Legend ya awali ilikuwa imeandikwa mkononi: "Zaidi ya 10,000",
    "5,000 - 10,000"... Lakini `tz_map` haipaki rangi kwa idadi kamili —
    inapaka kwa UWIANO na mkoa mkubwa. Kwa hiyo mkoa wenye wanachama 25,
    ukiwa ndio mkubwa, ulipakwa rangi ambayo legend iliiita "zaidi ya
    10,000". Ramani ilikuwa inadanganya kila aliyeiangalia.
    """
    if not regions:
        return []
    top = max(r["members"] for r in regions) or 1
    edges = [int(top * edge) for edge, _c in _BANDS]
    rows = [{"label": f"{edges[0] + 1:,}+", "color": _BANDS[0][1]}]
    for i in (1, 2):
        rows.append({"label": f"{edges[i] + 1:,} - {edges[i - 1]:,}",
                     "color": _BANDS[i][1]})
    rows.append({"label": f"0 - {edges[2]:,}", "color": _BASE_SHADE})
    return rows
