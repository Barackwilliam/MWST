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


---

# Awamu ya pili — 06 Agosti 2026

## 1. Signin/Register kuonekana ukiwa umeingia

`core/context_processors.py` sasa inatoa `is_authed`, `can_join` na `is_donor`
kwenye kila ukurasa. Zimetumika kwenye:

| Faili | Kilichobadilika |
|---|---|
| `templates/public/base.html` | Header: Dashibodi + Toka badala ya "Ingia / Login". Drawer: jina, jukumu na kitufe cha kutoka. |
| `templates/public/home.html` | Paneli ya kuingia kwenye hero inakuwa "Karibu tena, [jina]". |
| `_pagehero.html`, `_cta.html`, `uanachama.html` | "Jiunge Sasa" inabadilika kuwa "Dashibodi Yangu" au "Changia Sasa". |

Sheria ya `can_join`: mhisani bado anaonyeshwa "Jiunge Sasa" (anaweza kuwa
mwanachama); wengine wote tayari wamo.

Pia "Kumbuka Mimi" sasa inafanya kazi kweli — bila hiyo,
`session.set_expiry(0)` inafanya kipindi kiishe kivinjari kikifungwa.

## 2. Ukurasa wa Vifurushi

- Sehemu 11 mpya kwenye `members.Category` (ada ya usajili, ada ya mwaka,
  muda, alama, na bendera sita za faida).
- `members/migrations/0005_package_pricing.py` inaweka thamani zote za bango
  na kuunda **Diamond** kama haipo. Haiguswi `name` wala `benefits` za
  kategoria zilizopo — hizo ni maudhui ya mteja.
- Jedwali linatoka database, si maandishi ya kuandikwa kwenye kiolezo — bango
  na tovuti havitatofautiana ukibadilisha ada.
- Menyu ya header sasa: Nyumbani, Uanachama, **Vifurushi**, **Changia**, Mawasiliano.

Kubadilisha ada baadaye: Dashibodi -> Mfumo -> Kategoria za Uanachama.
Hakuna haja ya kugusa code.

## 3. Mhisani na kuchangia bila akaunti

| Njia | Kinachofanyika |
|---|---|
| `/changia/` | Fomu ya wazi. Hakuna akaunti inayohitajika. |
| `/changia/asante/<risiti>/` | Shukrani + mwaliko wa kufungua akaunti. |
| `/mhisani/jisajili/` | Akaunti ya mhisani; mchango wa mwisho unaunganishwa. |
| `/mhisani/` | Historia ya michango, jumla, na mgawanyo kwa mfuko. |

- Jukumu jipya `Role.DONOR` na `Donor.user` (OneToOne, hiari).
- Mchango unaingia kama **`pending`** — afisa wa michango ndiye anayethibitisha.
  Hakuna kinachoingia kwenye leja mpaka hapo.
- Mwaliko wa akaunti unaonekana **baada tu ya kuchangia**, si kabla, na
  unaeleza faida nne mahususi. Hakuna kulazimisha.
- `Donor` hatafutwi mara mbili: tunatafuta kwa simu/barua pepe kwanza.

## 4. Ukurasa mpya wa kuingia

Umejengwa kwa mujibu wa picha: nembo, "Karibu Tena!", hatua 1 (vigae vya
majukumu vyenye tiki), hatua 2 (fomu), Kumbuka Mimi, kigawanyo cha AU,
chaguo la OTP, na ujumbe wa usalama.

**MUHIMU — usalama:** jukumu unalochagua ni **mwongozo wa maonyesho tu**.
Ruhusa halisi zinatoka kwenye `user.role` ya akaunti. Nimejaribu: kuchagua
"Msimamizi" kisha kuingia kwa akaunti ya mwanachama kunampeleka
`/mwanachama/`, na `/taifa/` inamrudisha. Usibadilishe hili — kama jukumu
lililochaguliwa lingeamua ruhusa, mtu yeyote angeweza kuwa msimamizi.

## 5. Tafsiri

Katalogi ya Kiingereza: **1282 -> 1420 entries, zote zimetafsiriwa.**
Nimefuata njia ile ile salama (msingi ni katalogi kamili, si matokeo ya
`makemessages`). Nimejaribu `/vifurushi/`, `/changia/` na `/ingia/` kwa
Kiingereza — hakuna neno la Kiswahili lililobaki.

Kumbuka onyo la awali: **usiendeshe `makemessages --no-obsolete`.**

## 6. Vitu viwili vya kuamua

**Kigae cha "Kujitolea".** Picha yako ina majukumu sita; mfumo una matano —
hakuna jukumu la volunteer kwenye `Role`. Nimeweka kigae hicho na dokezo
linalosema wajitoleaji hutumia akaunti ya mwanachama. Ukitaka jukumu halisi
lenye dashibodi yake, ni kazi ya ziada.

**OTP.** Picha ina "Login with Phone Number (OTP)" lakini mfumo hauna huduma
ya SMS. Kwa sasa kitufe kinaelekeza kwenye ukurasa wa mawasiliano badala ya
kuahidi kitu kisichofanya kazi. OTP halisi inahitaji Beem au Africa's
Talking — awamu tofauti.

## 7. Bado halijafanyika

Usalama wa `config/settings.py` (nywila ya Supabase ndani ya code) — angalia
sehemu ya 5.1 hapo juu. Halijabadilika.



---

# Awamu ya tatu — 08 Agosti 2026

## 1. Kuhusu Sisi (`/kuhusu/`)

Maandishi rasmi ya MWST yameongezwa kwa lugha zote mbili kwenye
`core/data/about.py`: utangulizi wa aya tatu, Dira, Dhima, Tunu sita,
Tunachofanya (vitu 10), Kauli Mbiu na Motto.

Kama `legal.py`, hii ni hati inayotafsiriwa nzima — matoleo mawili kamili,
si `{% trans %}` kila sentensi. Ukibadilisha moja, badilisha na jingine.

## 2. Mawasiliano (`/mawasiliano/`)

Umejengwa upya kwa muundo wa bango rasmi: kadi sita (Anwani, Namba za Simu,
Barua Pepe, Saa za Kazi, Ramani, Mitandao), banner ya "Tuko hapa kukusaidia",
na ayah ya Al-Qur'an 5:2 chini.

Anwani: **Shariff PBZ House, Dodoma Mjini, Nyerere Square, Plot 4 Block M
Wing A4 — Ghorofa ya Tatu, S.L.P 450, Dodoma.**

Wakati wa kupima nilikuta bug: data ilikuwa `pages.py` lakini view inatumia
`queries.py`, kwa hiyo ukurasa ulionyesha kadi tupu. `public_mawasiliano()`
sasa inatumia data moja; FAQ bado zinatoka database.

## 3. Bei mpya za vifurushi

`members/migrations/0006_new_fees.py`:

| Daraja | Ada ya usajili | Ada ya mwezi |
|---|---|---|
| Bronze | 10,000 | 10,000 |
| Silver | 20,000 | 20,000 |
| **Gold** | **5,000** | **5,000** |
| Platinum | 100,000 | 100,000 |
| Tanzanite | 1,000,000 | 200,000 |

- **Diamond imestaafishwa** — haijafutwa (kumbukumbu zinabaki) bali
  imeondolewa kwenye ukurasa wa vifurushi (`is_selectable=False`,
  `registration_fee=0`).
