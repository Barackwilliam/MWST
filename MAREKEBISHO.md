# Marekebisho — 06 Agosti 2026

Muhtasari wa mabadiliko yaliyofanyika: picha halisi, mobile responsiveness,
na kurasa mbili mpya za kisheria.

---

## 1. Picha

| Tatizo | Suluhisho | Faili |
|---|---|---|
| Kwenye `/picha/` picha zilijaza sehemu ya juu tu, SVG ya fallback ikionekana chini | `.gallery__item img { height: 92px }` ilikuwa inashinda `.illus__img { height:100% }` kwa specificity. Imeongezwa `.illus .illus__img { height:100% }` | `static/css/mwst.css` |
| Crop ilikatia maandishi ya mabango katikati | `object-position: center 40%` kwa `.illus--card/--tall/--media/--wide` | `static/css/mwst.css` |
| `scenes/mawasiliano.jpg` haikuwepo (ilitumika mara 3) | Imetengenezwa kutoka `mkutano.jpg` — **badilisha na picha halisi ukipata** | `static/img/scenes/` |
| `hero-mosque.jpeg` nakala isiyotumika (212KB) | Imefutwa | `static/img/` |
| Picha nzito kwa mtandao wa simu | Scenes zimepunguzwa hadi 960px; matoleo ya WebP yameongezwa. **2.92 MB → 1.97 MB JPEG / 1.31 MB WebP** | `static/img/` |
| Hakuna WebP kwenye markup | `<picture>` + `<source type="image/webp">`; hero inatumia `image-set()` | `templates/components/illus.html`, `templates/public/home.html` |
| Simu ilipakua picha ya desktop | `<link rel="preload">` sasa ni `media`-scoped na inaelekeza WebP | `templates/public/home.html` |

### Ukiongeza picha mpya ya scene

1. Weka `static/img/scenes/<jina>.jpg` (upana 960px inatosha).
2. Tengeneza WebP:
   ```bash
   python -c "from PIL import Image; im=Image.open('static/img/scenes/x.jpg').convert('RGB'); im.save('static/img/scenes/x.webp','WEBP',quality=78,method=6)"
   ```
3. Picha isipokuwepo, SVG ya `components/illus.html` inaonekana badala yake — hakuna kuvunjika.

---

## 2. Mobile responsiveness

- **Hero ya nyumbani**: overlay ilikuwa `.88`/`.90` — msikiti haukuonekana kabisa.
  Sasa ni gradient ya hatua nne (`.90 → .74 → .62 → .86`).
- **`.hero__art { display:none }` kwenye ≤900px**: picha zote za hero za kurasa za ndani
  zilifichwa kwenye simu. Sasa zinaonekana chini ya maandishi (190px; 160px kwenye ≤560px).
- **Overflow kwenye `/picha/`**: `scrollWidth` 423 dhidi ya 390. Chanzo ni `.pager__nav` —
  `overflow-x:auto` haitoshi kwa sababu flex item ina `min-width:auto`. Sasa inajifunga.
- **`.chips` / `.chip` hazikuwepo kabisa kwenye CSS** — vichujio vya albamu vilionekana
  kama maandishi tu. Zimeandikwa zilingane na `.tab`.
- **`body { overflow-x: clip }`** — `clip` badala ya `hidden` kwa sababu `hidden` inavunja
  `position: sticky` ya `.pub-nav`.

Baada ya marekebisho, ukaguzi wa `scrollWidth vs clientWidth` kwenye 360px na 390px
kwa kurasa 9 hauonyeshi overflow popote.

---

## 3. Kurasa za kisheria

| Faili | Maelezo |
|---|---|
| `core/data/legal.py` | Hati zote mbili kamili, Kiswahili na Kiingereza |
| `templates/public/legal.html` | Kiolezo kimoja kinachotumika na kurasa zote mbili |
| `core/views.py` | `faragha()` na `vidakuzi()` — huchagua lugha kwa `get_language()` |
| `core/urls.py` | `/faragha/` na `/vidakuzi/` |
| `templates/public/base.html` | Viungo kwenye footer + kidirisha cha vidakuzi |
| `static/js/mwst.js` | Mantiki ya kidirisha (localStorage, mwaka mmoja) |

Hati za kisheria **hazitumii `{% trans %}`** kwa kila sentensi — hutafsiriwa na
kupitishwa nzima, kwa hiyo matoleo mawili kamili yapo kwenye `legal.py`.
Ukibadilisha toleo moja, badilisha na jingine.

