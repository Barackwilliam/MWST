"""
Tengeneza .mo kutoka core/translations.py bila kuhitaji GNU gettext.

Endesha:  python tools/build_mo.py
"""
import struct, sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from core.translations import CATALOG  # noqa: E402

BASE = pathlib.Path(__file__).resolve().parent.parent


def make_mo(catalog, path):
    items = sorted((k.encode("utf-8"), v.encode("utf-8")) for k, v in catalog.items())
    keys = b"\x00".join(k for k, _ in items)
    n = len(items)
    keystart = 7 * 4 + 16 * n
    valuestart = keystart + len(keys) + 1

    koffsets, voffsets = [], []
    o = keystart
    for k, _ in items:
        koffsets += [len(k), o]; o += len(k) + 1
    o = valuestart
    for _, v in items:
        voffsets += [len(v), o]; o += len(v) + 1

    out = struct.pack("Iiiiiii", 0x950412de, 0, n, 7 * 4, 7 * 4 + n * 8, 0, 0)
    out += struct.pack("i" * len(koffsets + voffsets), *(koffsets + voffsets))
    out += keys + b"\x00"
    out += b"\x00".join(v for _, v in items) + b"\x00"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(out)
    return n


header = {"": "Content-Type: text/plain; charset=UTF-8\nLanguage: en\n"}

n = make_mo({**header, **CATALOG}, BASE / "locale/en/LC_MESSAGES/django.mo")
make_mo({"": "Content-Type: text/plain; charset=UTF-8\nLanguage: sw\n"},
        BASE / "locale/sw/LC_MESSAGES/django.mo")
print(f"Imetengenezwa: {n} maneno -> locale/en/LC_MESSAGES/django.mo")
