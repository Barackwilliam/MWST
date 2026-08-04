# MWST Membership Management System

Mfumo kamili wa Usimamizi wa Uanachama wa **Muslim Welfare Society of Tanzania** —
tovuti ya umma, dashboards za maafisa, na backend yenye database halisi.

---

## Kuendesha (Windows)

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```

Fungua <http://127.0.0.1:8000/>

### Watumiaji wa mfano

| Mtumiaji | Password | Jukumu | Anakoenda |
|---|--|---|---|
| `admin` | `mwst2026` | Msimamizi Mkuu | `/taifa/` |
| `usimamizi` | `mwst2026` | Afisa wa Usimamizi | `/taifa/` |
| `usajili` | `mwst2026` | Afisa Usajili | `/usajili/` |
| `malipo` | `mwst2026` | Afisa Malipo ya Ada | `/malipo/` |
| `michango` | `mwst2026` | Afisa Michango | `/michango/` |
| `wadau` | `mwst2026` | Afisa Wadau | `/wadau/` |
| `mratibu` | `mwst2026` | Mratibu wa Mkoa | `/taifa/` |
| `mwanachama` | `mwst2026` | Mwanachama | `/mwanachama/` |

### Usimamizi wote uko ndani ya mfumo

`/mfumo/` ina **model 39** zinazosimamiwa kwa design ya MWST yenyewe: orodha,
kutafuta, kuchuja, kuongeza, kuhariri na kufuta. Hakuna mtu anayetolewa nje
kwenda Django admin.

Django admin ipo kwa **dharura pekee** kwenye `/dharura-admin/` — haitajwi
popote kwenye menyu. Kuibadilisha au kuizima kabisa, weka `DJANGO_ADMIN_URL`
kwenye environment (thamani tupu = imezimwa).

### Ukubwa wa data za mfano

`seed` inaweka **rekodi 20 au chini kwa kila sehemu** — inatosha kuona kila
kipengele kikifanya kazi bila kujaza database.

```bat
python manage.py seed --limit 50      :: rekodi 50 kwa kila sehemu
python manage.py seed --mikoa-yote    :: mikoa yote 26 ya Tanzania
python manage.py seed --fresh         :: futa data za zamani kwanza
```

Kwa chaguo-msingi mikoa ni 20, kwa hiyo ramani inaonyesha mikoa 20. Kwa
matumizi halisi tumia `--mikoa-yote`, au weka mikoa iliyobaki kupitia
`/usimamizi/geo/region/`.

Wilaya na kata ni moja kwa kila mzazi — kiwango cha chini kinachoruhusu
cascading dropdowns za fomu ya usajili kufanya kazi. Ongeza zilizobaki
kwenye admin kadri unavyohitaji.

---

## Kurasa

### Tovuti ya umma
`/` Nyumbani · `/kuhusu/` · `/uanachama/` · `/huduma/` · `/habari/`
`/matukio-yetu/` · `/mawasiliano/` · `/jiunge/` · `/ingia/` · `/hakiki/<serial>/`

### Eneo la Mwanachama
| Ukurasa | Anachoweza kufanya |
|---|---|
| `/mwanachama/` | Dashibodi, kadi, salio, pointi |
| `/mwanachama/wasifu/` | Kuhariri taarifa zake |
| `/mwanachama/kadi/` | Kadi yenye QR + historia ya kadi |
| `/mwanachama/malipo/` | Historia + **kulipa ada** |
| `/mwanachama/michango/` | Historia + **kutoa mchango** |
| `/mwanachama/pointi/` | Leja ya pointi + tuzo |
| `/mwanachama/msaada/` | **Kuomba msaada** + kufuatilia |
| `/mwanachama/familia/` | Kuongeza/kuondoa familia na wanufaika |
| `/mwanachama/matukio/` | **Kujiandikisha** kwenye matukio |
| `/mwanachama/taarifa/` | Matangazo, arifa na habari |

### Maafisa
| Ukurasa | Jukumu |
|---|---|
| `/usajili/` | Afisa Usajili — kusajili mwanachama |
| `/maombi/` | Kuidhinisha au kukataa maombi |
| `/wanachama/` | Orodha yenye vichujio |
| `/mwanachama-taarifa/<id>/` | Maelezo kamili + kusitisha/kutoa kadi |
| `/malipo/` | Afisa Fedha — kurekodi na **kuthibitisha** malipo |
| `/michango/` | Afisa Michango — kurekodi na kuthibitisha |
| `/ustawi/` | Afisa Ustawi — **kuidhinisha maombi ya msaada** |
| `/maombi/<id>/hariri/` | **Kusahihisha ombi** kabla ya kuidhinisha |
| `/mwanachama-taarifa/<id>/hariri/` | **Kuhariri taarifa** za mwanachama |
| `/risiti/<aina>/<id>/` | Risiti inayochapishwa |
| `/ujumbe/` | **Kutuma ujumbe** kwa wanachama |

### Kutuma ujumbe

`/ujumbe/` inaruhusu kutuma kwa: wanachama wote, walio hai, kategoria moja,
mkoa mmoja, au **waliochelewa kulipa** (hawajalipa siku 45).

| Njia | Hali |
|---|---|
| Arifa ya ndani | Inafanya kazi — inafika mara moja kwenye `/mwanachama/taarifa/` |
| Barua pepe | Inafanya kazi — inahitaji `EMAIL_HOST`; bila hiyo inachapishwa console |
| SMS | Inahifadhiwa kwenye foleni (`MessageLog`) hadi gateway iunganishwe |

Ujumbe unabinafsishwa: `{jina}` na `{namba}` zinabadilishwa kwa kila
mwanachama. Mratibu akituma, unawafikia kanda yake pekee.

### Mratibu wa Kanda
| Ukurasa | Anachoona |
|---|---|
| `/kanda/` | Dashibodi ya kanda yake: KPI, ramani, mikoa, matukio |
| `/kanda/mikoa/` | Mikoa, halmashauri na idadi ya kata |
| `/kanda/wanachama/` | Wanachama wa kanda yake pekee |
| `/maombi/` | Maombi ya kanda yake |
| `/matukio/` | Matukio ya kanda yake |
| `/taifa/` | Muhtasari wa taifa (kusoma tu) |

Kila kitu kimebanwa kwa kanda. Mratibu akifungua `/wanachama/` au
`/malipo/` moja kwa moja, bado anaona kanda yake tu. Akijaribu
`/kanda/?kanda=nyingine`, anarudishwa kwenye kanda yake.

### Msimamizi
`/taifa/` (na jedwali la mchanganuo wa kanda zote sita) · `/dashibodi/` ·
`/wadau/` · `/media/` · `/usimamizi/`

Msimamizi anaweza kufungua dashibodi ya kanda yoyote:
`/kanda/?kanda=ziwa`

### Kupakua ripoti (CSV)
`/pakua/malipo/` · `/pakua/michango/` · `/pakua/wanachama/` · `/pakua/maombi/`
`/pakua/wahisani/` · `/pakua/matukio/` · `/pakua/mikoa/` · `/pakua/kanda/`

Mratibu akipakua, anapata data ya kanda yake pekee.

Vichujio vya ukurasa vinaheshimiwa: `/pakua/malipo/?status=pending&from=2026-01-01`

---

## Mzunguko wa Uanachama

```
MTU WA NJE                AFISA USAJILI              MWANACHAMA
─────────                 ─────────────              ──────────
/jiunge/
jaza fomu
   │
   ▼