### Kidirisha cha vidakuzi
Sera inaahidi "kidirisha cha mapendeleo", kwa hiyo kipo kweli:
Kubali vyote / Vya lazima tu, hifadhi ya mwaka mmoja, na kitufe cha kubadilisha
kwenye ukurasa wa Sera ya Vidakuzi.

Uchaguzi unawekwa kwenye `document.documentElement.dataset.cookieConsent`
(`"all"` au `"essential"`). Ukiongeza analytics baadaye, iwashe pale tu thamani
ni `"all"`.

---

## 4. Tafsiri — ONYO MUHIMU

**Usiendeshe `python manage.py makemessages --no-obsolete` kwenye mradi huu.**

Filter yako ya `|tr` inaita `gettext()` kwenye maandishi yanayotoka
`core/data/*.py` (mfano `"Nyumbani"`, `"Kuhusu Sisi"`). `makemessages`
haiwezi kuyaona kwenye source code, kwa hiyo inayahesabu kama *obsolete*
na kuyafuta. Nilipojaribu, entries zilishuka **1240 → 803** (hasara ya
tafsiri 437).

Njia salama ya kuongeza tafsiri mpya:

```bash
# 1. Toa katalogi kamili kutoka .mo
msgunfmt locale/en/LC_MESSAGES/django.mo > locale/en/LC_MESSAGES/django.po

# 2. Ongeza msgid/msgstr mpya mwenyewe mwishoni mwa .po

# 3. Compile
msgfmt --check -o locale/en/LC_MESSAGES/django.mo locale/en/LC_MESSAGES/django.po
```

Sasa `.po` zote mbili zipo kwenye repo (hazikuwepo awali — `.mo` tu),
kwa hiyo hatua ya 1 haihitajiki tena. Katalogi ya Kiingereza ina
**1282 entries, zote zimetafsiriwa** (zilikuwa 1239 zenye mapengo 39).

---

## 5. Kilichobaki kufanya

### 5.1 Usalama — kipaumbele cha kwanza

`config/settings.py` mistari 92–101 ina nywila ya Supabase wazi ndani ya code,
na iko kwenye git history. Sikuibadilisha kwa sababu ingevunja deploy kama
environment variables hazijawekwa kwanza.

**Hatua:**

1. Badilisha nywila kwenye Supabase (Settings → Database → Reset password).
   Kuiondoa kwenye code hakuifanyi kuwa siri — iko kwenye history.
2. Weka `DATABASE_URL` kwenye Render (Environment → Add):
   ```
   postgresql://postgres.<ref>:<NYWILA_MPYA>@aws-0-eu-west-3.pooler.supabase.com:5432/postgres?sslmode=require
   ```
3. Badilisha `settings.py`:

```python
import os
import dj_database_url

DATABASE_URL = os.environ.get("DATABASE_URL", "")

if DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(
        DATABASE_URL, conn_max_age=600, ssl_require=True)}
elif DEBUG:
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }}
else:
    raise RuntimeError(
        "DATABASE_URL haijawekwa. Weka environment variable kabla ya kuanzisha "
        "mfumo kwenye production."
    )
```

`dj-database-url` tayari iko kwenye `requirements.txt`.

### 5.2 Taarifa zinazokinzana kwenye hati zako

Hati mbili ulizonipa zinatofautiana:

| | Sera ya Faragha | Sera ya Vidakuzi |
|---|---|---|
| Tovuti | `www.muslimwelfare.or.tz` | `www.mwst.or.tz` |
| S.L.P. | `0000` | `00000` |

Nimetumia `muslimwelfare.or.tz` na S.L.P. `0000` kwa zote mbili
(`ORG_SW` / `ORG_EN` kwenye `core/data/legal.py` — sehemu moja tu ya kubadilisha).
**Thibitisha ipi ni sahihi na weka namba halisi ya S.L.P.**

### 5.3 Picha

Mabango ya MWST ndani ya picha yana maandishi ya Kiingereza yaliyofungwa —
hayatafsiriki na yanarudia kichwa cha kadi kilichoandikwa chini yake.
Kwa muda mrefu, picha zisizo na mabango zingekuwa bora zaidi, hasa kwa
thumbnails ndogo (74×56, 44×38) ambapo maandishi hayasomeki.

---

## Vidokezo vya kuendesha

Folda hii **haina** `staticfiles/` — inazalishwa na
`python manage.py collectstatic` (tayari iko kwenye `buildCommand` ya `render.yaml`).