- **Tanzanite** sasa ni daraja linaloweza kuchaguliwa, si la heshima tu,
  kwa sababu limepewa ada.
- Kigezo cha ukurasa wa vifurushi kimebadilika kutoka `annual_fee__gt=0`
  kwenda `registration_fee__gt=0`, ili madaraja ya urithi (mfano Founder)
  yasionekane.
- Ada ya mwaka haikutolewa safari hii, kwa hiyo imewekwa 0 na **safu yake
  inajificha yenyewe** hadi itakapotolewa.

### ONYO: ada ya Gold

Gold ni **5,000** — ndogo kuliko Bronze (10,000) na Silver (20,000).
Hivyo ndivyo ulivyoagiza, na nimetekeleza kama ulivyosema. Lakini
inamaanisha daraja la kati ndilo la bei ya chini kabisa kwenye jedwali la
umma — mtu anaweza kuchagua Gold kwa 5,000 badala ya Bronze kwa 10,000.

Kama ilikuwa **50,000**, badilisha thamani mbili za `"G"` kwenye
`0006_new_fees.py` kisha uendeshe migration mpya. Ni sehemu moja tu.

## 4. Hali ya majaribio ya malipo

`PAYMENTS_DEMO` kwenye `config/settings.py` (chaguo-msingi `True`).
Ikiwa `True`:

- Kidokezo cha njano kinaonekana kwenye fomu ya kuchangia: *"Malipo bado
  hayajaunganishwa ... HAKUNA pesa halisi itakayotolewa."*
- Kitufe kinasoma "Tuma Mchango (Demo)".
- Ukurasa wa shukrani unaonyesha ujumbe wa kijani: *"Imefanikiwa — lakini ni
  majaribio tu"*, pamoja na risiti halisi ili uone mtiririko mzima.

Ukiunganisha mtoa huduma, weka `PAYMENTS_DEMO=False` kwenye environment ya
Render. Hakuna kitu kingine cha kubadilisha.

## 5. Kadi za benki — hazikusanywi

Mockup zilizonipa zilikuwa na `Card Number`, `CVV` na "Save card". **Sikuweka
sehemu hizo popote**, na sitaziweka. Nimethibitisha kwa kupima: hakuna input
yenye jina la card/cvv/expiry kwenye mfumo mzima.

Sababu: kukusanya namba za kadi kwenye seva yako kunakuweka chini ya PCI-DSS
kamili — ukaguzi wa gharama kubwa kila mwaka, na dhima yote ikitokea uvujaji.
Njia sahihi ni **hosted fields** au **redirect ya gateway** (Selcom, DPO,
Flutterwave, Stripe), ambapo namba inaenda moja kwa moja kwa mtoa huduma na
haigusi seva zetu kabisa. UI inaweza kuonekana ile ile — tofauti ni pale
namba inapoingia.

## 6. Tafsiri

Katalogi ya Kiingereza: 1420 -> **1451, zote zimetafsiriwa.**
Njia ile ile salama. Kumbuka: **usiendeshe `makemessages --no-obsolete`.**

## 7. Bado halijafanyika

- Ukurasa wa Uanachama (kuondoa tiers na how-to-join, kuweka muundo wa
  infographic ya MEMBERSHIP).
- Kurasa kamili za malipo (Lipa Ada / Michango) kwa muundo wa mockup.
- Jedwali la michango ya kila mwezi/mwaka la bango la Kiswahili.
- Usalama wa `config/settings.py` — angalia sehemu 5.1.



---

# Awamu ya nne — 08 Agosti 2026

## 1. Bei — Gold imerekebishwa

`0006_new_fees.py` sasa ina bei sahihi kwa **kila sehemu ya mfumo**:

| Daraja | Ada ya usajili | Ada ya mwezi |
|---|---|---|
| Bronze | 10,000 | 10,000 |
| Silver | 20,000 | 20,000 |
| Gold | **50,000** | **50,000** |
| Platinum | 100,000 | 100,000 |
| Tanzanite | 1,000,000 | 200,000 |

Sehemu zilizosasishwa:
- `members/migrations/0006_new_fees.py` — chanzo halisi (database).
- `core/data/pages.py` — thamani za akiba zinazotumika na `/jiunge/`.
- `core/management/commands/seed.py` — usakinishaji mpya unaanza na bei sahihi.

Ukurasa wa `/vifurushi/`, `/uanachama/`, `/jiunge/` na dashibodi ya mwanachama
zote zinasoma kutoka `members.Category`, kwa hiyo hazihitaji kugusa tena.

## 2. Kichagua lugha — sasa ni droplist

`templates/components/langpick.html` (kipya) kinatumika na tovuti ya umma
(`public/base.html`) na dashibodi (`base/topbar.html`).

- Ni `<select>` halisi — lugha inabadilika mara tu unapochagua, hakuna kubonyeza.
- Majina yanaonyeshwa kwa lugha yenyewe (`name_local`): **Kiswahili / English**,
  si yaliyotafsiriwa. Awali "English" ilikuwa inaonyeshwa kama "Kiingereza".
- `<noscript>` ina kitufe cha "Nenda" ili ifanye kazi hata JavaScript ikizimwa.

## 3. Ukurasa wa Uanachama umejengwa upya

Vifurushi na hatua za zamani vimeondolewa. Sasa una muundo wa bango la
MEMBERSHIP: Kuhusu Uanachama (pamoja na hadith), Jinsi ya Kujiunga (hatua 5),
Aina za Uanachama (5), Manufaa (16), Wajibu wa Mwanachama (8), Jinsi Uanachama
Unavyokoma (8 + onyo), na Kwa Nini Kujiunga.

Maudhui yapo `core/data/membership.py` kwa lugha zote mbili.
**Bei hazipo hapo** — kuna kiungo kinachoelekeza `/vifurushi/`, ili kuwe na
chanzo kimoja tu cha bei.

## 4. Bug ya `hide-xs`

Nilipoweka droplist, header ilianza kuvuja 15px kwenye simu. Chanzo halisi:
class `hide-xs` ilitumika kwenye `base.html` **lakini haikuwahi kufafanuliwa
kwenye CSS**, kwa hiyo maandishi "Ingia / Login" yalikuwa yanaonekana daima
na kubana header. Ilikuwa ipo tangu awali — droplist ndiyo iliifichua tu.

Imefafanuliwa sasa. Nimejaribu 320px, 360px, 390px na 430px kwa kurasa nane:
hakuna overflow popote.

## 5. Tafsiri

Katalogi ya Kiingereza: **1457, zote zimetafsiriwa.**
Nimejaribu `/uanachama/` kwa lugha zote mbili — sehemu zote zinabadilika
("KUHUSU UANACHAMA" -> "ABOUT MEMBERSHIP" n.k.), hakuna Kiswahili
kilichobaki kwenye toleo la Kiingereza.

## 6. Bado halijafanyika

- Kurasa kamili za malipo kwa muundo wa mockup (Lipa Ada / Michango yenye
  hatua nne, uteuzi wa mtoa huduma, aina za michango kama Zakat, Sadaqah,
  Waqf n.k.). Hali ya demo ipo tayari na inafanya kazi kwenye `/changia/`.
- Jedwali la michango ya kila mwezi/mwaka la bango la Kiswahili.
- Usalama wa `config/settings.py` — angalia sehemu 5.1.