Application               /maombi/
APP/MWST/2026/0021   ──►  anaona ombi
"pending"                 anabonyeza IDHINISHA
                             │
                             ▼
                          Kwa muamala mmoja:
                          • Member  MWST/G/000002/2026
                          • Account 1100000021
                          • Card    MWST/G/00021/2026 (QR)
                          • User    (jina = namba ya uanachama)
                          • Arifa ya kukaribisha
                             │
                             ▼
                          Skrini inaonyesha MARA MOJA:
                          jina la mtumiaji + nenosiri la muda
                          Afisa anampigia simu mwanachama
                             │                          │
                             └──────────────────────────▼
                                                   /ingia/
                                                   (namba au barua pepe)
                                                        │
                                                        ▼
                                                   /mwanachama/
```

**Nenosiri la muda linaonyeshwa mara moja tu** — halihifadhiwi popote. Afisa
akilisahau, anabonyeza *Rekebisha Nenosiri* kwenye ukurasa wa maelezo ya
mwanachama (`/mwanachama-taarifa/<id>/`) na kupata jipya. Mwanachama mwenye
barua pepe anaweza pia kutumia `/nenosiri/sahau/` mwenyewe.

Wanachama waliokuwepo kabla ya mabadiliko haya hawana akaunti ya kuingia.
Kitufe *Tengeneza Akaunti* kwenye ukurasa wao kinaitengeneza.

### Malipo yanafuata mkondo ule ule

Mwanachama akilipa kupitia `/mwanachama/malipo/`, malipo yanaingia yakiwa
**`pending`**. Afisa wa fedha anathibitisha kwenye `/malipo/` — ndipo leja
inaingizwa na pointi zinatolewa. Hakuna fedha inayoingia kwenye leja bila
afisa kuthibitisha.

---

## Madaraja ya Uanachama

| Daraja | Ada ya Mwezi | Kuchagua |
|---|---|---|
| Bronze | TZS 5,000 | Ndiyo |
| Silver | TZS 10,000 | Ndiyo |
| Gold | TZS 20,000 | Ndiyo |
| Platinum | TZS 50,000 | Ndiyo |
| **Tanzanite** | TZS 100,000 | **Hapana — la heshima** |

**Tanzanite haliombwi.** Halionekani kwenye fomu ya `/jiunge/` wala kwenye
usajili wa afisa. Linaonyeshwa kwenye `/uanachama/` kama daraja la heshima
pekee, likiwa na maelezo kwamba linatolewa na Uongozi.

Msimamizi (`super_admin` au `admin`) pekee ndiye anayeweza kulitoa. Kwenye
`/mwanachama-taarifa/<id>/` kuna kitufe **Toa Daraja la Tanzanite**. Kikibonyezwa:

1. Daraja linabadilika
2. **Kadi mpya inatolewa** — namba mpya yenye herufi `T`
3. Mwanachama anapata **arifa** kwenye dashibodi yake

Afisa wa kawaida hataoni kitufe hicho, na akijaribu kupitisha daraja kwenye
fomu ya kuhariri, halikubaliki — dropdown yake haina Tanzanite kabisa.

Kudhibiti hili kwenye admin: `Category.is_selectable` (kuzima kuchagua) na
`Category.is_special` (kuonyesha kama heshima). Ukitaka daraja jingine la
heshima, weka bendera hizo — hakuna code inayohitaji kubadilishwa, hata rangi
inatoka `Category.colour`.

---

## Kanda na Jiografia

Tanzania Bara imegawanywa **kanda sita**, kila moja na mratibu mmoja:

| Kanda | Mikoa | Ofisi | Mtumiaji |
|---|---|---|---|
| Mashariki | Dar es Salaam, Pwani, Morogoro, Tanga | Dar es Salaam | `mratibu.mashariki` |
| Kaskazini | Arusha, Kilimanjaro, Manyara | Arusha | `mratibu.kaskazini` |
| Ziwa | Mwanza, Mara, Kagera, Geita, Simiyu, Shinyanga | Mwanza | `mratibu.ziwa` |
| Kati | Dodoma, Singida, Tabora | Dodoma | `mratibu.kati` |
| Magharibi | Kigoma, Katavi, Rukwa | Kigoma | `mratibu.magharibi` |
| Kusini na Nyanda za Juu Kusini | Mbeya, Songwe, Iringa, Njombe, Lindi, Mtwara, Ruvuma | Mbeya | `mratibu.kusini` |

Nenosiri la wote: `mwst2026`

**Kanda ya sita ina mikoa saba** kwa sababu uligusa kanda sita. Kiutaalamu
Kusini (Lindi, Mtwara, Ruvuma) na Nyanda za Juu Kusini (Mbeya, Songwe,
Iringa, Njombe) huwa kanda mbili tofauti. Ukitaka kuzitenganisha, ongeza
kanda ya saba kwenye `/usimamizi/geo/zone/` kisha hamishia mikoa mitatu ya
Kusini huko.

### Jiografia ni halisi, si ya mfano

`geo/tanzania.py` ina mgawanyo halisi wa kiutawala:

- **Mikoa 26** ya Tanzania Bara
- **Halmashauri 184** — DC (Wilaya), MC (Manispaa), CC (Jiji), TC (Mji)
- **Kata 1,338**

Halmashauri zimeorodheshwa kwa **ukamilifu**. Kata zilizoorodheshwa ni kata
halisi za kila halmashauri, lakini si orodha kamili — Tanzania ina kata zaidi
ya 3,900. Ongeza zilizobaki kupitia `/usimamizi/geo/ward/` au import ya CSV.

Halmashauri zenye jina moja lakini aina tofauti (mfano **Kibaha TC** na
**Kibaha DC** mkoani Pwani) ni rekodi mbili tofauti — hiyo ndiyo hali halisi.

---

## Picha

`static/img/hero-mosque.jpg` (1280px, 187 KB) ndiyo picha ya hero ya ukurasa
wa mbele, na `hero-mosque-sm.jpg` (900px, 102 KB) inatumika kwenye simu.
Kubadilisha, weka picha yako kwa majina hayo hayo — hakuna code inayohitaji
kubadilishwa.

**Onyo la template**: Django `{# ... #}` inafanya kazi **mstari mmoja tu**.
Comment ya mistari mingi haichujwi — inachapishwa kwenye ukurasa kama
maandishi. Kwa maelezo marefu tumia `{% templatetag openblock %} comment {% templatetag closeblock %}`.

---

## Apps

```
accounts/   User (majukumu 10), AuditLog
geo/        Region, District, Ward, Branch
members/    Category, Member, Application, Card, FamilyMember, Beneficiary
finance/    Fund, Account, LedgerEntry, Payment, Contribution,
            Project, Campaign, Donor, Expense
programs/   PointRule, PointTransaction, Reward, AssistanceRequest,
            EventType, Event, EventRegistration
content/    SiteSetting, Verse, News, Announcement, Album, MediaItem,
            Service, Faq, Leader, Milestone, Pillar, ContactMessage,
            Notification, MessageLog
core/       queries.py (selectors), forms.py, views.py, mixins.py
```

---

## Maamuzi muhimu ya usanifu

**Namba za mfululizo** — `core.mixins.Sequence` inatumia `select_for_update()`
ndani ya transaction. Haiwezekani wanachama wawili kupata namba moja.

- Namba ya uanachama: `MWST/G/000123/2026`
- Namba ya akaunti: `1100000123`
- Risiti ya ada: `MWST-R-000245`
- Risiti ya mchango: `MWST-M-000421`
- Namba ya ombi: `APP/MWST/2026/0025`

**Leja** — salio la mwanachama halihifadhiwi kama namba; linahesabiwa kutoka
`LedgerEntry`. Ingizo halifutwi kamwe; kurekebisha kosa unaingiza entry ya
kinyume (`reverses`). Admin haina ruhusa ya kufuta leja.

**Pointi** — pia ni leja (`PointTransaction`). Salio ni jumla ya miamala.
Pointi zinatolewa moja kwa moja malipo yanapothibitishwa.

**Fedha zenye masharti** — Zaka, Waqf, Miradi, Fitrah na Kafara zina
`is_restricted=True`. Hazichanganywi na matumizi ya kawaida.

**Idempotency** — `Payment.idempotency_key` ina unique constraint. Gateway
ikituma callback mara mbili, malipo hayaingii mara mbili.

**Decimal** — fedha zote ni `DecimalField(max_digits=14+, decimal_places=2)`.
Hakuna float popote.

---

## Lugha (i18n)

Kiswahili ndiyo lugha ya msingi. Kiingereza kinaongezwa juu yake.

**Maandishi ya mfumo** — `core/translations.py` (maneno 870), inakusanywa kwa
`python tools/build_mo.py`. Hakuna haja ya GNU gettext.

**Maudhui ya database** — kila model yenye maudhui ina field mbili:
`title` (Kiswahili) na `title_en` (Kiingereza). Mixin ya `Bilingual` ina
method `.tx("title")` inayochagua kulingana na lugha inayotumika.

```python
class News(Bilingual, TimeStamped):
    title = models.CharField(max_length=200)      # Kiswahili
    title_en = models.CharField(max_length=200)   # English
```

Kwenye admin unajaza zote mbili. `title_en` ikiwa tupu, Kiswahili kinatumika.

---

## Vinavyofanya kazi kikamilifu

- Kuingia na kutoka, kuelekezwa kulingana na jukumu
- Ombi la uanachama kutoka tovuti → kuidhinishwa → mwanachama + kadi + akaunti
- Kurekodi malipo → leja → pointi → risiti
- Kurekodi michango kwa mfuko, mradi na kampeni
- Kujiandikisha kwenye matukio (mwanachama au mgeni)
- Fomu ya mawasiliano
- Uhakiki wa kadi kwa QR (`/hakiki/<serial>/`)
- Vichujio kwenye maombi na wanachama
- Kuhariri wasifu wa mwanachama
- Django admin kwa kila model
- Audit log ya kila kitendo muhimu

## Usalama wa kuingia

| Kinga | Jinsi inavyofanya kazi |
|---|---|
| Kuzuia kubahatisha nenosiri | Majaribio 8 kwa IP kwa dakika 15 |
| Open redirect | `?next=` inakubaliwa tu ikiwa ni ya tovuti hii |
| Herufi kubwa/ndogo | `ADMIN`, `admin`, `AdMiN` zote zinakubalika |
| Njia tatu za kuingia | Jina la mtumiaji, namba ya uanachama, au barua pepe |
| Kumbukumbu | Kila jaribio lililoshindwa linaingia kwenye audit log |

Kuzuia kunatumia cache ya Django. Kwenye seva moja `LocMemCache` inatosha;
kwa seva nyingi tumia Redis ili hesabu ishirikiwe.

---

## Kuingia kunagoma?

```bat
python manage.py akaunti
```

Inaonyesha jedwali la watumiaji wote wa mfano na kama nenosiri lao linafanya
kazi. Kisha:

```bat
python manage.py akaunti --reset mwanachama   :: mmoja
python manage.py akaunti --reset-all          :: wote
```

Sababu za kawaida:

| Dalili | Sababu | Suluhisho |
|---|---|---|
| "Hakuna mtumiaji yeyote" | `seed` haijaendeshwa | `python manage.py seed` |
| Nenosiri "IMEVUNJIKA" | akaunti imeharibika | `akaunti --reset-all` |
| Ameingia lakini anarudi nyumbani | `mwanachama` hajaunganishwa na rekodi | `akaunti --reset mwanachama` |
| 403 CSRF | `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` | angalia env vars |

Kuendesha `seed` tena ni salama — nenosiri za watumiaji wa mfano zinawekwa
upya kila mara, kwa hiyo huwezi kubaki na akaunti iliyoharibika.

---

## Kazi za matengenezo

```bat
python manage.py ruhusa                    # makundi ya ruhusa kwa kila jukumu
python manage.py akaunti                   # kagua akaunti za kuingia
python manage.py safisha_simu              # weka namba za simu muundo mmoja
python manage.py expire_members            # weka 'expired' kwa muda ulioisha
python manage.py expire_members --dry-run  # onyesha tu
python tools/build_mo.py                   # kusanya tafsiri
```

**`ruhusa`** ni muhimu. Bila hiyo afisa ana `is_staff=True` lakini hana ruhusa
yoyote, kwa hiyo kila ukurasa wa `/usimamizi/` unamkatalia. `seed` inaiita
yenyewe. Ukiongeza jukumu jipya au model mpya, endesha tena.

Endesha `expire_members` mara moja kwa siku (GitHub Actions au cron ya Render).

---

## Vilivyobaki kwa awamu ijayo

Vipengele hivi **pekee** ndivyo bado vina popup ya "awamu ijayo" (52 kati ya
117 vilivyokuwepo mwanzo). Vyote vinahitaji huduma ya nje:

| Kipengele | Kinachohitajika |
|---|---|
| Kutuma SMS | Gateway (BulkSMS / AfricasTalking / Twilio) |
| Kutuma barua pepe kwa wingi | SMTP + foleni |
| PDF ya kadi na risiti | WeasyPrint au ReportLab |
| Ripoti za Excel | openpyxl |
| Malipo ya moja kwa moja | Aggregator (ClickPesa / Selcom / AzamPay) + webhook |
| Kuchagua mwaka/kipindi kwenye chati | Filters za mwaka kwenye queries |
| Kucheza video | Player + hifadhi ya video |

**Kila kitu kingine kinafanya kazi kwa data halisi**, ikiwa ni pamoja na
kurejesha nenosiri (`/nenosiri/sahau/`) ambako Django hutumia SMTP —
bila `EMAIL_HOST`, barua pepe inachapishwa kwenye console.

---

## Kupeleka Render

`render.yaml` ipo. Env vars:

| Key | Thamani |
|---|---|
| `SECRET_KEY` | Render itaitengeneza |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com` |
| `DATABASE_URL` | connection string ya Supabase/Postgres |

Bila `DATABASE_URL` mfumo unatumia SQLite.

**Usiweke `.env` wala `db.sqlite3` kwenye Git.**

Mipangilio ya usalama (HSTS, SSL redirect, secure cookies) inawaka yenyewe
`DEBUG=False` inapowekwa. Ukisahau kuweka `SECRET_KEY` halisi, mfumo
utakataa kuanza badala ya kuendesha kwa key ya mfano.
