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

---

## Bar ya mradi haikupanda; mradi uliojaa; fomu ndefu

Mambo matatu, lakini yalikuwa na mzizi mmoja: mchango haukuwahi
kuunganishwa na mradi wowote kwenye database.

### 1. Michango haikuhesabiwa

Mnyororo ulivunjika sehemu nne mfululizo:

1. `home.html` na `huduma.html` zilipeleka `?mradi=<KICHWA cha mradi>` —
   herufi, si namba.
2. `core/views.py::changia()` ilisoma `aina` pekee. `mradi` haikusomwa
   kamwe.
3. `PublicDonationForm` haikuwa na uwanja wa `project`.
4. Kwa hiyo `Contribution.project` ilikuwa `NULL` daima, na
   `Project.raised()` — inayochuja kwa `project=self` — ilirudisha sifuri
   milele.

Bar ingeweza kusimama pale pale hata michango ya milioni ingeingia.

Marekebisho: viungo sasa vinapeleka `?mradi={{ p.id }}`; `changia()`
inasoma namba hiyo na kuipeleka kwenye fomu; fomu ina uwanja uliofichwa
wa `project`; `save()` inauhifadhi.

`raised()` inahesabu michango ya `CONFIRMED` pekee. Ya `pending`
haihesabiwi kwa makusudi — mtu anaweza kujaza fomu asilipe, au kadi
ikakataliwa; bar ingepanda kisha ikashuka, na ripoti za mweka hazina
zingeonyesha fedha zisizopo.

### 2. Mradi uliotimia

`Project` imepata `remaining()`, `is_full()`, `accepts_donations()` na
`suggest_other()`. Mradi usio na lengo (`target_amount = 0`) HAUJAI
kamwe — ni wa uendeshaji wa kudumu, si kampeni yenye kikomo.

`suggest_other()` inapanga kwa iliyokaribia lengo kwanza: mradi wa 80%
humvutia mtu zaidi kuliko wa 5%, na pia unamaliza haraka.

Kwenye kadi: beji ya **IMETIMIA** na kitufe cha "Changia Mradi Mwingine".
Mtu akifika `/changia/?mradi=<uliojaa>`, anaambiwa lengo limetimia na
beji inabadilika yenyewe kwenda mradi mwingine unaohitaji msaada.

Ukaguzi upo pia kwenye `clean_project()` — si kwenye kiolezo pekee.
`mradi` inatoka kwenye URL, na mtu anaweza kuandika namba yoyote; bila
huo ukaguzi fedha zingeingia kwenye mradi uliokwisha kamilika. Nilijaribu
kutuma POST ya kughushi yenye `project=<uliojaa>`: ilikataliwa, idadi ya
michango haikuongezeka.

### 3. Fomu imepunguzwa kutoka hatua 5 kwenda 3

- **1 · Unachangia nini** — kusudi, mradi, kiasi, marudio
- **2 · Taarifa zako**
- **3 · Njia ya malipo**

Baada ya kuunganisha hatua, ukurasa ULIONGEZEKA urefu (2,515 → 2,680px)
kwa sababu beji ya mradi iliongeza nafasi. Nilibana hatua ya malipo:
`.gv__methods` kutoka gridi kwenda pills, `.paybadge` 400 → 250px.
Mwisho: **2,418px**, fomu 1,765 → 1,611px.

### Kilichojaribiwa

- POST `/changia/` yenye `project=5` → `MUWESTA-M-000011 | project = 5`;
  baada ya kuthibitisha, `raised` 0 → 250,000 na kadi ikaonyesha
  "TZS 250,000 kati ya TZS 60,000,000".
- Mradi #4 kujazwa hadi 85,000,000 → `is_full()` kweli, beji IMETIMIA,
  bar 100%, na `/changia/?mradi=4` ikapendekeza mradi mwingine.
- POST ya kughushi kwenye mradi uliojaa: ilikataliwa (12 → 12).
- Njia 14: zote 200. Hakuna maandishi ya maoni yanayovuja.
  Hakuna kufurika kwa mlalo kwenye 360px wala 390px.
- Maneno mapya 8 yametafsiriwa; `compilemessages` → 1,837.

### Somo nililojifunza (tena)

Niliandika maoni ya `{# ... #}` ya mistari mingi mara tatu, nayo
yakachapishwa kwenye ukurasa. Somo hili lilikuwa tayari limeandikwa
hapa kwenye awamu ya 14. Mistari mingi = `{% comment %}` DAIMA.

Pia: nilianzisha `runserver` mpya bila kuua ya zamani, nikadhani
marekebisho hayafanyi kazi. Ilikuwa proceso ya zamani yenye kiolezo cha
kabla ya marekebisho. `pkill` kwanza.

### Bado inasubiri uamuzi wako

- `core/finance_models.py` ni nakala inayofanana herufi kwa herufi na
  `finance/models.py`. Mtu akibadilisha moja tu, kutakuwa na tofauti
  isiyoonekana.
- Nenosiri la Supabase bado lipo wazi `config/settings.py:137`.
- `SOMA.md` sehemu ya 1 inasema uingie kama `admin` kwenye ukurasa wa
  umma; `core/views.py:688` inazuia superuser hapo kwa makusudi.
- OTP inapita ikiwa SMS haipatikani (fail-open).
- Matangazo ya mfano yote ni `draft` — upau wa taarifa hauonekani kwenye
  usakinishaji mpya.
- MediaItem 20 hazina faili.
- `db.sqlite3.backup` iliyopo ina historia ya uhamishaji iliyochanganyika
  (`finance.0006` kabla ya `members.0009`). Ukiirudisha, utapata
  `InconsistentMigrationHistory`. Database mpya inajengeka safi.

---

## Ukaguzi mkubwa: maudhui ya static, mantiki na bugs

Ulitaka mambo matatu: hakuna maudhui ya static yaliyofungwa kwenye
template bila uhusiano na backend; mantiki irekebishwe; bugs zote
zipatikane. Yafuatayo ndiyo yaliyopatikana na kufanywa.

### SEHEMU 1 — FEDHA

#### Mchangiaji wa dola alilipishwa mara 2,615

`to_tzs()` ilibadilisha $100 kuwa TZS 261,500 na kuihifadhi kwenye
`Contribution.amount` — sahihi. Lakini `Contribution.currency` ilibaki
"USD", na njia zote mbili za malipo zilituma **kiasi cha TZS pamoja na
alama ya fedha ya asili**:

```python
amount=gift.amount,                 # 261500 (TZS)
currency=gift.currency or "TZS",    # "USD"
```

Pesapal ilimwonyesha mtu **$261,500**. EUR ingekuwa mara 2,840, KES mara
20. Sasa ni `currency="TZS"` daima, kwa sababu `amount` tayari
imeshabadilishwa.

#### Malipo moja yaliweza kuhesabiwa mara mbili au tatu

Pesapal hupiga IPN wakati ule ule kivinjari kinapiga callback; Selcom
hupiga webhook wakati ukurasa wa kusubiri unauliza hali kila sekunde
chache. Ubadilishaji wa hali ulikuwa **soma-kisha-andika bila kufuli**:

```python
if state == "confirmed" and gift.status != PaymentStatus.CONFIRMED:
    gift.status = PaymentStatus.CONFIRMED
    gift.save(update_fields=["status"])
```

`select_for_update` haikuwepo popote kwenye njia ya malipo. Nyuzi mbili
zilisoma `pending` kwa wakati mmoja, zote zikaandika `confirmed`, na
signal ikaendeshwa mara mbili:

* `LedgerEntry` mbili kwa malipo moja — salio la mwanachama likaongezeka
  maradufu
* pointi mara mbili
* `renew_term()` mara mbili — miaka 6 ya uanachama kwa malipo ya miaka 3
* na kwa ombi jipya, `Application.activate()` mara mbili: **wanachama
  WAWILI**, namba mbili, kadi mbili na akaunti mbili kwa mtu mmoja
* risiti mbili za SMS, zote zikilipiwa na MUWESTA

Sasa kuna `Contribution.settle()` — njia moja inayoshika kufuli la safu
(`select_for_update`) kabla ya kubadilisha hali. Callback, IPN, webhook
na kipima-hali zote zinapitia hapo.

Ulinzi wa pili: kizuizi cha database kwenye `(gateway, gateway_ref)`.
`idempotency_key` ilikuwepo kwenye model tangu mwanzo lakini
**haikuandikwa kamwe**, kwa hiyo kizuizi chake hakikushika chochote.

#### Kidokezo kutoka nje kingeweza kurudisha nyuma uamuzi wa afisa