---

# Awamu ya tano — 08 Agosti 2026

## Ukurasa wa Michango umejengwa upya (`/changia/`)

Muundo wa mockup ya MICHANGO, sehemu tano zenye namba pamoja na paneli ya
muhtasari inayobadilika papo hapo:

1. **Chagua Aina ya Mchango** — vigae 16: Zakat, Sadaqah, Waqf, Kafara,
   Futari/Iftar, Qurbani, Elimu ya Kiislamu, Yatima, Afya na Matibabu,
   Mradi wa Visima, Ujenzi wa Misikiti, Scholarship, Chakula kwa Wahitaji,
   Misaada ya Dharura, Miradi ya Maendeleo, Michango ya Jumla.
2. **Kiasi cha Kuchangia** — viwango vya haraka saba + kiasi cha mwenyewe,
   pamoja na fedha saba (TZS, USD, EUR, GBP, AED, SAR, KES).
3. **Rudia Mchango** — Mara Moja, Kila Wiki, Kila Mwezi, Kila Robo Mwaka,
   Kila Nusu Mwaka, Kila Mwaka.
4. **Njia ya Malipo** — M-Pesa, Airtel Money, Mixx by Yas, HaloPesa, T-Pesa,
   EzyPesa, Benki, Visa/Mastercard, PayPal.
5. **Taarifa za Mchangiaji** — jina, simu, barua pepe, mkoa, ujumbe, na
   chaguo la kuchangia bila jina.

Muhtasari upande wa kulia unaonyesha aina, kiasi, kurudia, njia, ada (0) na
jumla — vyote vinabadilika papo hapo bila kupakia ukurasa upya.

### Faili
| Faili | Kazi |
|---|---|
| `core/data/giving.py` | Katalogi: aina, kurudia, watoa huduma, fedha, viwango |
| `core/forms.py` | `PublicDonationForm` (si ModelForm tena) |
| `core/views.py` | `changia()` |
| `templates/public/changia.html` | Ukurasa |
| `finance/migrations/0003_...` | `purpose`, `recurrence`, `currency`, `entered_amount` |

### Fedha
Kiasi kinahifadhiwa **mara mbili**: `entered_amount` (kama mtoaji
alivyokiweka, mfano USD 100) na `amount` (TZS). Hivyo kumbukumbu zote za
kifedha zinabaki kwa sarafu moja bila kupoteza alichokiweka.

**ONYO:** viwango vya kubadilisha fedha vipo `giving.py` na ni vya **mfano
tu** — havisasishwi. Ukiunganisha gateway, chukua kiwango kutoka kwake.

### Kadi
Bado hakuna sehemu ya namba ya kadi wala CVV, na kuna maandishi wazi
yanayoeleza kwamba kadi ikitumika mtu atapelekwa kwenye ukurasa salama wa
mtoa huduma. Hii ndiyo njia pekee sahihi (PCI-DSS).

## Tafsiri
Katalogi: **1508 entries, zote zimetafsiriwa.** Aina za michango na kurudia
zinatafsiriwa kupitia `giving.localise()` (si gettext) kwa sababu ni data,
si maandishi ya kiolezo.

## Bado halijafanyika
- Ukurasa wa "Lipa Ada ya Uanachama" (mockup ya LIPA ADA / Donate-Pay
  Membership yenye hatua nne). Michango imekamilika; ada ya uanachama bado
  inatumia fomu ya zamani.
- Jedwali la michango ya kila mwezi/mwaka la bango la Kiswahili.
- Usalama wa `config/settings.py` — sehemu 5.1.



---

# Awamu ya sita — 08 Agosti 2026

## Ukurasa wa Lipa Ada (`/lipa/`)

Muundo wa mockup ya LIPA ADA / Donate-Pay Membership:

- **Kiashiria cha hatua nne** juu (Chagua, Taarifa, Malipo, Thibitisha).
- **Kadi tano za vifurushi** zenye ngao ya rangi ya daraja, bei ya mwezi,
  faida nne, na kitufe cha "Chagua X" chenye rangi ya daraja.
- **Kipindi cha Malipo** — vigae vinne vinavyoonyesha bei halisi ya kila
  kipindi na punguzo lake.
- **Taarifa za Mlipaji**, **Njia ya Malipo** (makundi matatu), na
  **Muhtasari wa Malipo** unaobadilika papo hapo.
- **Safu ya uaminifu** chini (SSL, risiti, uwazi, msaada).

### Vipindi na punguzo

| Kipindi | Miezi | Punguzo |
|---|---|---|
| Kila Mwezi | 1 | — |
| Robo Mwaka | 3 | 5% |
| Nusu Mwaka | 6 | 10% |
| Mwaka Mzima | 12 | 15% |

Bei **hazijaandikwa mkononi**. Zinahesabiwa kutoka `Category.monthly_fee`.
Mfano kwa Gold (50,000/mwezi): 50,000 / 142,500 / 270,000 / 510,000.
Ukibadilisha ada ya mwezi, vipindi vyote vinajirekebisha vyenyewe.

### Usalama wa bei

`MembershipPaymentForm.totals()` **inahesabu upya kiasi kwenye seva** kutoka
kwenye database. Kiasi hakichukuliwi kutoka kwenye fomu, kwa hiyo mtu hawezi
kubadilisha bei kwenye kivinjari akalipa kidogo. Hii ni muhimu — ni aina ya
udhaifu niliyoukuta kwenye Mudandaza (`make_sale` price injection).

## Hitilafu mbili nilizokutana nazo

1. **`Decimal` na `float` hazichanganyiki** — `period_price()` ilikuwa
   inavunjika kwa 500. Imerekebishwa kwa kubadilisha `monthly_fee` kuwa float.
2. **`intcomma` haiwekagi koma** kwenye lugha ya `sw`, kwa sababu inategemea
   kitenganishi cha maelfu cha locale na Kiswahili hakina. Bei zilikuwa
   zinaonekana "TZS 10000". Suluhisho: `intcomma:False` inalazimisha koma.

## Tafsiri
Katalogi: **1548 entries, zote zimetafsiriwa.** `/lipa/` imejaribiwa kwa
lugha zote mbili — MEMBERSHIP PACKAGES, PAYER DETAILS, Monthly/Quarterly/
Half Year/Full Year — hakuna Kiswahili kilichobaki.

## Ukaguzi wa mwisho
Kurasa 12 zote zinarudi 200. Hakuna overflow kwenye 360px wala 390px.

## Bado halijafanyika
- Jedwali la michango ya kila mwezi/mwaka la bango la Kiswahili. **Sikuliweka
  kwa makusudi**: bei zake (Shaba 10,000 / Fedha 25,000 / Dhahabu 50,000 /
  Almasi 100,000+ kwa mwezi; 120,000 / 300,000 / 600,000 / 1,200,000+ kwa
  mwaka) zinapingana na bei ulizothibitisha tarehe 08 Agosti. Nikiliweka,
  tovuti ingekuwa na bei mbili tofauti kwenye kurasa tofauti.
- Usalama wa `config/settings.py` — sehemu 5.1.



---

# Awamu ya saba — 08 Agosti 2026

## Uboreshaji wa muonekano wa mfumo mzima

Hii ni **safu ya kuboresha**, si kuandika upya. Imewekwa mwishoni mwa
`mwst.css` na inaboresha vipimo vya msingi ili mfumo mzima ubadilike kwa
pamoja, badala ya kurekebisha ukurasa mmoja mmoja.

