# MUWESTA — Mfumo wa Usimamizi wa Uanachama

Mfumo kamili wa Muslim Welfare Society of Tanzania: tovuti ya umma,
uanachama, michango, malipo ya mtandaoni, pointi, na dashibodi za
watumishi.

---

## 1. Kusimika kwenye kompyuta yako

```cmd
cd MWST
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

copy .env.example .env
python manage.py migrate
python manage.py seed
python manage.py watumishi --reset --password mwst2026
python manage.py pointi
python manage.py collectstatic --noinput
python manage.py runserver
```

Fungua `http://127.0.0.1:8000/` na uingie kwa `admin` / `mwst2026`.

`.env` haiendi kwenye git wala Render. Environment halisi HUSHINDA
`.env` daima, kwa hiyo faili hii haiwezi kuathiri production.

---

## 2. Mazingira (environment variables)

| Kigezo | Maana |
|---|---|
| `DEBUG` | `True` kwa development pekee |
| `SECRET_KEY` | Badilisha kabla ya production |
| `ALLOWED_HOSTS` | `.onrender.com` kwa Render |
| `SITE_URL` | `https://mwiso.onrender.com` — lazima iwe https |
| `DATABASE_URL` | Ikikosekana, inarudi Supabase iliyoandikwa kwenye settings |
| `SELCOM_API_KEY` / `_SECRET` / `_VENDOR_ID` | Malipo ya simu (USSD push) |
| `PESAPAL_CONSUMER_KEY` / `_SECRET` / `_ENV` / `_IPN_ID` | Malipo ya kadi |

Render haitasoma `render.yaml` kama service iliundwa kwa mkono —
weka vigezo hivi kwenye dashibodi.

**Build Command ya Render:**

```
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

Bila `migrate` mwishoni, migration mpya hazitafika kwenye database.

---

## 3. Amri za usimamizi

| Amri | Kazi |
|---|---|
| `python manage.py seed` | Data ya awali (kanda, mikoa, madaraja, mifuko) |
| `python manage.py watumishi` | Unda akaunti za watumishi. `--reset` kubadilisha nenosiri, `--mratibu <code>` kwa kanda |
| `python manage.py pointi` | Weka kanuni za pointi za ushiriki |
| `python manage.py pesapal_ipn` | Sajili IPN URL kwa Pesapal (mara moja) |
| `python manage.py expire_members` | Weka alama kwa wanachama waliomaliza muda |
| `python manage.py compilemessages` | Kompaili tafsiri baada ya kuhariri `.po` |

---

## 4. Mtiririko wa uanachama

```
/jiunge/  ->  Ombi (pending)
              |
              v  afisa anahakiki
          awaiting_payment  ->  afisa anampa kiungo:
                                /lipa/?ombi=APP/MUWESTA/2026/0001
              |
              v  malipo yanathibitishwa (Selcom au Pesapal)
          Mwanachama kamili: namba, kadi ya QR, akaunti ya kuingia
```

Namba ya uanachama, kadi na nenosiri **hazitolewi** wakati wa kuhakiki —
zinatolewa malipo yakithibitishwa. Kwa malipo ya nje ya mfumo (taslimu au
benki), tumia hatua ya *Kamilisha uanachama* kwenye Django admin.

Kipindi kimoja cha uanachama ni **miaka mitatu**.

---

## 5. Malipo

| Njia | Gateway | Mtiririko |
|---|---|---|
| Lipa kwa Simu | Selcom | Kidokezo kinatumwa simuni; mtu habaki kuondoka tovuti |
| Kadi ya Benki | Pesapal | Mtu anapelekwa ukurasa wa Pesapal |
| Benki / PayPal | — | Zimewekwa kama "zinakuja"; fomu inazikataa upande wa seva |

**Kanuni ya msingi:** callback wala webhook **haviaminiki** peke yake.
Hali halisi huthibitishwa kwa `GetTransactionStatus` (Pesapal) au
`order-status` (Selcom). Hali isiyofahamika huhesabiwa `pending`, si
`confirmed`.

URL za kuweka kwa watoa huduma:

- Pesapal IPN: `https://mwiso.onrender.com/pesapal/ipn/`
- Selcom webhook: `https://mwiso.onrender.com/selcom/webhook/`

---

## 6. Pointi za MUWESTA

Sera yote ipo kwenye **`programs/points.py`** — mahali pamoja pekee:

| Kigezo | Thamani | Maana |
|---|---|---|
| `SHILLINGS_PER_POINT` | 1,000 | TSh kwa pointi 1 |
| `MONEY_CAP` | 4,000 | Kikomo cha pointi za fedha kwa kipindi |
| `MEMBERSHIP_FEE_POINTS` | 100 | Pointi za ada |
| `PERIOD_YEARS` | 3 | Kipindi kinachoamua kiwango |
| `OFFICER_DAILY_CAP` | 300 | Kikomo cha afisa kwa siku |

Ngazi: Mshiriki → Mchangiaji → Mhudumu → Nguzo → Mhimili wa Jamii.

Pointi mbili: **za kipindi** (miaka 3, zinaamua kiwango) na **za maisha**
(hazipungui, za vyeti). Bonasi za muda huwekwa kupitia Django admin →
*Bonasi za Pointi*, si kwenye code.

---

## 7. Lugha

Kiswahili ndiyo lugha ya msingi; Kiingereza kipo kwenye
`locale/en/LC_MESSAGES/django.po`.

Ukiongeza maandishi mapya:

```cmd
python manage.py makemessages -l en
python manage.py compilemessages
```

Hati za kisheria (`core/data/legal.py`) **hazitumii** `{% trans %}` —
zina matoleo mawili kamili. Ukibadilisha moja, badilisha jingine.

---

## 8. Onyo la usalama

Nywila ya Supabase bado imeandikwa kwenye `config/settings.py` kama
fallback, na ipo kwenye git history. **Ibadilishe Supabase**, kisha
uweke anwani mpya kwenye `DATABASE_URL` ya Render pekee.

Vivyo hivyo kwa funguo za Pesapal na Selcom zilizowahi kupita kwenye
mazungumzo au terminal — zi-regenerate kabla ya kwenda live.

Nenosiri moja kwa watumishi wote (`mwst2026`) ni la majaribio pekee.
Kwa mfumo halisi endesha `python manage.py watumishi --reset` bila
`--password`; kila mmoja atapata lake la nasibu.