`/pesapal/ipn/` haina saini wala ukaguzi wa IP. Ukaguzi ulikuwa
`gift.status != CONFIRMED`, ambayo `cancelled` inaikidhi. Afisa
akighairi malipo ya udanganyifu, mtu yeyote angeweza kuyarudisha kwa
kuomba URL moja. Tawi la `failed` lilikuwa halina ukaguzi wa hali
kabisa — mchango uliokwisha ingia leja ungeweza kugeuzwa `failed`.

Sasa `GATEWAY_MUTABLE = (PENDING,)`: kidokezo kinaweza kubadilisha
mchango unaosubiri pekee. Uamuzi wa afisa ni wa mwisho.

#### Kughairi hakukurudisha chochote

Kughairi kulibadilisha `status` pekee. Leja na pointi zilibaki. Afisa
akighairi malipo ya TZS 500,000 (hundi iliyokataliwa), dashibodi ilisoma
TZS 0 huku leja ikisoma TZS 500,000 — na leja ndiyo hati ya mwisho.

`LedgerEntry.reverses` na `PointTransaction.reverse()` zilikuwepo tangu
mwanzo, hazikuwa zinaitwa. Sasa `reverse_posting()` inaziita. Leja
haifutwi; kosa linarekebishwa kwa ingizo la kinyume.

#### Selcom ilikuwa imekufa kabisa kwenye `/lipa/`

```python
phone = (gift.donor.phone if gift.donor else "") or ""
```

`/lipa/` **haiweki `donor` kabisa** — inaweka `donor_phone`. Kwa hiyo
kila malipo ya ada kwa Selcom yalisimama hapo, na mtu akaambiwa "mchango
wako umehifadhiwa" bila njia yoyote ya kulipa. Sasa kuna `contact_phone`
na `contact_email` zinazosoma mahali pote. `donor_email` imeongezwa —
Pesapal inahitaji njia MOJA ya mawasiliano, na `/lipa/` ilikuwa haitumi
yoyote.

#### Kikomo cha pointi kilikuwa kinaepukika

Ada ilitoa pointi 100 bila kupimwa, kwa `objects.create(kind=MONEY)` —
ikiruka `MONEY_CAP` kabisa. Mtu aliyelipa ada mara 40 alipata pointi
4,000 kwa TSh 400,000; mchangiaji wa kawaida alihitaji TSh 4,000,000
kufikia kikomo hicho, kisha akasimama. Sasa ada nayo inapitia kikomo.

Pia: `award()` na `award_money()` sasa zinakataa kutoa pointi mara mbili
kwa risiti ile ile.

#### Hesabu za fedha zilikuwa zinapoteza shilingi

`months_price` ilibadilisha `Decimal` kuwa `float` kisha ikatumia
`round()`, ambayo ni **banker's rounding**. Ada ya 5,000 kwa miezi 3
(punguzo 5%) ni 14,250; `round(142.5)` ilitoa 142, si 143 — bei ikawa
14,200. JavaScript ya ukurasa ule ule ilionyesha 14,300. **Bei
iliyoonyeshwa haikulingana na iliyolipishwa.**

`recurrence_total` ilikata desimali kabla ya kubadilisha fedha: $10.99 ×
miezi 3 × 0.95 = $31.3215 ikawa $31, kisha ikazidishwa kwa 2,615 — TZS
841 zikipotea kila muamala.

Vyote sasa ni `Decimal` na `ROUND_HALF_UP`, na vinalingana na JavaScript.

#### Viwango vya fedha vilikuwa vya kubuni

Maelezo ya `core/data/giving.py` yenyewe yalisema viwango "ni vya MFANO
tu na havisasishwi" — huku `to_tzs()` ikivitumia kwa michango HALISI.
Kila shilingi iliyoingia kutoka nje ya nchi ilipimwa kwa kiwango cha
kubuni. Sasa kuna jedwali `ExchangeRate` (`/mfumo/viwango-fedha/`).

**TAZAMA**: viwango vya kuanzia bado ni vya mfano. Vibadilishe kabla ya
kupokea michango ya fedha za nje.

### SEHEMU 2 — USALAMA

#### Daftari lote la michango lilisomeka

```python
if request.session.get("mwst_last_gift") != receipt and not request.user.is_authenticated:
    raise Http404
```

`and not request.user.is_authenticated` ilimaanisha **mtu YEYOTE
aliyeingia** — hata mhisani aliyejisajili mwenyewe dakika iliyopita —
aliweza kusoma risiti zote. Namba zinafuatana
(`MUWESTA-M-000001, -000002...`), kwa hiyo jina la mtoaji, kiasi, mfuko
na hali ya kila mchango vilisomeka kwa loop moja.

Pia `/pesapal/callback/?OrderMerchantReference=<risiti>` iliweka namba
hiyo kwenye session ya mgeni na kumpeleka kwenye risiti. Bila akaunti
yoyote.

Sasa: risiti inasomeka na aliyechangia kwenye kipindi hiki, mwenye
rekodi, au afisa. Callback inakubali `OrderTrackingId` pekee — UUID ya
Pesapal, isiyokisiwa.

#### Taarifa za waombaji wote zilivunwa kwa loop

`/lipa/?ombi=APP/MUWESTA/2026/0007` ilijaza jina, simu na barua pepe ya
mwombaji. Namba zinafuatana: `0001` hadi `9999`. Sasa kiungo lazima kiwe
na saini (`pay_token`), ambayo hutolewa kwenye SMS pekee.

> Hapa nilifanya kosa nilipokuwa narekebisha: nilitumia
> `signing.dumps()`, ambayo huingiza MUDA ndani ya saini — saini
> ilibadilika kila sekunde, na kiungo cha SMS kingekufa mara moja.
> Jaribio langu la kwanza lilipita kwa sababu lilitengeneza na kutumia
> saini ndani ya sekunde moja. Sasa ni `salted_hmac`, ambayo ni imara.

#### OTP ilikuwa imezimika kimya kimya

`sms.send_code()` inarudisha `False` **kila mara** NextSMS isipokuwa
imewekwa. Ukaguzi wa "SMS imeshindwa" ulimruhusu mtu aingie bila code —
ulikusudiwa kwa hitilafu ya muda, lakini usanidi usiokuwepo si hitilafu
ya muda. Kila afisa aliingia bila hatua ya pili, huku dashibodi ikisema
OTP imewashwa. Mwenye nenosiri lililoibiwa la afisa aliingia moja kwa
moja.

Sasa: mwanachama bado anaruhusiwa (kumfungia nje kwa kosa letu si
sahihi), lakini **afisa anakataliwa**, na msimamizi anaambiwa nini cha
kufanya.

Pia: sheria ya "maafisa: kila mara" ilikuwa inaangalia `user.is_staff` —
bendera inayowekwa na amri za mstari wa amri pekee. Afisa aliyeundwa
kupitia `/mfumo/watumiaji/` hakuipata, kwa hiyo alipitia njia ya kifaa
kinachoaminika cha siku 30. Maafisa wawili wenye jukumu moja walikuwa na
ulinzi tofauti kabisa. Sasa inaangalia JUKUMU.

#### Afisa wa wadau angeweza kutengeneza wanachama

`staff_required` inakubali kila jukumu lisilo la mwanachama. Kuthibitisha
malipo ya `ada` kunazalisha mwanachama, kadi na akaunti ya kuingia — kwa
hiyo afisa asiyehusika na fedha kabisa angeweza kutengeneza uanachama
bila senti kuingia. Sasa kuna `MONEY_ROLES`.

Vivyo hivyo `reset_login`: ilikuwa haijazuiwa kabisa. Afisa yeyote
angeweza kurejesha nenosiri la mwanachama yeyote, kusoma nenosiri la
muda kwenye ujumbe ule ule, na kuingia kama mtu huyo. Ilikuwa pia
inamfufua mwanachama aliyesimamishwa (`is_active = True`). Sasa ni
msimamizi pekee, na `is_active` haiguswi.

#### Ufinyu wa kanda haukuwepo kwenye vitendo

Orodha zilichuja kwa mkoa; vitendo havikuchuja. Mratibu wa kanda moja
angeweza kuidhinisha ombi la kanda nyingine, kuthibitisha malipo ya
mwanachama asiye wake, na kusoma risiti yoyote — kwa POST yenye `pk`.
Dashibodi ya taifa nayo ilikuwa wazi kabisa. Kupakua CSV ya wahisani
hakukuwa na ufinyu **kabisa**, tofauti na kila kitu kingine.

#### Mengineyo