### Herufi
- **Archivo** imeongezwa kwa vichwa (`--font-display`). Ni grotesque yenye
  mwonekano wa kitaasisi inayokaa vizuri kwenye maandishi ya herufi kubwa
  yanayotumika sana kwenye mabango ya MWST. Inter ilikuwa inatumika kila
  mahali — ni safi lakini haina utambulisho.
- **Inter** inabaki kwa maandishi ya kawaida, **Amiri** kwa Kiarabu.
- Mizani ya ukubwa (`--t-2xs` hadi `--t-4xl`) yenye uwiano wa 1.2/1.25,
  badala ya namba zilizochaguliwa kiholela.
- Eyebrow sasa zina nafasi ya herufi ya `.16em` — zinaakisi mtindo wa
  mabango.

**Gharama:** Archivo ni takribani 40KB (uzito 3). Nimeiongeza kwenye
`preconnect` iliyopo na `display=swap`, kwa hiyo maandishi yanaonekana kabla
herufi haijapakuliwa.

### Kivuli
Vivuli vilikuwa vya kijivu (`rgba(15,23,42,...)`) — mwonekano wa
chaguo-msingi. Sasa vina mguso wa kijani cha brand (`rgba(4,35,24,...)`) na
tabaka mbili, kwa hiyo kadi zinaonekana zimekaa juu ya ukurasa badala ya
kuchorwa juu yake.

### Ufikivu
- **`prefers-reduced-motion` sasa inaheshimiwa na `.reveal`.** Awali kanuni
  hiyo ilikuwepo lakini ilishughulikia `animation` na `transition` za jumla
  tu — `.reveal` ina `opacity: 0` ya awali, kwa hiyo mtu mwenye usikivu wa
  mwendo alikuwa bado anaona kila sehemu ikitembea. Nimethibitisha:
  `opacity` sasa ni `1` moja kwa moja.
- Pete ya focus ni ya dhahabu, inaonekana wazi juu ya kijani na juu ya
  nyeupe pia (kijani juu ya kijani hakikuonekana).
- Sehemu zote za fomu zina mrejesho unaofanana wa kugusa.

### Uchapishaji
Kurasa za kisheria na risiti sasa zinachapishwa safi — menyu, vitufe,
kidirisha cha vidakuzi na paneli za pembeni zinaondolewa, na viungo
vinaonyesha anwani yake.

## Hitilafu mbili nilizozikuta

**Maoni ya Django ya mistari miwili yanaonekana kwenye ukurasa.**
`{# ... #}` ya Django **haiwezi kuvuka mstari mmoja**. Nilipoandika maoni ya
mistari miwili kwenye `base.html`, yalionekana kama maandishi juu kabisa ya
kila ukurasa. Nilipoichunguza zaidi nikakuta na `langpick.html` ilikuwa na
tatizo lilelile — lilikuwepo tangu awamu ya nne bila kuonekana kwenye
majaribio yangu. Zote mbili zimebadilishwa kwenda `{% comment %}`.

Kwa siku zijazo: maoni yanayovuka mstari lazima yatumie `{% comment %}`.

## Ukaguzi wa mwisho
- Kurasa 12 zote zinarudi 200, hakuna maoni yanayovuja.
- Hakuna overflow kwenye 360px, 390px wala 768px.
- `prefers-reduced-motion` inafanya kazi.

## Bado halijafanyika
- Jedwali la michango la bango la Kiswahili — bado linapingana na bei za leo.
- Usalama wa `config/settings.py` — sehemu 5.1.



---

# Awamu ya nane — 08 Agosti 2026

## 1. Nukuu zinazoteleza (ukurasa wa mwanzo)

Sehemu mpya kati ya takwimu na CTA, yenye nukuu tano: Qur'an 3:92 (pamoja
na maandishi ya Kiarabu), hadith tatu, na ujumbe wa kampeni ya MUWESTA.

- Rangi ni kijani kizito na muundo wa kijiometri wa Kiislamu — isome kama
  ukuta wa msikiti, si kadi ya matangazo.
- Hujisogeza kila sekunde 9, **lakini husimama** mtu akiweka kishale au
  akitumia kibodi. Nukuu ndefu zinahitaji muda wa kusoma.
- Mishale, vitone na mishale ya kibodi (kulia/kushoto).
- `prefers-reduced-motion` inaheshimiwa: kujisogeza kunazimwa kabisa.
- `aria-hidden` inabadilika kwa kila slaidi ili programu za wasioona zisome
  nukuu moja tu.

Maudhui yapo `core/data/verses.py`. **Maandishi ya Kiarabu yasibadilishwe
bila kuthibitisha na mtaalamu** — kosa dogo la herufi kwenye aya linabadilisha
maana. Ndiyo maana nimeyaweka sehemu moja tu, si kwenye kiolezo.

## 2. MWST -> MUWESTA

Nimebadilisha **maandishi yanayoonekana** kwenye faili 49 (mistari 326) na
**rekodi 2,200 kwenye database** kupitia `core/migrations/0002_rebrand_muwesta.py`.

Kubadilisha code peke yake hakukutosha — habari, matukio, maswali, historia
na maelezo ya picha yapo kwenye database, si kwenye faili.

### Vilivyobaki MWST kwa makusudi

| Kitu | Sababu |
|---|---|
| `mwst_tags`, `mwst.css`, `mwst.js`, `mwst-logo.svg` | Majina ya faili na moduli. Kubadilisha kunavunja `{% load %}` na `{% static %}`. |
| `mwst-cookie-consent` | Ufunguo wa localStorage. Ukibadilika, kila mtu aliyekwisha kubali vidakuzi ataulizwa tena. |
| `MWST.css()` | Kitambulisho cha JavaScript kwenye chati. |
| `mwst.or.tz` | Kikoa halisi. |
| `@MWSTanzania` | Akaunti halisi za mitandao. |
| `MWST/{daraja}/{namba}/{mwaka}` | **Namba za uanachama.** |
| `MWST-M-000123` | **Namba za risiti.** |

### Uamuzi unaohitajika kwako: namba za uanachama na risiti

Hizi sikubadilisha kwa sababu si maandishi — ni vitambulisho. Wanachama
waliopo tayari wana kadi zilizochapishwa zenye `MWST/G/000123/2026`, na
wahisani wana risiti zenye `MWST-M-000481`.

Chaguo tatu:
1. **Ziache** — kadi na risiti zilizopo zinabaki sahihi. Rahisi zaidi.
2. **Badilisha kwa wapya tu** — `MUWESTA/...` kuanzia sasa. Kutakuwa na
   miundo miwili kwenye mfumo, lakini hakuna kadi itakayoharibika.
3. **Badilisha zote** — inahitaji kutoa upya kadi zote na kuwaarifu
   wanachama. Kumbukumbu za nyuma hazitalingana na zilizo mikononi mwao.

Napendekeza namba 2. Niambie ukiamua.

## 3. Ukaguzi
- Kurasa 12 zote 200; **hakuna "MWST" inayoonekana popote** kwenye maandishi.
- Nukuu zinafanya kazi kwa Kiswahili na Kiingereza.
- Hakuna overflow kwenye 360px wala 390px.
- Katalogi: **1552 entries, zote zimetafsiriwa.**



