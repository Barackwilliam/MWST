# MWST Membership Management System — Frontend

Mfumo wa Usimamizi wa Uanachama wa **Muslim Welfare Society of Tanzania**.
Hatua ya sasa: **frontend prototype** yenye sample data, tayari kwa Django backend.

---

## Kuendesha (Windows)

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

Fungua: <http://127.0.0.1:8000/>

## Kurasa za Tovuti ya Umma

| Ukurasa | URL |
|---|---|
| Nyumbani | `/` |
| Kuhusu Sisi | `/kuhusu/` |
| Uanachama | `/uanachama/` |
| Huduma Zetu | `/huduma/` |
| Habari | `/habari/` |
| Matukio | `/matukio-yetu/` |
| Mawasiliano | `/mawasiliano/` |
| Jiunge Sasa | `/jiunge/` |
| Ingia / Login | `/ingia/` |

## Dashboards

| Ukurasa | URL | Maelezo |
|---|---|---|
| Msimamizi Mkuu (Taifa) | `/taifa/` | Ramani ya mikoa, fedha, miradi |
| Afisa Usajili | `/usajili/` | Wizard ya hatua 5 |
| Afisa Malipo ya Ada | `/malipo/` | Rekodi, vyanzo, waliokosekana |
| Afisa Michango | `/michango/` | Zaka, Sadaqa, Waqf, malengo |
| Wadau na Wahisani | `/wadau/` | Kampeni, wahisani, ramani |
| Matukio | `/matukio/` | Kalenda, washiriki, arifa |
| Picha na Video | `/media/` | Galeria, hifadhi, upakiaji |
| Dashibodi Kuu | `/dashibodi/` | Super admin |
| Dashibodi ya Mwanachama | `/mwanachama/` | Kadi, wallet, pointi |

Kutoka ukurasa wa mwanzo (`/`), bofya **"Au ingia kama"** kuchagua role.

---

## Vipengele vinavyohitaji backend

Kila kitufe/kiungo kisichoweza kufanya kazi bila database kina `data-backend`.
Mtumiaji akikibofya, anapata **popup (modal)** nzuri yenye ujumbe:

> "Kipengele hiki kitapatikana mfumo wa nyuma (backend) utakapokamilika.
> Kwa sasa unaona muundo na taarifa za mfano."

Kuongeza mahali pengine:

```html
<button data-backend="Kurekodi malipo">Rekodi Malipo</button>
```

---

## Muundo

```
config/              settings, urls, wsgi
core/
  data/
    common.py        rangi, miezi, aya, mikoa
    navs.py          menyu za sidebar (moja kwa kila role)
    dashboards.py    taifa, usajili, malipo, michango
    outreach.py      wadau, matukio, media, tovuti
    tzmap.json       paths za ramani ya Tanzania
  mockdata.py        dashibodi kuu + mwanachama
  views.py           <-- hapa backend itaingia
templates/
  base/              app.html, sidebar, topbar, footer, icons
  components/        kpi, kpi_stacked, kpi_note, donut_card,
                     quick_actions, tzmap
  admin_panel/       dashboards za maafisa
  member/            dashibodi ya mwanachama
  public/            tovuti ya umma + login
static/
  css/mwst.css       design tokens + components zote
  js/mwst.js         sidebar, theme, charts, toast ya backend
```

## Njia ya kuhamia backend

Templates hazitabadilika. Mfano:

```python
# SASA
def malipo(request):
    ctx = dash.malipo()

# BAADAYE
def malipo(request):
    ctx = {
        "kpis": build_payment_kpis(),
        "records": Payment.objects.select_related("member")[:10],
        ...
    }
```

Key za context zimeandaliwa zikifanana na field za model zijazo:
`membership_no`, `receipt_no`, `amount`, `category`, `status`.

---

## Lugha (i18n)

Mfumo unafanya kazi kwa **Kiswahili** na **Kiingereza**. Bofya kitufe cha lugha
kwenye topbar kubadili. Chaguo linahifadhiwa kwenye session.

- Lugha ya msingi: **Kiswahili** (`msgid` ni Kiswahili)
- Kamusi: `core/translations.py` (maneno 578)
- Compiler: `python tools/build_mo.py` -> `locale/en/LC_MESSAGES/django.mo`

Hakuna haja ya GNU gettext; compiler ni Python safi.

**Kuongeza neno jipya:**

```python
# core/translations.py
CATALOG = {
    ...
    "Neno Jipya": "New Word",
}
```

```bat
python tools/build_mo.py
```

**Kutumia kwenye template:**

```django
{% load i18n mwst_tags %}

{% trans "Neno Jipya" %}      {# maandishi ya moja kwa moja #}
{{ item.label|tr }}           {# maandishi kutoka data #}
```

Filter `|tr` inatafsiri thamani zinazotoka `core/data/`. Neno lisipopatikana
kwenye kamusi, linarudi kama lilivyo — hakuna kitakachovunjika.

---

## Design system

| Token | Thamani | Matumizi |
|---|---|---|
| `--g-950` | `#042318` | Sidebar |
| `--g-500` | `#12864a` | Primary, active |
| `--n-700` | `#1b3b6f` | Secondary (bluu) |
| `--gold-500` | `#d4af37` | Accent, wordmark |
| `--canvas` | `#f4f6f9` | Background |

Dark mode inafanya kazi kupitia toggle ya jua/mwezi kwenye topbar.

---

## Vitu vya kubadilisha

- `static/img/mwst-logo.svg` ni nembo ya muda. Weka faili rasmi.
- QR kwenye kadi ni placeholder. Backend: `qrcode` + verify URL yenye saini.
- Picha zote ni gradient placeholders. Weka picha halisi za MWST.
- Ramani ya Tanzania ni approximation. Inaweza kubadilishwa na GeoJSON halisi.

## Bado hazijajengwa

Coordination (Mkoa/Wilaya), Management Officer, Maombi ya Uanachama (orodha),
Wanachama (orodha), SMS, Barua Pepe, Role Based Dashboards.