* **Mwenyekiti wa kata alisoma malalamiko dhidi yake mwenyewe.** Orodha
  ya mazungumzo ilichuja kwa ngazi; ukurasa wa mazungumzo moja ulikagua
  eneo pekee. Kiongozi angeweza kusoma — na kujibu ndani ya —
  mazungumzo ambayo mwanachama alifungua na UONGOZI WA TAIFA.
* **Kuteka historia ya michango kwa jina.** Kujisajili kama mhisani
  kulihamisha michango YOTE yenye jina lile lile. Jina si siri. Sasa
  lazima simu au barua pepe ilingane.
* **Maombi mawili, wanachama wawili.** `AWAITING_PAYMENT` ilikuwa nje ya
  orodha ya hali zinazozuia ombi jipya. Pia hakukuwa na kizuizi cha
  database kwenye kitambulisho, simu wala barua pepe — sasa kipo.
* **Kiasi cha msaada kilichukuliwa kutoka POST bila ukaguzi.** `abc`
  ilivunja ukurasa; `-50000` iliingia; kiasi kikubwa kuliko kilichoombwa
  kiliingia.
* **Nenosiri la Supabase lilikuwa wazi** kwenye `settings.py`, na
  maelezo yake yenyewe yakikiri lipo kwenye historia ya git. Limeondolewa;
  production sasa inalazimika kuwa na `DATABASE_URL`.
  **Nywila bado ipo kwenye historia ya git — ibadilishe Supabase.**
* **`SECRET_KEY` ya mfano ilipita ulinzi.** Ukaguzi ulitafuta kiambishi
  `django-insecure-` pekee; chaguo-msingi halikuwa nalo. Deploy
  iliyosahau funguo ingeanza production ikiwa na funguo iliyochapishwa
  kwenye repo — session ya msimamizi mkuu ingeweza kughushiwa, na
  kidakuzi cha kifaa kinachoaminika (kuruka OTP) pia.
* **`*.onrender.com` ilikuwa asili inayoaminika ya CSRF.** Render ni
  mwenyeji wa pamoja — programu yoyote ya bure pale ingeweza kutuma POST
  kwenye `/maombi/<pk>/approve/`.
* **`ALLOWED_HOSTS = *`** iliruhusu Host-header injection: kiungo cha
  kubadilisha nenosiri hujengwa kutoka `request.get_host()`.
* **Faili zilizopakiwa zilikuwa 404 kwenye production.** WhiteNoise
  inahudumia `STATIC_ROOT` pekee. Afisa alipakia picha, akaambiwa
  "imefanikiwa", picha haikuonekana popote.
* **Fomula kwenye CSV.** Jina lililoandikwa `=HYPERLINK(...)` lilikuwa
  linatekelezwa kwenye Excel ya afisa.
* **`_alert_login` MBILI.** Ya pili ilififisha ya kwanza, kwa hiyo arifa
  ya barua pepe haikuwahi kutumwa — huku ufafanuzi wa ya kwanza ukisema
  inatumwa.
* **Mtumiaji aliyeundwa `/mfumo/watumiaji/` hakuweza kuingia kamwe** —
  fomu haina uwanja wa nenosiri, kwa hiyo `password=""` ilihifadhiwa.
  Hakuna kosa lililoonekana popote.

#### Bug iliyokuwa inavunja production pekee

`Case.save()` iliita `Sequence.next` — inayotumia `select_for_update` —
**bila `transaction.atomic`**. SQLite inainyamazia kimya; Postgres
inatoa `TransactionManagementError`. Kila mwanachama aliyejaribu kufungua
tatizo alipata 500. Mfumo mzima wa malalamiko ulikuwa umekufa kwenye
production na ulifanya kazi vizuri kwenye kompyuta ya maendeleo. Kila
mahali pengine panapoita `Sequence.next` tayari palikuwa sahihi — hapa
pekee ndipo palipokuwa pamesahaulika.

### SEHEMU 3 — MAUDHUI YA STATIC

#### Mistari 2,049 ya namba za kubuni imeondolewa

`core/mockdata.py`, `core/data/dashboards.py`, `core/data/outreach.py`,
`core/data/common.py::REGIONS`, `core_data/`, `core/finance_models.py`,
`templates/base/wadau.html`.