---

# Awamu ya tisa — 09 Agosti 2026

## Vitambulisho: chaguo namba 2 limetekelezwa

Vitambulisho **vipya** vinaanza na `MUWESTA`; vya **zamani** vinabaki
kama vilivyo.

| Kitu | Kabla | Kuanzia sasa |
|---|---|---|
| Namba ya uanachama | `MWST/G/000123/2026` | `MUWESTA/G/000124/2026` |
| Namba ya kadi | `MWST/G/00123/2026` | `MUWESTA/G/00124/2026` |
| Kumbukumbu ya maombi | `APP/MWST/2026/0012` | `APP/MUWESTA/2026/0013` |
| Namba ya risiti | `MWST-M-000481` | `MUWESTA-M-000487` |

### Jinsi inavyofanya kazi

Kianzio kipo sehemu moja tu — `ID_PREFIX` kwenye `config/settings.py`:

```python
ID_PREFIX = os.environ.get("ID_PREFIX", "MUWESTA")
```

Kila mahali panapotengeneza kitambulisho panasoma hapo. Ukitaka kubadilisha
tena baadaye, ni mstari mmoja (au environment variable kwenye Render).

**Hakuna migration inayohitajika.** Namba za mfuatano zinatoka
`Sequence.next()`, ambayo haitegemei kianzio kabisa — kwa hiyo mfuatano
unaendelea pale ulipoishia. Rekodi za zamani zimehifadhi maandishi yao
kama yalivyo; hakuna kinachoandikwa upya.

### Kilichothibitishwa

```
risiti ya kwanza (ya zamani):     MWST-M-000002
mwanachama wa kwanza (wa zamani): MWST/S/000001/2024
risiti mpya:                       MUWESTA-M-000487
risiti 80 na wanachama 383 wa MWST wamebaki bila kuguswa
```

Nimejaribu pia kwa kivinjari: mchango mpya kupitia `/changia/` ulitoa
`MUWESTA-M-000487`.

### Kinachotarajiwa

Mfumo utakuwa na **miundo miwili ya vitambulisho** kwa muda mrefu. Hii ni
sahihi na ndiyo lengo la chaguo namba 2 — kadi zilizo mikononi mwa
wanachama zinaendelea kulingana na zilizo kwenye mfumo.

Ukitafuta mwanachama kwa namba, kumbuka kuwa wa zamani wana `MWST/` na
wapya wana `MUWESTA/`. Utafutaji kwenye mfumo unatumia `icontains`, kwa
hiyo kuandika `000123` peke yake kunafanya kazi kwa wote wawili.

Placeholder kwenye `/lipa/` imesasishwa kuonyesha muundo mpya.



---

# Awamu ya kumi — 09 Agosti 2026

## Aina ya kitambulisho ni droplist sasa

Sehemu ya "National ID (NIDA)" ilikuwa kisanduku kimoja cha maandishi
kinachodhania kila mtu ana NIDA. Sasa kuna sehemu mbili:

1. **Aina ya Kitambulisho** (droplist) — NIDA, Leseni ya Udereva, Kadi ya
   Mpiga Kura, Pasipoti, Kitambulisho cha Kazi, Kitambulisho Kingine cha
   Uanachama.
2. **Namba ya Kitambulisho** — kama ilivyokuwa.

### Faili
| Faili | Kilichobadilika |
|---|---|
| `members/models.py` | `ID_TYPES` + sehemu ya `id_type` kwenye `Member` na `Application` |
| `members/migrations/0007_...` | Migration |
| `core/forms.py` | `ApplicationForm` na fomu ya wafanyakazi |
| `templates/member/dashboard.html` | "NIDA" iliyoandikwa mkononi imeondolewa |
| `templates/admin_panel/mwanachama_detail.html` | Lebo inaonyesha aina halisi |
| `templates/admin_panel/usajili.html` | Sehemu mpya imeongezwa kwenye fomu |

### Maamuzi mawili

**Chaguo tupu "---------" limeondolewa.** Django huliongeza kwenye sehemu
zisizo za lazima. Hapa halina maana — NIDA ndiyo chaguo-msingi, na mtu
asiyekuwa na kitambulisho anaacha namba tu wazi.

**"NIDA" iliyoandikwa mkononi kwenye dashibodi imeondolewa.** Ilikuwa
inaonyesha "NIDA" hata kama mtu ametumia pasipoti. Sasa inatumia
`get_id_type_display()`.

Aina ya kitambulisho inanakiliwa ombi linapogeuzwa kuwa uanachama.

### Kilichojaribiwa
Ombi halisi kupitia `/jiunge/` lenye pasipoti lilihifadhiwa sahihi:
```
APP/MUWESTA/2026/0146 | Hawa Juma Mrisho | passport -> Pasipoti | TZ9911223
```
Chaguo zinatafsiriwa: NIDA / Driving Licence / Voter\'s Card / Passport /
Employee ID / Other Membership Card. Hakuna overflow kwenye 390px.

Katalogi: **1559 entries, zote zimetafsiriwa.**



---

# Awamu ya kumi na moja — 10 Agosti 2026

## 1. Ukanda wa matangazo (juu kabisa ya ukurasa wa mwanzo)

Umewekwa **juu ya hero**, ndipo jicho linapoanzia. Matangazo yanabadilishana
kila sekunde 6; kubofya kunafungua ukurasa wa maelezo kamili
(`/matangazo/<id>/`). Kuna pia ukurasa wa yote (`/matangazo/`).

**Uamuzi wa muundo:** kinachong'aa ni **nukta ndogo pekee**, si maandishi.
Maandishi yanayomeremeta ni magumu kusoma, na yanaweza kumdhuru mtu mwenye
kifafa cha mwanga. Nukta ina mpigo laini wa sekunde 2.4 unaovuta jicho bila
kuwa kero, na `prefers-reduced-motion` unauzima kabisa.

Ukanda husimama mtu akiweka kishale au akitumia kibodi, na `aria-hidden`
inabadilika ili programu za wasioona zisome tangazo moja tu.

## 2. Uidhinishaji: Msimamizi ndiye wa mwisho

Sehemu mpya kwenye `Announcement`: `status` (rasimu / inasubiri / imeidhinishwa
/ imekataliwa), `is_urgent`, `created_by`, `approved_by`, `approved_at`,
`review_note`.

- Afisa na Mratibu wanaweza kuandaa tangazo.
- **Wakichagua "Imeidhinishwa" wenyewe, mfumo unairudisha "Inasubiri idhini"**
  na kuwaambia. Msimamizi pekee ndiye anayeweza kuidhinisha.
- Umma unaona yaliyoidhinishwa **pekee** — kigezo kimewekwa kwenye kila
  query ya matangazo, si kwenye kiolezo. Hivyo hakuna njia ya kulipita.

Bila kizuizi hiki, mtu yeyote mwenye akaunti ya ofisi angeweza kuchapisha
chochote kwa jina la MUWESTA kwenye ukurasa wa mwanzo.

Matangazo matatu yaliyokuwepo yamewekwa "imeidhinishwa" na migration
ili yasitoweke ghafla.

## 3. Viongozi wapya

Orodha ya zamani (4) imeondolewa; wapya (6) wamewekwa kupitia
`content/migrations/0004_muwesta_leaders.py` ili wafike Render pia:

Mwenyekiti Ramadhani Juma Hussein; Makamu Mwenyekiti Ramadhani Juma Magembe;
Katibu Yahya Idd Nyambo; Katibu Msaidizi Jumaa Bakari Mashango;
Mweka Hazina Mohammed O. Kapera; Mweka Hazina Msaidizi Omari Mziray.

## 4. Kiswahili ndiyo lugha ya msingi

`core/middleware.py` -> `DefaultSwahiliMiddleware`.

Django hupanga lugha hivi: session -> cookie -> **`Accept-Language`** ->
settings. Kwa hiyo `LANGUAGE_CODE = "sw"` **haikutosha** — mtu mwenye
kivinjari cha Kiingereza alikuwa anapata tovuti ya Kiingereza bila kuomba.

Middleware inaondoa `Accept-Language` kabla `LocaleMiddleware` haijaisoma,
ILI MRADI mtumiaji hajachagua lugha mwenyewe. Akichagua, chaguo lake
linahifadhiwa na hili halimgusi tena.

Imethibitishwa kwa kivinjari chenye `Accept-Language: en-US`: ukurasa
ulikuja kwa Kiswahili; baada ya kuchagua English, ukabaki Kiingereza.

## 5. Ukaguzi
Kurasa zote 200; hakuna overflow kwenye 360px wala 390px.
Katalogi: **1579 entries, zote zimetafsiriwa.**



---

# Awamu ya kumi na mbili — 10 Agosti 2026

## Ukanda wa matangazo umeimarishwa

Ulikuwa kijani kizito — ulizama kati ya utility bar ya kijani na hero ya
kijani. Sasa ni ukanda wa tahadhari unaotofautiana wazi:

