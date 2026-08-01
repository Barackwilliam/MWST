import json
from pathlib import Path

from . import common, navs, dashboards, outreach, pages  # noqa: F401
from .common import MONTHS, C, tzs, verse, QUOTE, REGIONS  # noqa: F401

_MAP = json.loads((Path(__file__).parent / "tzmap.json").read_text())


def tz_map(regions):
    """Rudisha mikoa ikiwa na path ya SVG + rangi kulingana na idadi."""
    if not regions:
        return []
    top = max(r["members"] for r in regions)
    out = []
    for r in regions:
        ratio = r["members"] / top
        if ratio > .6:    shade = "#0d5433"
        elif ratio > .35: shade = "#12864a"
        elif ratio > .18: shade = "#4cbd83"
        else:             shade = "#c9e8d5"
        out.append({**r, "path": _MAP.get(r["name"], ""), "shade": shade})
    return out


MAP_LEGEND = [
    {"label": "Zaidi ya 10,000", "color": "#0d5433"},
    {"label": "5,000 - 10,000",  "color": "#12864a"},
    {"label": "2,000 - 5,000",   "color": "#4cbd83"},
    {"label": "Chini ya 2,000",  "color": "#c9e8d5"},
]

ROLES = [
    {"label": "Mwanachama", "icon": "user", "url": "/mwanachama/", "tint": "green",
     "desc": "Kadi, malipo, pointi na maombi yako"},
    {"label": "Afisa", "icon": "briefcase", "url": "/usajili/", "tint": "navy",
     "desc": "Usajili, malipo na michango"},
    {"label": "Mratibu", "icon": "map", "url": "/wadau/", "tint": "purple",
     "desc": "Wadau, wahisani na kampeni"},
    {"label": "Msimamizi", "icon": "shield", "url": "/taifa/", "tint": "red",
     "desc": "Mfumo mzima na mikoa yote"},
]