Ndani yake: wanachama "142,718", "TZS 136,450,000", mgawanyo wa
wanachama kwa mikoa 26, majina ya wafadhili wasiokuwepo ("Muslim Aid
International — TZS 328,500,000"), risiti za kubuni, na namba ya
kitambulisho `19901234567890` pamoja na barua pepe ya mtu.

Hazikuwa zikitumika na ukurasa wowote, lakini zilikuwa **mtego**: mtu
akitafuta namba kwenye msimbo angeziamini, na `ctx = dashboards.national()`
moja ingezirudisha kwenye tovuti. Maelezo ya faili yenyewe yalikiri:
"Namba zote zimechukuliwa moja kwa moja kutoka kwenye picha za muundo."

#### Namba za kubuni zilizokuwa zikionekana LEO

`seed.py` iliandika takwimu za picha za muundo kwenye database:
"wanafunzi 1,240 wamefadhiliwa", "kambi 18 za afya mwaka huu", "visima 34
vimechimbwa". Zilionekana `/huduma/` kama **beji ya kijani ya
uthibitisho** — mgeni aliziamini. Sasa ni tupu, na beji haionekani
zikiwa hazipo.

Vivyo hivyo viongozi wanne wa kubuni. Orodha rasmi ipo kwenye migration
`content/0004_muwesta_leaders.py`, na `seed` ilikuwa ikiiongezea majina
ya kubuni baada ya migration kuiweka. Sasa migration ndiyo chanzo pekee.

#### Beji za menyu

Msimamizi aliona "128" karibu na *Maombi ya Uanachama*, afisa aliona
"18" — **milele**. Zilikuwa maandishi ndani ya `navs.py`. Mtu
aliyefungua ukurasa akakuta maombi matatu alijua namba hizo ni za
urembo, na kuanzia hapo hakuamini namba nyingine yoyote kwenye mfumo.
Sasa ni hesabu halisi, ndani ya eneo lake, na `None` zikiwa hakuna.

#### Ramani ilikuwa inadanganya

Legend ilisema "Zaidi ya 10,000", "5,000 - 10,000"... lakini `tz_map`
haipaki rangi kwa idadi kamili — inapaka kwa **uwiano na mkoa mkubwa**.
Mkoa wa wanachama 25, ukiwa ndio mkubwa, ulipakwa rangi ambayo legend
iliiita "zaidi ya 10,000". Sasa legend inahesabiwa kutoka kwenye data
halisi.

#### Vihesabio vilivyopewa majina yasiyo sahihi

| Kilichosemwa | Kilichohesabiwa | Sasa |
|---|---|---|
| Mikoa Tunayofanya Kazi | mikoa YOTE ya Tanzania (26) | mikoa yenye wanachama (15) |
| Wilaya Tulizofikia | wilaya ZOTE (184) | wilaya zenye wanachama (20) |
| Miradi Inayoendelea | miradi YOTE | inayoendelea pekee |
| Matukio Mwaka Huu | matukio YOTE tangu mwanzo | ya mwaka huu |
| Wanufaika kwa Mwezi | usajili WOTE tangu mwanzo | wa mwezi huu |

#### Maudhui yaliyokuwa yamefungwa kwenye template

* **Jina, kauli mbiu na maadili ya shirika** yalikuwa yameandikwa kwenye
  `base.html`, `sidebar.html`, `footer.html`, `idcard.html`,
  `dashboard.html`, `login.html` na `verify.html` — kila mahali kwa
  maneno yake. `SiteSetting` ilikuwepo na ilihaririwa; hakuna
  kilichobadilika. Sasa vyote vinasoma pale.
* **Huduma tano za footer** zilikuwa zimeandikwa, zote zikielekeza
  mahali pamoja. Sasa zinatoka jedwali la Huduma.
* **Kadi tatu za huduma kwenye `/kuhusu/`** zilikuwa zimeandikwa ndani
  ya HTML wakati jedwali lipo.
* **Aya za Qur'an** zilikuwa ndani ya HTML na ndani ya
  `core/data/verses.py`, huku jedwali la `Verse` likiwepo na
  likihaririwa `/mfumo/aya/` — lakini likisomwa na dashibodi pekee.
  Uwanja wa `slot` umeongezwa.
* **"Maeneo Sita ya Huduma"** — kichwa kilisema "Sita" wakati gridi
  inazunguka jedwali lenye idadi yoyote.
* **"pointi 1 kwa kila TSh 1,000"** ilikuwa imeandikwa kwenye
  `pointi.html`, ikirudia `SHILLINGS_PER_POINT`. Bodi ikibadilisha
  kiwango, sentensi aliyoisoma mwanachama ingebaki ya zamani — kwenye
  lugha zote mbili.
* **"miaka 18"** ilikuwa imeandikwa mara mbili: kwenye ukaguzi na kwenye
  HTML. Sasa ni `MIN_JOIN_AGE`.
* **`www.muslimwelfare.or.tz`** ilikuwa imeandikwa kwenye
  `vifurushi.html`, karibu kabisa na simu na barua pepe zinazotoka
  `SiteSetting`.
* **Mifano ya namba za kumbukumbu** (`APP/MUWESTA/2026/0001`) ilikuwa na
  "MUWESTA" na "2026" ndani yake.
* **Mwaka `2026`** ulikuwa chaguo-msingi la hakimiliki kwenye footer.
* **Beji ya bahasha** ilikuwa `None` daima — haikuweza kuonekana kamwe,
  hata ujumbe ukiwepo. Mtumiaji aliisoma kama "huna ujumbe", si kama
  "hakijakamilika". Beji ya arifa iliyo pembeni yake ilikuwa halisi.

#### Ukurasa wa mawasiliano

Namba TANO zilichapishwa hadharani; **NNE zilikuwa `123 456`** — namba
za mfano kwenye ukurasa wa mawasiliano wa shirika. Barua pepe zilikuwa
`@mwst.or.tz` wakati sehemu nyingine za mfumo zinatumia
`@muslimwelfare.or.tz`. Hakuna aliyeweza kuzirekebisha bila deploy.

Sasa: jedwali la `ContactChannel` (`/mfumo/mawasiliano/`). Bila rekodi,
ukurasa unarudi kwenye simu na barua pepe kuu za mipangilio — si kwenye
namba za mfano.

#### Nyaraka za kisheria

Zilitaja **`https://mwiso.onrender.com`** kama tovuti rasmi ya shirika,
na **`S.L.P. 0000, Dodoma`** kama anwani ya posta. Tarehe ya kuanza
kutumika ilikuwa imeandikwa, kwa hiyo kuisasisha kulihitaji deploy.

Sasa zinatoka `SiteSetting`. Uwanja usiojazwa **haujachapishwi kabisa** —
ni bora kukosa mstari kuliko kuchapisha anwani ya majaribio kwenye hati
inayofunga kisheria.

**Weka tovuti halisi** `/mfumo/mipangilio/` — kwa sasa mstari wa
"Tovuti" hauonekani kwenye nyaraka.

#### Habari hazikuweza kusomwa

`News.body` — habari yenyewe — ilihifadhiwa na kuhaririwa, lakini
haikuwa na ukurasa. Kila "Soma Zaidi" kilirudi `/habari/`, ukurasa ule
ule uliokuwa na kiungo hicho. Ukurasa `/habari/<id>/` umeongezwa.

Vivyo hivyo **Masharti ya Huduma**: yalitumia kiolezo kimoja na sera
nyingine lakini hayakuwa na chip yake, kwa hiyo yalionekana kama
ukurasa uliopotea.

### Kilichojaribiwa

* Kurasa **240** kwa majukumu sita (admin, usajili, malipo, michango,
  wadau, mwanachama): zote 200. Vipengele **41** vya `/mfumo/`: vyote
  vinafunguka na kuruhusu kuongeza.
* `settle()` ikiitwa mara tatu mfululizo: leja **1**, pointi **1**.
* Mchango uliogharikiwa + kidokezo `confirmed` → hakikubadilika.
* Kughairi → salio 100,000 → 50,000; wito wa pili haukubadilisha kitu.
* Malipo 50 ya ada → pointi zilisimama kwenye kikomo (awali 5,000).
* Nakala ya `gateway_ref` → `IntegrityError`.
* Risiti ya mtu mwingine: **404** kwa mgeni na kwa mwanachama.
* `/pesapal/callback/?OrderMerchantReference=<risiti>`: **404**.
* `/lipa/?ombi=<ref>` bila saini: hakuna taarifa binafsi; na saini:
  inajaza.
* Kuthibitisha malipo: `wadau` imezuiwa, `usajili` imezuiwa, `malipo`
  imeruhusiwa.
* `reset_login`: `registration` imezuiwa, `admin` imeruhusiwa.
* Beji ya menyu: **14**, sawa na maombi halisi yanayosubiri.
* Kufungua tatizo: `TAT/2026/0001` — na `Sequence.next` sasa ipo ndani
  ya muamala.
* Barua pepe ya kubadilisha nenosiri: jina la shirika linatoka database.
* Hakuna kufurika kwa mlalo kwenye 360px wala 390px kwenye kurasa 13.
* Hakuna maandishi ya maoni yanayovuja.
* Maneno mapya 43 yametafsiriwa; `compilemessages` → **1,879**.

### Mambo ambayo hayajafanywa, na sababu

* **Maudhui marefu ya `core/data/`** — sera ya faragha, masharti, aina
  za uanachama, faida 16, wajibu 8 — bado yapo kwenye Python.
  Yanapitia kwenye view kwenda kwenye template (si "static kwenye
  template"), lakini hayahaririki bila deploy. Kuyahamisha ni kazi ya
  awamu yake yenyewe: yanahitaji model yenye vipengele na mpangilio, si
  uwanja mmoja wa maandishi.
* **Slaidi za aya za ukurasa wa mbele** zina poster za picha
  zinazorejewa kwa jina la faili la static. Kuzihamisha kunahitaji
  kupakia picha, si uwanja wa maandishi tu.
* **`SOMA.md` sehemu ya 1** bado inasema uingie kama `admin` kwenye
  ukurasa wa umma. `core/views.py` inazuia superuser hapo **kwa
  makusudi** — tumia akaunti ya jukumu (`usajili`, `malipo`...) au
  Django admin. Sehemu hiyo inahitaji kusahihishwa.
* **Kikomo cha majaribio ya kuingia** kipo kwenye `LocMemCache`, ambayo
  ni ya proceso moja. Kwa gunicorn yenye watumishi N, kikomo halisi ni
  `8 × N`, na kinafutika kila deploy. Kinahitaji Redis.

---

## Safari ya mwanachama, na ngazi za uongozi

Ombi lilikuwa: kufuatilia hatua zote kuanzia mtu anapojisajili, kupitia
malipo, hadi anapokabidhiwa akaunti na kitambulisho — na kukagua ngazi
zote za uongozi ili kila kiongozi afanye jukumu lake.

Nilifuatilia safari kwa kuiendesha, si kwa kuisoma. Kila hatua ilipimwa
kwa script inayopiga fomu halisi, signal halisi na URL halisi.

### SEHEMU 1 — SAFARI ILIKWAMA HATUA YA MWISHO

**Mwanachama aliyelipa hakuweza kuingia. Hakuna mtu aliyeweza.**

Hii ni bug moja, na ilizima hatua ya mwisho ya safari nzima kwa **kila
mwanachama aliyejiunga kwa njia ya mtandao**.

Mtiririko ulivyo: `Contribution` inathibitishwa → signal ya
`post_save` → `apply_membership()` → `Application.activate()`.
Ndani ya `activate()`:

```python
member.temp_password = member.create_login()
```

`create_login()` hutengeneza nenosiri la herufi kumi na kulirudisha.
Linawekwa kama **sifa ya kumbukumbu** kwenye kitu cha Python. Si uwanja
wa database.

Tatizo ni MAHALI `activate()` inapoitwa: ndani ya callback ya Pesapal,
au IPN, au webhook ya Selcom. Hakuna afisa mbele ya skrini. Request ile
inaisha, kitu cha Python kinafutwa, na nenosiri linakwenda nalo.

Ukurasa wa asante ulijaribu kulionyesha:

```python
"temp_password": getattr(member, "temp_password", None),
```

Lakini `changia_asante` inasoma `Contribution` upya kutoka database, kwa
hiyo `member` ni kitu kipya kabisa. `getattr` ilirudisha `None` **kila
mara, kwa kila mwanachama, bila kukosa**. Jaribio langu lilithibitisha:

```
[ BAYA ] member.temp_password baada ya kupakia upya DB: None
[ BAYA ] Ukurasa wa asante unaonyesha nenosiri la muda: False
   Kujaribu kuingia:
     nenosiri='mwst2026'              -> imekataliwa
     nenosiri='MUWESTA/B/000002/2026' -> imekataliwa
```

Na SMS? `send_membership_ready` ilisema kwa makusudi:

> "Wasiliana na afisa upate taarifa za kuingia."

Afisa hakuwa na taarifa hizo. Hazikuwa zimehifadhiwa mahali popote.
Ujumbe wa `/jiunge/` ulikuwa ukiongeza ahadi ya tatu:

> "utapigiwa simu na kupewa namba yako ya uanachama pamoja na **nenosiri
> la kuingia kwenye mfumo**"

Na Django admin ilikuwa na ya nne:

> "Nenosiri la muda linapatikana **kwenye ukurasa wa ombi**."

Halikuwa pale. Sehemu nne za mfumo zilikuwa zikielekeza mtu kwa nenosiri
ambalo hakuna sehemu ya tano iliyokuwa nalo. Njia pekee ya kweli ilikuwa
msimamizi kufungua ukurasa wa mwanachama na kubofya "Rejesha taarifa za
kuingia" — na hakuna mahali palipokuwa kikimwambia afanye hivyo. Afisa wa
usajili, ambaye ndiye anayeshughulika na mwanachama mpya, hana ruhusa
hiyo hata kidogo.

**Nilichofanya.** Sikuweka nenosiri kwenye SMS — uamuzi wa kutolituma
uko kwenye msimbo kwa sababu nzuri (SMS haifutiki, simu hukopeshwa).
Badala yake nenosiri linawekwa na mwanachama mwenyewe:

* `Member.setup_token` — saini ya HMAC ya `pk` pamoja na **alama ya
  nenosiri la sasa**. Nenosiri likiwekwa, alama inabadilika, na kiungo
  kinakufa chenyewe. Hakuna tarehe ya mwisho ya kuhifadhi, hakuna rekodi
  ya ziada, hakuna kiungo cha kutumika mara mbili.
* `/anza/` (`weka_nenosiri`) — ukurasa wa kuweka nenosiri, unatumia
  `SetPasswordForm` ya Django, kwa hiyo kanuni za nenosiri ni zile zile
  za mfumo wote.
* SMS ya "uanachama umeanza" sasa inakuwa na kiungo hicho.
* Ukurasa wa asante unamwonyesha kitufe cha kuweka nenosiri — kwa
  **mlipaji pekee** (`session["mwst_last_gift"]`), si kwa afisa
  anayeruhusiwa kuona risiti. Kiungo kinaweka nenosiri; si cha kupita
  kwa mtu wa tatu.
* Ujumbe wote wanne wa uongo umesahihishwa kusema kinachotokea kweli.

Sikutumia `signing.dumps` — ndiyo hitilafu niliyoifanya na kuirekebisha
raundi iliyopita: huingiza muda ndani ya saini, saini inabadilika kila
sekunde, na kiungo cha SMS kinakufa mara moja. `salted_hmac` haina muda.

Baada ya marekebisho, safari yote ni safi:

```
[  OK  ] 1. Ombi: APP/MUWESTA/2026/0022 hali=pending
[  OK  ] 2. Baada ya kuhakikiwa: hali=awaiting_payment
[  OK  ] 4. Malipo yamethibitishwa -> mwanachama #22
[  OK  ] 5. Namba ya uanachama: MUWESTA/B/000003/2026
[  OK  ]    Kadi: MUWESTA/B/00031/2026 (inaisha 2029-09-25)
[  OK  ]    Leja imeingizwa: #12
[  OK  ]    Kuingia kwa namba ya uanachama: imefanikiwa
[  OK  ]    Kiungo CHA ZAMANI kimekufa -> 302
[  OK  ] 7. /mwanachama/ -> 200
```

**Kusitisha mwanachama hakukusitisha kitu.**

Afisa akibofya "Sitisha", `Member.status` ilikuwa `suspended` —
na hapo ndipo ilikoma. `user.is_active` haikuguswa, na hakuna mahali
pengine hali hiyo ilikuwa ikiangaliwa. Jaribio:

```
[ BAYA ] Aliyesitishwa anaweza kuthibitishwa: True (user.is_active=True)
[ BAYA ] login()=True, /mwanachama/ -> 200
```

Aliyesitishwa aliendelea kuingia, kuona kadi yake, kuomba msaada na
kutuma malalamiko. Uamuzi wa afisa ulikuwa maandishi kwenye jedwali.

Sasa kusitisha kunaweka `is_active=False` pia. `ModelBackend.get_user`
inarudisha `None` kwa akaunti isiyo hai, kwa hiyo **hata kipindi
kilichokuwa kimefunguliwa kinakoma kwenye ombi linalofuata** — bila
kuhitaji ukaguzi kwenye kila mmoja wa view 14 za mwanachama.
Kuhuisha kunarudisha. Muda kuisha (`expired`) HAKUZUII — mtu anahitaji
kuingia ndio aweze kuhuisha.

### SEHEMU 2 — NGAZI ZA UONGOZI

**Ngazi tatu kati ya tano hazikuwa zinabana chochote.**

`geo/scope.py` inajua ngazi zote tano na docstring yake inasema wazi
kwamba mantiki hii haipaswi kuandikwa mahali pengine. Lakini
`core/views.py` ilikuwa na nakala yake ya pili:

```python
def scope_regions(user):
    zone = user_zone(user)
    return None if zone is None else list(zone.regions...)
```

`None` = mikoa yote. `user_zone` inajua **kanda pekee**. Kwa hiyo
kiongozi wa mkoa, wa wilaya na wa kata wote walipata "mikoa yote":

```
mratibu_kanda   views.scope_regions=4 mkoa       geo.scope_members=2/21
mratibu_mkoa    views.scope_regions=MIKOA YOTE   geo.scope_members=1/21
mratibu_wilaya  views.scope_regions=MIKOA YOTE   geo.scope_members=0/21
mratibu_kata    views.scope_regions=MIKOA YOTE   geo.scope_members=0/21
```

Jukumu lenyewe linaitwa **"Mratibu wa Mkoa"**. Paneli mbili za mfumo
mmoja zilikuwa na majibu mawili tofauti kwa swali moja: `/uongozi/`
ilibana kwa usahihi, `/mfumo/` haikubana kabisa. Mwenyekiti wa kata
mmoja aliona orodha ya wanachama wote wa nchi na namba zao za simu,
aliweza kuwapakua CSV, na `_in_scope` ilimruhusu kuthibitisha malipo ya
mtu wa mkoa wowote.

`scope_regions` sasa inatoka `geo.scope`, ngazi zote tano. `_in_scope`
inatumia `can_see_member` — si mkoa, kwa sababu kwa mwenyekiti wa kata
mkoa ni eneo kubwa mno. Na orodha ya wanachama inapita `scope_members`,
kwa hiyo mwenyekiti wa kata anaona kata yake, si mkoa wake. Asiye na
wadhifa wala jukumu la makao makuu anaona **sifuri**, si nchi nzima —
upande salama wa kukosea.

**`?kanda=` ilikuwa wazi kwa yeyote.** Mratibu wa Kanda ya Mashariki
aliandika `?kanda=kaskazini` na akapata dashibodi nzima ya kanda
nyingine. Na mratibu asiye na kanda alionyeshwa `Zone.objects.first()` —
kanda ya kwanza kwenye orodha, si yake, ila ilifunguka kama yake. Sasa
`?kanda=` ni ya msimamizi pekee.

**Nyadhifa za uongozi hazikuwa na ukurasa wowote.**

`geo.Leadership` ndiyo inayoamua kila kitu: nani anaona wanachama gani,
nani anapokea tatizo gani, nani anathibitisha ada ya nani. "Viongozi"
kwenye menyu ilikuwa ikihariri `content.Leader` — orodha ya picha ya
ukurasa wa "Kuhusu Sisi", isiyotoa ruhusa yoyote. Msimamizi hakuwa na
njia ya kumteua mwenyekiti wa kata ndani ya mfumo; ilihitaji Django
admin, ambayo mfumo huu hautumii. Ngazi zote tano zilikuwa kwenye
msimbo, hazikuwa na mlango. Nimeongeza `/mfumo/uongozi/`; `clean()` ya
model inakataa ngazi bila eneo, na nikaijaribu.

**Kughairi malipo: mlango mmoja, matokeo mawili.** Afisa akighairi
kwenye `/malipo/`, leja inarekebishwa kwa ingizo la kinyume. Kiongozi
akighairi malipo yale yale kwenye `/uongozi/ada/`, `status` ilibadilika
na leja ikabaki na pesa isiyokuwapo. Sasa njia zote mbili zinapitia
`reverse_posting`, na kughairi mara ya pili hakuguse tena.

### SEHEMU 3 — KILA AFISA NA KAZI YAKE

`staff_required` inakubali kila jukumu lisilo la mwanachama. Nilipima
majukumu 8 dhidi ya kurasa 16 na matokeo yalikuwa jedwali la "OK" tupu:
**kila afisa alifikia kila ukurasa.**

Vitendo, si kuona tu:

* Afisa wa michango, wa wadau na wa ustawi wote wangeweza **kuidhinisha
  ombi la uanachama** — hatua inayoruhusu mtu kulipa na kuwa mwanachama.
* Yeyote angeweza **kusitisha au kufufua** mwanachama, na **kumtolea
  kadi mpya**.
* Yeyote angeweza **kupakua CSV** ya wanachama wote (majina, simu, namba
  za vitambulisho, anwani), ya wahisani, na ya michango. CSV ni nakala
  inayotoka nje ya mfumo — hakuna AuditLog baada ya kuhifadhiwa kwenye
  simu ya mtu.
* Yeyote angeweza **kutuma SMS kwa wanachama WOTE**.

Sasa: usajili kwa usajili, fedha kwa fedha, wadau kwa wadau, ustawi kwa
ustawi. Kutuma ujumbe kwa wote na kusitisha uanachama ni vya msimamizi
na usimamizi. Majina ya makundi (`REG_ROLES`, `MONEY_ROLES`,
`OUTREACH_ROLES`, `WELFARE_ROLES`) yanalingana na yale ya
`core/registry.py` kwa makusudi — jukumu moja lisiwe na maana mbili
kwenye sehemu mbili za mfumo mmoja.

Afisa wa ustawi alikuwa akianzia `/taifa/` — dashibodi ya mfumo mzima,
yenye takwimu za fedha zisizomhusu. Sasa anaanzia `/ustawi/`.

**Menyu iliyobaki ikiahidi.** Kubana kurasa kunazalisha tatizo la pili:
menyu na vitufe vinabaki vikionyesha viungo ambavyo mtu atakataliwa
akibofya. `_filter_nav` ilikuwa ikichuja `/mfumo/` pekee.

Sasa `role_required` inaandika orodha ya majukumu kwenye view yenyewe
(`wrapper.mwst_roles`), na menyu inaisoma pale — **orodha moja, si
nakala ya pili inayoweza kutofautiana** siku mtu atakapobadilisha
kizuizi kimoja. Gridi ya "Vitendo vya Haraka" inapita ukaguzi ule ule:
afisa wa ustawi alikuwa akiona "Rekodi Malipo" na "Tuma Ujumbe kwa
Wote" kama vitufe vikubwa vya rangi — hatua za kwanza anazoziona
akiingia — na kila kimoja kilimwambia hana ruhusa.

Kwenye gridi hiyo nilipata pia:

* `/mfumo/programs/assistancerequest/` — muundo wa Django admin
  (`app/model`), si wa registry inayotumia slug. Kitufe **"Maombi ya
  Msaada" kwenye dashibodi kuu kilikuwa kikitoa 404 kwa kila mtumiaji.**
* "Tuma SMS kwa Wote" na "Tuma Email kwa Wote" — vitufe viwili, mahali
  pamoja (`/ujumbe/` yenyewe inauliza njia).
* "Ongeza Habari" ikielekeza `/media/`, yaani picha.
* `<path ... href="/taifa/">` kwenye ramani — `href` kwenye `<path>`
  haifanyi kitu kwenye SVG (kiungo kinahitaji `<a>`), kwa hiyo ilikuwa
  markup iliyokufa ikielekeza kila mkoa kwenye dashibodi ya taifa.
* Kichwa "Quick Actions" kilikuwa hakijatafsiriwa kwenye mfumo wa
  Kiswahili.

### Kilichojaribiwa

Database mpya kabisa (`rm db.sqlite3 && migrate && seed`), kisha:

* **Safari kamili** — ombi → kuhakikiwa → fomu ya malipo → `settle()` →
  mwanachama, namba, akaunti ya leja, kadi, kipindi cha miaka 3, akaunti
  ya kuingia → kuweka nenosiri → kuingia → `/mwanachama/`,
  `/mwanachama/kadi/`, na kuhakiki kadi hadharani. **Vipimo 25, vyote
  OK.** Kiungo cha zamani cha kuweka nenosiri kinakufa.
* **Ngazi tano** — Taifa anaona 22/22, Kanda 2, Mkoa 1, Wilaya 0, Kata
  0. Mazungumzo ya ngazi ya mkoa yanaonekana kwa mwenyekiti wa mkoa
  **pekee**: taifa 404, kanda 404, wilaya 404, kata 404. Wadhifa
  uliomalizika muda unamtoa mara moja (`/uongozi/` → 302).
* **Majukumu 8 × kurasa 16**, pamoja na CSV kwa kila aina.
* **Kutembea kurasa 71 kwa kila jukumu** — kurasa bovu **0**, na hakuna
  kitufe au kiungo kinachoishia "Huna ruhusa" kwa majukumu yote manane.
* **Fedha** — kughairi kwa afisa na kwa kiongozi kunatoa matokeo yale
  yale (50,000 na 30,000 zimerudishwa), kughairi mara ya pili
  hakubadilishi salio, na kiongozi wa eneo moja hagusi malipo ya
  mwingine (404 upande wa uongozi, 302 upande wa watumishi).

### Yaliyobaki

* **Tafsiri ya Kiingereza ya sehemu ya uongozi haipo.**
  `makemessages` inatoa msgid 276 zisizokuwa kwenye `.po` — nyingi ni za
  `leader_views.py`, `leadership.py` na kiolezo za `/uongozi/`. Lakini
  `.po` iliyopo ina msgid 1,878 ambazo `makemessages` **haizioni**
  (inatoa 1,345 tu), kwa hiyo kuiandika upya kungeharibu tafsiri
  zilizopo. Nimeongeza zangu 16 kwa mkono na kuacha zile 276; kuzimaliza
  ni kazi ya awamu yake, inayoanza kwa kutafuta kwa nini
  `makemessages` inakosa nusu ya faili.
* **`Member.temp_password`** bado inawekwa na `activate()`. Haina madhara
  (hakuna anayeisoma sasa), lakini ni sifa inayoahidi kitu
  isichotoa — inafaa kuondolewa kabisa.
* **`content.Leader` na `geo.Leadership`** zote zinaitwa "Viongozi"
  kwenye paneli. Nimeitofautisha kwa lebo ("Nyadhifa za Uongozi"),
  lakini majina mawili yanayokaribiana kwa vitu viwili tofauti kabisa
  yatachanganya mtu tena.

---

## Tafsiri ya Kiingereza imekamilika

Raundi iliyopita niliacha hii ikiwa haijakamilika, na nikaisema:
sehemu yote ya uongozi haikuwa na tafsiri, na `makemessages` ilikuwa
ikitoa msgid 1,345 wakati `.po` ilikuwa na 1,878 — kuiandika upya
kungeharibu tafsiri zilizopo. Kwanza nilitafuta kwa nini.

### Kwa nini `makemessages` inakosa nusu ya faili

Mfumo huu hutafsiri herufi za DATABASE na za dict za Python, si za
kiolezo pekee. Filter `tr` (`core/templatetags/mwst_tags.py`) huita
`gettext()` kwa thamani inayotoka kwenye muktadha:

```python
@register.filter(name="tr")
def tr(value):
    return gettext(str(value))
```

Inatumika mara 224 kwenye kiolezo: `{{ k.label|tr }}`, `{{ a.label|tr }}`,
`{{ r.name|tr }}`. Herufi zenyewe zipo kwenye `core/data/navs.py` na
`core/queries.py` kama thamani za kawaida — HAZIJAZUNGUSHWA kwenye
`_()`, na `xgettext` haiwezi kuzitambua. Kwa hiyo `.po` ilikuwa na
mamia ya entries ambazo `makemessages` haizioni: si taka, ni ndizo
zinazoendesha menyu na KPI zote.

Kwa hiyo sikuiandika upya. Nilitengeneza nakala ya mradi kwenye
`/tmp`, nikaendesha `makemessages` HUKO, nikalinganisha, na
nikaongeza tu zinazokosekana kwenye `.po` halisi. Tafsiri 1,895
zilizopo hazikuguswa hata moja.

Sikutumia `msgcat` kuunganisha, ingawa ndiyo njia ya kawaida: ilikuwa
inaweka **entries 180 kama `fuzzy`** (msgid ile ile na thamani mbili —
moja tupu kutoka kwenye uchimbaji mpya). `msgfmt` huruka fuzzy kimya
kimya, kwa hiyo tafsiri 180 zilizokuwa zinafanya kazi zingeacha
kufanya kazi bila kosa lolote kuonekana. Pia `msgmerge` ingeweka
zilizoandikwa kwa mkono kama `#~ obsolete`, yaani kuzitoa kabisa.

### Herufi tatu zilizokuwa haziwezi kutafsiriwa kabisa

Wakati wa kulinganisha nilikutana na entries ambazo msgid zao
hazingeweza kulingana na ombi halisi — yaani zilikuwa hazina njia ya
kutafsiriwa, hata mtu akiandika tafsiri.

**1. `—` badala ya mstari mrefu** (`core/views.py`):

```python
"limehifadhiwa — afisa atawasiliana nawe."
```

Python inaibadilisha kuwa herufi moja (—) wakati wa kuendesha, lakini
`xgettext` huihifadhi kama herufi sita za escape. msgid kwenye `.po`
ilikuwa `...limehifadhiwa — afisa...` huku ombi halisi likiwa
`...limehifadhiwa — afisa...`. Hazikulingana kamwe. Nimeweka herufi
halisi.

**2 na 3. `{% trans %}` yenye `\"` ndani** (`templates/member/viongozi.html`
na kiolezo changu kipya):

```django
{% trans "...ni bora kutumia \"Toa Taarifa kwa Kiongozi\" badala ya..." %}
```

Django inaisoma vizuri wakati wa kuendesha, lakini `xgettext` huikata
msgid kwenye backslash:

```
msgid "Ukiwa na tatizo linalohitaji ufuatiliaji, ni bora kutumia \\"
```

Kwa hiyo `makemessages` huzalisha entry iliyokatika kila inapoendeshwa.
Nimeziandika kwa mkono kwa `\"` kwenye `.po` — ndipo zinapolingana na
ombi halisi — na kuziacha kwenye kiolezo kama zilivyo, kwa sababu
maandishi yanayoonekana ni sahihi. Ni sehemu mbili pekee kwenye mradi
wote, na zinahitaji kubaki za mkono.

### Herufi 21 za dict ambazo zilikuwa zimesahaulika

Ukaguzi wa AST wa `core/data/navs.py` na `core/queries.py` ulionyesha
lebo 21 zinazopita `|tr` bila entry yoyote — "Dashibodi ya Uongozi",
"Wanachama Wote", "Wilaya Zinazohusika", "Kadi Zinazosubiri",
"Uanachama Wangu" na nyingine. Menyu yote ya uongozi ilikuwa Kiswahili
kwenye tovuti ya Kiingereza kwa sababu hii.

`core/data/membership.py`, `about.py`, `legal.py`, `giving.py` na
`verses.py` hazina tatizo hili — zina `lang` au `_en` zao, si gettext.

### Sentensi zilizoundwa kwa f-string

Sentensi inayoundwa kwa f-string haina msgid, kwa hiyo haiwezi
kutafsiriwa — hata ikiwa sehemu zake zimo kwenye `.po`:

```python
"note": f"{pct(...)}% ya jumla ya wanachama"      # queries.py
_kpi("Wanachama Wote", jumla, ..., f"Hai: {hai}")  # leadership.py
_kpi("Matatizo Kwangu", wazi, ..., f"Ya haraka: {haraka}")
```

Zimebadilishwa kuwa `gettext("%(pct)s%% ya jumla ya wanachama") % {...}`
na `_("Hai: %(n)s") % {...}`. Na `templates/admin_panel/media.html`
ilikuwa na sentensi nzima ya Kiswahili bila `{% trans %}` kabisa.

### Majina ya database yaliyokuwa yakisomwa vibaya

Hii ni tofauti na tafsiri: thamani ilikuwa ipo, lakini kiolezo
kilikuwa kikisoma uwanja usiofaa.

`Zone` ina `name_en` na imejazwa ("Eastern Zone"), lakini kiolezo
kilikuwa kikiandika `{{ zone.name|tr }}` — yaani kumwomba gettext
atafsiri thamani ya database, ambayo haiko kwenye `.po`. Vivyo hivyo
`Fund`: `{{ f.name }}`, `{{ g.fund.name }}`, na
`{{ gift.fund.tx_name|default:gift.fund.name }}` — ambapo `tx_name`
**haipo kabisa** kwenye model, kwa hiyo `default` ilitumika kila mara.

Nimebadilisha kwenda `|tx:"name"`. Kwa `Zone` nimefanya zaidi:
`__str__` yake sasa inarudisha `tx("name")`, kwa sababu kanda
huonyeshwa kwa `str()` mahali pengi — orodha ya nyadhifa,
`Leadership.area_name`, chaguo za fomu — na kurekebisha kila moja
kungeacha zinazobaki. Mikoa, wilaya na kata hazina `name_en`; ni
majina ya pekee, hayatafsiriwi.

### Maoni yangu yalivuja kwenye HTML

Ukaguzi wa mwisho ulinasa kosa nililolifanya raundi hii: niliandika
maoni ya `{# ... #}` yenye mistari mingi kwenye kiolezo tatu.
**`{# #}` ya Django ni ya mstari MMOJA.** Ikizidi, inavuja kama
maandishi. Kwa hiyo `/mfumo/wanachama/`, `/mfumo/wadau/`, `/taifa/` na
`/kanda/` zilikuwa zikichapisha maelezo yangu ya msimbo kwenye
ukurasa — zikionekana kwa mtumiaji. Nimezibadilisha kuwa
`{% comment %}`. Hii ni kosa lile lile lililoandikwa kwenye faili hii
tangu awali kama la kujiepusha nalo; nililifanya tena.

### Kilichojaribiwa

* `msgfmt --check` — **msgid 2,190, zote zina tafsiri, hakuna fuzzy,
  hakuna kosa la `%(...)s`**. (Zilikuwa 1,895.)
* Kutembea **kurasa 59 kwa Kiingereza** (umma, uongozi ngazi mbili,
  paneli ya watumishi, eneo la mwanachama) kwa kutafuta maneno ya
  Kiswahili kwenye maandishi yanayoonekana. Kutoka mistari 20 hadi
  **1** — na iliyobaki ni thamani ya Kiswahili ndani ya
  `<textarea name="about">` kwenye ukurasa wa mipangilio, ambapo ndiyo
  inayohaririwa. Sahihi.
* Ukaguzi wa **kinyume**: Kiingereza kikivuja kwenye tovuti ya
  Kiswahili — **mistari 0**.
* Ukaguzi wa AST: lebo zinazopita `|tr` bila entry — **0**.
* Kutembea **kurasa 71 × majukumu 8 × lugha 2 = mara 1,136** —
  kurasa bovu 0, vitufe visivyoruhusiwa 0, kiolezo kilichovuja 0.
* Ukaguzi wa kurudia wa safari na majukumu: **vipimo 23, vyote OK**
  (ombi → malipo → kadi → nenosiri → kuingia; kusitisha; ngazi nne za
  ufinyu; majukumu sita; kughairi leja).

### Yaliyobaki

* **Lugha haiwezi kubadilishwa kwa `Accept-Language` kwa makusudi**
  (`core/middleware.py`) — Kiswahili ni lugha ya msingi hadi mtu
  achague mwenyewe. Ni uamuzi, si hitilafu, lakini inamaanisha jaribio
  la kivinjari lolote linahitaji kuweka cookie ya lugha.
* **`{% trans %}` yenye `\"`** bado ni mtego: `makemessages` itazalisha
  entries mbili zilizokatika kila inapoendeshwa. Zipuuze; zile za
  kweli zimeandikwa kwa mkono. Kuziondoa kabisa kunahitaji kubadilisha
  nukta mbili kwenye kiolezo (mfano " na "), yaani kubadilisha
  maandishi mtu anayoyaona.
* **`locale/sw`** ina msgid moja tu. Ni sahihi — Kiswahili ni lugha ya
  chanzo, haihitaji katalogi.

---

## Milango miwili ya kuingia

Ombi lilikuwa: fomu mbili za kuingia — moja ya wanachama, nyingine
maalum kwa viongozi wa aina zote — na zitenganishwe.

```
/ingia/            wanachama, wahisani, wajitoleaji
/ingia/viongozi/   viongozi wa aina zote
```

### "Viongozi wa aina zote" ni pande mbili

Mfumo huu una aina mbili za uongozi zisizohusiana kimuundo:

* **Nyadhifa za kuchaguliwa** (`geo.Leadership`) — mwenyekiti au katibu
  wa kata, wilaya, mkoa, kanda, taifa. Jukumu lao la mfumo mara nyingi
  ni `member`, na wanaingia kwa **namba ya uanachama**.
* **Maafisa wa ofisi** (`Role`) — usajili, fedha, michango, ustawi,
  wadau, mratibu, usimamizi. Wanaingia kwa **jina la mtumiaji**.

Wote wanapitia mlango wa viongozi. `_is_leader_account()` inaangalia
pande zote mbili; `_door_of()` inarudisha mlango unaomhusu mtu.

### Mlango kwanza, nenosiri baadaye

Hili ni jambo la usalama lililoamua muundo. Kama ukaguzi wa mlango
ungefanyika BAADA ya kuthibitisha nenosiri, afisa aliyefika mlango wa
wanachama angepata majibu mawili tofauti:

* nenosiri sahihi → "nenda mlango wa viongozi"
* nenosiri baya   → "nenosiri si sahihi"

Tofauti hiyo yenyewe ingekuwa ikithibitisha nenosiri kwa yeyote
anayelijaribu. Kwa hiyo mlango unaangaliwa **kwa kitambulisho pekee**,
kabla nenosiri kuguswa — na majibu yanakuwa sawa:

```
[  OK  ] Nenosiri sahihi na lisilo sahihi hutoa jibu lile lile mlango usio wake
```

Kinachofichuka ni "kitambulisho hiki ni cha kiongozi" — jambo lililo
wazi hata hivi (majina ya maafisa ni `usajili`, `malipo`; viongozi
wameorodheshwa kwenye `/mwanachama/viongozi/`).

### Kila mlango unafanya kazi yake

Chips za majukumu zimegawanywa kwa `door`. Ukurasa wa wanachama
haumwombi mtu jina la mtumiaji la ofisi; ukurasa wa viongozi
**hauna mwaliko wa kujiunga** — wadhifa hutolewa na mfumo
(`/mfumo/uongozi/`), si kwa kujiandikisha, na kumwambia mtu "jiunge"
kungeahidi kitu ambacho ukurasa huo hauwezi kutoa. Kila mmoja una
kiungo kimoja kidogo cha mlango mwingine.

Fomu yenyewe ni faili moja (`public/_login_form.html`) inayotumiwa na
milango yote miwili. Ulinzi — kikomo cha majaribio, kuzuia msimamizi
mkuu, ukaguzi wa kusitishwa, code ya SMS, arifa ya kuingia — ni mwili
mmoja (`_login_door`). Kuandika mara mbili ni kuhakikisha kwamba siku
moja moja itasahihishwa na nyingine itabaki na hitilafu.

Kurasa zilizolindwa zinaelekeza mlango sahihi: `staff_required`,
`role_required` na `leader_required` zote zinaenda `/ingia/viongozi/`,
na `@login_required` ya mwanachama inaenda `/ingia/`. Awali
`leader_required` ilitumia `LOGIN_URL` (`/ingia/`), yaani ilimtupa
kiongozi kwenye fomu ambayo akaunti yake inakataliwa.

### Kiongozi anaishia eneo lake

Kiongozi wa kata ana jukumu `member` na rekodi ya uanachama, kwa hiyo
`home_url_name()` ilimpeleka `/mwanachama/` — hata baada ya kubofya
"Kiongozi" na kuingia kwa nia ya kufanya kazi ya wadhifa wake. Mlango
anaouchagua ni maelezo ya anachotaka, kwa hiyo sasa anaenda
`/uongozi/`. Maafisa hawabadilishwi — `/usajili/`, `/malipo/` ni sahihi
kwao. Na `?next=` inashinda vyote.

### Hitilafu ya awali niliyoikuta njiani

`_clear_pending()` ilikuwa inafuta `mwst_next` pamoja na kila kitu
kingine, na iliitwa **mstari mmoja kabla ya** `_finish_login()` —
ambaye ndiye anayeisoma. Kwa hiyo mtu aliyebofya kiungo cha ndani
(`?next=/malipo/`), akaulizwa code ya SMS, alipelekwa ukurasa wake wa
kawaida badala ya pale alipotaka kwenda. Kiungo alichobofya kilipotea
kimya kimya **kila mara OTP ilipowashwa** — yaani kwa kila afisa, kila
siku.

Sasa `_clear_pending(keep_intent=True)` inaacha nia yake (aende wapi,
kifaa kikumbukwe, alitoka mlango upi) kwa `_finish_login`, na inafuta
vitufe vya "ni nani anasubiri" pekee.

### Uthibitisho wa hatua mbili haukubadilika

Maafisa: code kila mara. Viongozi wa kuchaguliwa: code kwenye kifaa
kipya, kisha kifaa kinaaminika siku 30 — sawa na mwanachama. Hii ni kwa
makusudi: hawana ofisi, wanatumia simu zao uwanjani, na code kila mara
ingekuwa kero inayowafanya watafute njia ya kuzunguka. Paneli yao
inaonyesha eneo lao pekee, si nchi nzima.

### Kilichojaribiwa

Vipimo **31, vyote OK**, kwenye database mpya:

* Kurasa zote mbili zinafunguka na ni **tofauti**: "Eneo la Viongozi"
  lipo upande mmoja pekee; mwaliko wa kujiunga upande mwingine pekee.
* Chips: wanachama wanaona "Mwanachama" na hawaoni "Afisa"/"Msimamizi";
  viongozi wanaona "Kiongozi"/"Msimamizi" na hawaoni "Mhisani".
* Mtu akifika mlango usio wake — **pande zote sita** (mwanachama,
  kiongozi wa kata, afisa × milango miwili) — anaelekezwa, na anaingia
  mlango wake.
* Nenosiri sahihi na baya hutoa jibu lile lile mlango usio wake.
* `/uongozi/`, `/taifa/`, `/malipo/` → `/ingia/viongozi/?next=...`;
  `/mwanachama/` → `/ingia/?next=...`.
* Msimamizi mkuu bado amezuiwa pande zote mbili.
* **OTP**: mlango, `next` na "Kumbuka mimi" vyote vinavuka hatua ya
  code. Kiongozi → `/uongozi/`, afisa aliyeomba `/malipo/` → `/malipo/`.
* Safari ya usajili bado nzima: ombi → malipo → kadi → kuweka nenosiri
  → **`/ingia/`** (mlango wa wanachama) → `/mwanachama/kadi/`.
* Kutembea kurasa 71 × majukumu 8 × lugha 2: **matatizo 0**.
* Tafsiri 13 mpya; `.po` ina msgid **2,203**, zote zina tafsiri.
  Kurasa zote mbili: Kiswahili safi, Kiingereza safi.

### Yaliyobaki

* **Fomu ndogo ya kuingia kwenye ukurasa wa mbele** (`home.html`)
  inatuma kwa `/ingia/`. Kiongozi akiitumia anaelekezwa mlango wake —
  inafanya kazi, lakini ni hatua ya ziada. Kuiondoa au kuigawa ni
  uamuzi wa muonekano, sikuugusa.
* **`LOGIN_URL` bado ni `/ingia/`**. Ni sahihi kwa `@login_required` ya
  kurasa za mwanachama; kurasa za uongozi zina vizuizi vyao
  vinavyoelekeza mlango wao. Kama view mpya ya uongozi itaongezwa kwa
  `@login_required` peke yake, itaelekeza mlango usio sahihi — tumia
  `leader_required` au `role_required`.

### Nyongeza: mlango wa viongozi haukuonekana

Fomu zote mbili zilikuwa zikifanya kazi, lakini ya viongozi haikuwa na
**njia yoyote ya kuifikia** kutoka kwenye tovuti — kilikuwa sentensi
ndogo chini ya ukurasa wa wanachama pekee. Kwa vitendo ilihitajika
kujua URL `/ingia/viongozi/` kichwani, na hakuna kiongozi anayeweza
kuibahatisha. Kutengeneza mlango na kutoueleza ni kama kutokuutengeneza.

Sasa unafikiwa kwa njia nne:

* **Footer ya kila ukurasa** — "Ingia kama Kiongozi"
* **Menyu ya simu** (drawer) — kitufe chake. Header haigusi: ina nafasi
  ya vitufe viwili pekee, na kuongeza cha tatu kunabana (imeandikwa
  hivyo kwenye kiolezo tangu awali).
* **Kitufe kwenye `/ingia/`**, chenye mstari wa kutenganisha — si
  mwendelezo wa fomu, ni njia nyingine kabisa
* **Kitufe cha kurudi** kwenye `/ingia/viongozi/`

Imejaribiwa: kiungo kipo kwenye `/`, `/kuhusu/`, `/lipa/` na `/ingia/`
kwa lugha zote mbili, na milango yote miwili bado inafanya kazi
(afisa → `/usajili/`, mwanachama → anaelekezwa mlango wake).