| Kipengele | Kabla | Sasa |
|---|---|---|
| Msingi | Kijani kizito | Krimu-nyekundu, mstari mzito mwekundu chini |
| Maandishi | Nyeupe, uzito wa kawaida | **Nyekundu nzito (#991b1b), Archivo, 15px, bold** |
| Lebo | Dhahabu hafifu | Bloku nyekundu nzito, herufi nyeupe |
| Kitufe | Kiungo cha maandishi | Kitufe cha "SOMA" chekundu chenye mpigo |
| Mwendo | Nukta pekee | Ikoni inaruka, mwanga unapita, kitufe kinapiga |

### Mwendo — na kile nisichokifanya

Umeomba imeremete. Nimeweka mwendo wa aina **tatu** unaovuta jicho:
ikoni ya megaphone inaruka juu-chini (1.6s), mwanga hafifu unapita ukanda
mzima (5.5s), na kitufe cha SOMA kina pete inayotanuka (2.2s).

Lakini **maandishi yenyewe hayameremeti.** Sababu mbili: maandishi
yanayozimika na kuwaka ni magumu kusoma — na tangazo lipo ili lisomwe, si
lipendeze tu. Pili, kumeremeta zaidi ya mara 3 kwa sekunde kunaweza
kusababisha kifafa cha mwanga (WCAG 2.3.1). Mwendo wote niliouweka uko
chini ya kiwango hicho kwa mbali.

Kama bado hautoshi kuvuta usikivu, njia salama za kuongeza ni: kufanya
ukanda mnene zaidi, kuongeza ikoni kubwa, au kutumia rangi kali zaidi —
si kuongeza kasi ya kumeremeta.

### Mwonekano wa giza
Krimu ingeng'aa sana usiku, kwa hiyo mwonekano wa giza unatumia nyekundu
nzito yenye maandishi ya `#fca5a5`.

### Simu
Chini ya 760px: lebo na hesabu zinafichwa, kichwa cha tangazo kinapata
mistari miwili badala ya kukatwa, na kitufe cha SOMA kinabaki.

`prefers-reduced-motion` inazima mwendo wote — rangi pekee inabaki
kuvuta jicho.



---

# Awamu ya kumi na tatu — 10 Agosti 2026

## Picha ya Ofisi Kuu

Picha ya `msikiti` (scene ya jumla) kwenye kadi ya "Anwani ya Makazi"
imebadilishwa na picha ya jengo la Ofisi Kuu.

- `static/img/ofisi-kuu.jpg` (106 KB) na `.webp` (72 KB), upana 900px —
  inaonyeshwa kwa ~361px, kwa hiyo 900px inatosha hata kwa skrini za 2x.
- Inatumia `<picture>` na WebP kama picha nyingine zote.
- `loading="lazy"` na `width`/`height` zimewekwa ili ukurasa usiruke
  picha inapopakuliwa.

### Maelezo chini ya picha

Nimeongeza `figcaption`: **"Muundo wa Ofisi Kuu inayopendekezwa — Dodoma"**.

Sababu: bango lililo kwenye picha yenyewe linasema "PROPOSED HEAD OFFICE".
Kadi hiyo inaonyesha anwani halisi ya ofisi iliyopo (Shariff PBZ House,
Nyerere Square). Bila maelezo, mtu angedhani jengo hilo ndilo la kwenda
leo — na akifika Nyerere Square asilione, ni aibu kwa shirika.

Ukiniambia jengo hili tayari limejengwa, nitaondoa neno
"inayopendekezwa" mara moja.

### Jambo la kuzingatia

Bango la jengo kwenye picha bado linasoma **"MUSLIM WELFARE SOCIETY OF
TANZANIA (MWST)"**. Tovuti sasa inatumia MUWESTA kila mahali, kwa hiyo
picha inatofautiana na maandishi yaliyo kando yake. Hilo ni suala la
muundo wa picha, si code — litahitaji picha mpya wakati jina jipya
litakapowekwa kwenye michoro.



---

# Awamu ya kumi na nne — 10 Agosti 2026

## Nukuu zimehamishwa juu na kupewa muonekano mpya

Zilikuwa chini kabisa, kabla ya CTA — watu wengi hawakufika hapo. Sasa
zipo **mara baada ya hero (sehemu ya kuingia)**, ndipo mtu anapoendelea
baada ya kuona ujumbe wa mwanzo.

### Muonekano

Hero iliyo juu yake ni kijani kizito. Sehemu hii ikiwa nayo nzito, ukurasa
ungeonekana mzito mno — kwa hiyo ni **krimu nyepesi yenye tao la mihrab la
dhahabu**, isome kama ukurasa wa msahafu ulioangaziwa, si kadi ya tovuti.

- Tao la mihrab (`.verses__arch`) lenye mstari wa ndani — ni alama ile ile
  inayotumika kwenye hero za kurasa za ndani, kwa hiyo si pambo geni.
- Pambo la pembe mbili (juu-kushoto, chini-kulia) na nyota ya dhahabu juu.
- Kiarabu: kijani kizito, `Amiri`, hadi 33px.
- Tafsiri: `Archivo`, hadi 23px, wino wa kijani-nyeusi.
- Mwonekano wa giza una toleo lake — krimu ingeng'aa sana usiku.

## Hitilafu niliyoifanya na kuirekebisha

Nilipobadilisha CSS ya nukuu nilitumia `s.index()` kutafuta mwanzo na
mwisho wa block. Lakini alama ya "mwisho" niliyochagua (KIDOKEZO CHA HALI
YA MAJARIBIO) ilikuwa **kabla** ya block ya nukuu kwenye faili, si baada
yake. Matokeo: `s[:start] + new + s[end:]` ilirudia takribani mistari 700
ya CSS, ikiwemo block ya zamani ya nukuu — ambayo, ikiwa ya mwisho kwenye
faili, ndiyo iliyoshinda. Ndiyo maana muonekano mpya haukuonekana.

Niligundua kwa sababu screenshot ilionyesha kijani kizito badala ya krimu
hata baada ya kulazimisha `color_scheme="light"`.

Imerekebishwa, na nimekagua faili nzima: kila kichwa cha sehemu kipo mara
**moja** tu, na mabano yanalingana (1491 kufungua, 1491 kufunga).

Somo: kwa `str.index()` ya alama mbili, lazima kuthibitisha kuwa ya pili
ipo **baada** ya ya kwanza kabla ya kukata.

## Ukaguzi
Kurasa 12 zote 200. Hakuna overflow kwenye 360px, 390px wala 768px.



---

# Awamu ya kumi na tano — 10 Agosti 2026

## "Jiunge Sasa" imeongezwa kwenye header

Ilikuwa kwenye hero, drawer na CTA pekee — si kwenye header. Sasa ipo kila
ukurasa.

### Mpangilio wa vitufe

| Kitufe | Mtindo | Sababu |
|---|---|---|
| **Jiunge Sasa** | Dhahabu (`btn--gold`) | Ndilo lengo kuu la shirika |
| **Ingia** | Tulivu (`btn--quiet`, mpaka pekee) | Ni la watu waliokwisha jiunga |

Vikiwa na rangi sawa, vyote viwili vingepoteza nguvu — kimoja lazima
kiongoze. Pia nimefupisha "Ingia / Login" kuwa "Ingia" tu; lugha
inabadilishwa na droplist iliyo kando, kwa hiyo maandishi ya lugha mbili
kwenye kitufe kimoja hayakuwa na haja.

### Kwenye simu linafichwa — kwa makusudi

Chini ya 900px, "Jiunge Sasa" linafichwa (`hide-sm`). Vipimo vilivyopimwa
kwenye upana wa header:

```
360px   langform:68  Ingia:40   burger:34   -> OK
390px   langform:68  Ingia:40   burger:34   -> OK
768px   langform:68  Ingia:89   burger:38   -> OK
1024px  langform:68  Jiunge:135 Ingia:89 burger:38 -> OK
1280px  langform:118 Jiunge:135 Ingia:89   -> OK
```

Vitufe vitatu kwenye 390px vingesababisha overflow ile ile niliyoirekebisha
awamu ya nne. Hakuna kinachopotea: drawer ina "Jiunge Sasa" ya dhahabu
wazi, na hero ya ukurasa wa mwanzo pia.

### Akiwa ameingia

- **Mwanachama / mtumishi**: "Dashibodi" + "Toka" pekee — hana cha kujiunga.
- **Mhisani**: anaendelea kuonyeshwa "Jiunge Sasa", kwa sababu bado
  anaweza kuwa mwanachama (`can_join`).

Imethibitishwa: nikiingia kama mwanachama, header inaonyesha "Dashibodi"
pekee. Kiingereza: "Join Now" / "Sign In".



---

# Awamu ya kumi na sita — 10 Agosti 2026

## Platinum imekuwa Diamond; Silver ni 25,000 kwa mwezi

| Daraja | Ada ya usajili | Ada ya mwezi |
|---|---|---|
| Bronze | 10,000 | 10,000 |
| Silver | 20,000 | **25,000** |
| Gold | 50,000 | 50,000 |
| **Diamond** (ilikuwa Platinum) | 100,000 | 100,000 |
| Tanzanite | 1,000,000 | 200,000 |

### Njia iliyotumika — na kwa nini

`members/migrations/0008_platinum_to_diamond.py` **inabadilisha jina la
safu ya Platinum**, haihamishi wanachama.

Wanachama **19** waliokuwa Platinum wamekuwa Diamond papo hapo bila rekodi
yoyote kuguswa. Njia mbadala ingekuwa kuwahamishia kwenye safu nyingine ya
Diamond — lakini hiyo ingehusisha kubadilisha `category_id` ya kila
mwanachama, na kila hatua kama hiyo ni nafasi ya kupoteza mtu njiani.

Safu ya zamani ya `Diamond` (iliyoundwa awamu ya tatu, ikastaafishwa awamu
ya nne) haikuwa na mwanachama hata mmoja, kwa hiyo imefutwa ili herufi `D`
ipatikane. Migration ina kinga: ikikutwa ina wanachama kinyume na
matarajio, haifutwi — inabadilishwa jina badala yake.

### Namba za uanachama

Wanachama 19 wa zamani wana `MWST/P/000123/2026`. **Hazibadiliki** — ni
vitambulisho vilivyochapishwa kwenye kadi, sawa na uamuzi wa chaguo namba 2.
Wapya watapata `MUWESTA/D/...`.

### Sehemu zilizosahihishwa
Marejeo **27** ya "Platinum" kwenye faili 9: `pages.py`, `queries.py`,
`dashboards.py`, `mockdata.py`, `seed.py`, `translations.py`,
`members/models.py`, `michango.html`, na `mwst.css` (`--cat-platinum` ->
`--cat-diamond`). Migration za zamani (0005, 0006) zimeachwa kama zilivyo —
zinaeleza hali ya kihistoria, si ya sasa.

Katalogi ya tafsiri nayo imesahihishwa.

### Kilichojaribiwa
Nimerudisha migrations hadi 0005 kisha kuziendesha zote upya — matokeo ni
yale yale, na wanachama 19 wamebaki Diamond. Kurasa 12 zote 200, na
**"Platinum" haionekani popote** kwa Kiswahili wala Kiingereza.

Vipindi vya Silver sasa: 25,000 / 71,200 / 135,000 / 255,000.



---

# Awamu ya kumi na saba — 10 Agosti 2026

## Pesapal imeunganishwa

| Faili | Kazi |
|---|---|
| `finance/gateways/pesapal.py` | Mteja wa API 3.0 |
| `finance/management/commands/pesapal_ipn.py` | Kusajili IPN mara moja |
| `core/views.py` | `pesapal_callback`, `pesapal_ipn`, `_pesapal_start`, `_pesapal_sync` |
| `finance/migrations/0004_...` | `gateway`, `gateway_ref` kwenye `Contribution` |
| `PESAPAL.md` | Hatua tano za kuunganisha |

### Maamuzi matatu ya usalama

**1. Siri hazipo kwenye code.** Zinatoka environment: `PESAPAL_CONSUMER_KEY`,
`PESAPAL_CONSUMER_SECRET`, `PESAPAL_ENV`, `PESAPAL_IPN_ID`, `SITE_URL`.
Huu ni mradi ambao tayari una nywila ya Supabase kwenye git history —
sikutaka kuongeza ya pili.

**2. Callback haiaminiki.** Pesapal inamrudisha mtu kwenye
`/pesapal/callback/?OrderTrackingId=...`. Mtu yeyote anaweza kuandika URL
hiyo mwenyewe. Kwa hiyo hali **HAICHUKULIWI kutoka kwenye URL** — inaulizwa
Pesapal kwa `GetTransactionStatus`. Vivyo hivyo kwa IPN.

**3. Kadi haziguse seva yetu.** Mtu analipia kwenye ukurasa wa Pesapal.
Hii ndiyo sababu niliyokataa kuweka sehemu za Card Number na CVV awamu ya
tano — sasa kuna njia sahihi ya kuzipokea.

### Kushindwa hakupotezi rekodi
Pesapal ikigoma, mchango unabaki `pending`, mtumiaji anapelekwa ukurasa wa
shukrani na maelezo, na sababu inaandikwa kwenye log. Hatupotezi rekodi
kwa sababu tu gateway imeshindwa.

### Hali ya majaribio inajizima
Funguo zikiwekwa, `PAYMENTS_DEMO` inakuwa `False` yenyewe. Bila hivyo mtu
angeambiwa "hakuna pesa itakayotolewa" wakati kuna gateway halisi.

### Kilichojaribiwa hapa
- IPN inarudisha JSON sahihi inayotarajiwa na Pesapal.
- Bila funguo, Pesapal haionekani na mtiririko wa demo unaendelea kama
  kawaida — `/changia/` ilitoa risiti MUWESTA-M-000488.
- Bila funguo, mteja hutoa `PesapalError` safi, si crash.

**Sikuweza kujaribu muamala halisi** — mazingira haya hayana ruhusa ya
kufikia `cybqa.pesapal.com`, na sina funguo (wala sitaki kuwa nazo).
Majaribio ya kweli ni hatua ya 4 kwenye `PESAPAL.md`.



---

# Awamu ya kumi na nane — 13 Agosti 2026

## Kutoka majaribio kwenda production

Ombi lilikuwa "toa demo zote". Nilipoangalia nini hasa demo ilikuwa
inashikilia, nilikuta si kibandiko tu — ilikuwa inaficha tatizo la kweli.

### Tatizo lililokuwa chini ya kibandiko

Fomu ya malipo ilikuwa inaonyesha njia **tisa**. Moja tu, Pesapal,
ilikuwa imeunganishwa. Mtu akichagua M-Pesa au Visa, mfumo ulimhifadhia
mchango na kumpa namba ya risiti — bila pesa yoyote kutoka. Kibandiko cha
DEMO ndicho kilichokuwa kinamwambia asidhani amelipa.

Kuondoa kibandiko peke yake kungeacha mfumo unaodanganya kwa ukimya. Kwa
hiyo badala ya kuficha njia zisizofanya kazi, nimezipitisha kwenye
zinazofanya kazi.

### Njia zote sasa zinapitia Pesapal

Pesapal inachukua M-Pesa, Airtel, Mixx, HaloPesa, T-Pesa, EzyPesa na kadi
kwenye ukurasa wake. Kila njia sasa ina `gateway` kwenye `giving.py`:

| Njia | gateway | Inakamilishwaje |
|---|---|---|
| M-Pesa, Airtel, Mixx, HaloPesa, T-Pesa, EzyPesa, Visa/Mastercard | `pesapal` | Redirect kwenda Pesapal |
| Uhamisho wa benki | `manual` | Afisa anathibitisha pesa ikiingia |
| PayPal | — | **Imeondolewa** |

PayPal iliondolewa kwa sababu hakuna kitu nyuma yake. Ni bora njia isiwepo
kuliko iwepo isifanye kazi. Kundi la "Lipa Mtandaoni" limevunjwa — Pesapal
si njia mbadala ya M-Pesa, ni mlango ambao M-Pesa hupitia. Imebaki kama
"Nionyeshe njia zote" kwa mtu asiyejua atumie ipi.

`giving.gateway_for(key)` hurudisha `""` kwa ufunguo usiojulikana, na
`_finish_payment` huikataa. Malipo yakatae kuanza ni bora kuliko yaende
njia isiyo sahihi kimya kimya.

### Ukurasa wa asante ulikuwa unasema uongo

Ulisoma "Hongera, na asante sana! Mchango wako umepokelewa" kwa kila
hali — hata malipo yaliyoshindwa. Sasa unategemea hali halisi:
imekamilika / hayakukamilika / yanasubiri. Kwa yaliyoshindwa unasema wazi
kwamba hakuna kilichokatwa.

Vivyo hivyo `/lipa/` ilikuwa inaonyesha "Malipo yako yamepokelewa" kabla
mtu hajafika Pesapal. Ujumbe huo umeondolewa.

### Nywila ya Supabase ilikuwa wazi kwenye kodi

`settings.py` ilikuwa na username, nywila na host za Supabase zimeandikwa
moja kwa moja, chini ya block iliyokuwa imefanywa comment ikieleza njia
sahihi. Zimehamishwa kwenda `DATABASE_URL`.

**Kuiondoa kwenye kodi hakuitoi kwenye git history.** Nywila hiyo lazima
ibadilishwe Supabase. Nimeandika hivyo kwenye `PESAPAL.md` na kwenye
`render.yaml` ili isipite bila kuonekana.

### Kinga mbili zinazozuia mfumo kuanza

**Bila `DATABASE_URL` na `DEBUG=False`** — mfumo unakataa kuanza. Awali
ungeanguka kwenye SQLite ambayo Render huifuta kila deploy; wanachama na
michango wangepotea kimya kimya na mtu angegundua baada ya wiki.

**`SITE_URL` isiyo `https://`** — mfumo unakataa kuanza. Pesapal hujenga
callback na IPN kutoka hapo. Ikiwa si sahihi, mtu anayelipa hafiki kwenye
risiti yake, na hiyo hugundulika baada ya malipo, si kabla.

Kukataa kuanza ni kali, lakini makosa haya mawili yote hujificha hadi baada
ya kuathiri mtu.

### Vilivyoondolewa

`PAYMENTS_DEMO`, `templates/components/demo_notice.html`,
`core/mockdata.py` (haikuwa inatumika popote tangu backend ianze),
CSS ya `.demo-notice`, vibandiko vya "(Demo)" kwenye vitufe,
block ya usalama iliyokuwa imerudiwa mara mbili kwenye `settings.py`,
na `payments_demo` kwenye context processor.

`DEBUG` sasa ni `False` kwa chaguo-msingi. Awali ilikuwa `True` — mtu
akisahau kuiweka kwenye Render, tovuti ingekuwa inaonyesha traceback
kamili kwa umma.

### Kilichojaribiwa

- Kurasa 12 za umma: zote 200.
- `/changia/` kwa benki: risiti inaundwa, hali `pending`, ujumbe unasema
  kutumia namba ya risiti kama kumbukumbu.
- `/changia/` kwa M-Pesa bila funguo za Pesapal: kosa wazi kwa mtumiaji,
  kosa kwenye log, rekodi haipotei.
- `/changia/` kwa M-Pesa na funguo zilizowekwa: inaenda kutafuta token,
  Pesapal ikigoma inarudi na ujumbe wa ukweli — si risiti ya mafanikio.
- `/lipa/` kwa benki: TZS 25,000 (Silver, mwezi), `pending`.
- Neno "DEMO" halionekani popote kwenye HTML iliyotolewa.
- `check --deploy`: onyo moja tu la `SECRET_KEY` ya majaribio niliyotumia.

**Sikuweza kujaribu muamala halisi wa Pesapal** — mazingira haya
hayaruhusu kufikia `cybqa.pesapal.com`, na sina funguo. Hatua ya 4 kwenye
`PESAPAL.md` ndiyo jaribio la kweli, na inapaswa kufanywa kwa sandbox
kabla ya `PESAPAL_ENV=live`.
