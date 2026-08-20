# Pesapal — kuunganisha na kuwasha

Mfumo hauna tena hali ya majaribio. Kila njia ya malipo inayoonekana kwenye
fomu inafanya kazi kweli: njia zote za simu na kadi zinapitia Pesapal, na
uhamisho wa benki unathibitishwa na afisa kwa mkono.

---

## 1. Environment variables kwenye Render

Render → huduma yako → **Environment**:

| Ufunguo | Thamani | Lazima? |
|---|---|---|
| `DATABASE_URL` | `postgresql://postgres.xxx:NYWILA@aws-0-eu-west-3.pooler.supabase.com:5432/postgres` | Ndiyo |
| `SECRET_KEY` | herufi 50+ za nasibu | Ndiyo |
| `DEBUG` | `False` | Ndiyo |
| `ALLOWED_HOSTS` | `.onrender.com` | Ndiyo |
| `SITE_URL` | `https://mwiso.onrender.com` | Ndiyo |
| `PESAPAL_CONSUMER_KEY` | kutoka Pesapal | Ndiyo |
| `PESAPAL_CONSUMER_SECRET` | kutoka Pesapal | Ndiyo |
| `PESAPAL_ENV` | `sandbox`, baadaye `live` | Ndiyo |
| `PESAPAL_IPN_ID` | hatua ya 3 hapa chini | Ndiyo |

Mfumo hauanzi bila `DATABASE_URL`, na hauanzi kama `SITE_URL` si `https://`.
Hizo ni kinga za makusudi: ya kwanza inazuia kumbukumbu kupotea kwenye SQLite
inayofutwa kila deploy, ya pili inazuia callback ya Pesapal kuvunjika kimya
kimya baada ya mtu kulipa.

**Nywila ya Supabase ilikuwa wazi kwenye `settings.py` na ipo kwenye git
history.** Kuiondoa kwenye kodi hakuitoi kwenye historia. Ibadilishe kwenye
Supabase (Project Settings → Database → Reset password) kabla ya kuweka
`DATABASE_URL`.

## 2. Deploy

Environment variables husomwa wakati wa kuanza. Ukiongeza baada ya deploy,
fanya deploy nyingine (Manual Deploy → Deploy latest commit).

## 3. Sajili IPN mara moja

Kwenye Render Shell:

    python manage.py pesapal_ipn

Utapata:

    IPN imesajiliwa: https://mwiso.onrender.com/pesapal/ipn/
    PESAPAL_IPN_ID=fe078e53-78da-4a83-aa89-e7ded5c456e6

Weka namba hiyo kama `PESAPAL_IPN_ID`, kisha deploy tena. Bila hiyo,
`SubmitOrderRequest` inakataliwa na Pesapal.

Kuona zilizosajiliwa: `python manage.py pesapal_ipn --list`

## 4. Jaribu kwa sandbox

Nenda `/changia/`, chagua njia yoyote ya simu au kadi, tuma. Utapelekwa
Pesapal. Tumia kadi za majaribio za Pesapal kukamilisha. Ukirudi,
risiti inapaswa kusoma **"Malipo yako yamekamilika"**.

Jaribu pia kughairi ukiwa Pesapal — risiti inapaswa kubaki
**"inasubiri"**, si "imekamilika".

## 5. Hamia live

1. `PESAPAL_ENV=live`
2. Funguo za live (za sandbox hazifanyi kazi live)
3. **Sajili IPN upya** — `PESAPAL_IPN_ID` ya sandbox haifai live
4. Fanya muamala mmoja mdogo halisi kabla ya kutangaza

---

## Jinsi malipo yanavyofanya kazi

`core/data/giving.py` inaeleza kila njia inavyokamilishwa:

* **`gateway: "pesapal"`** — M-Pesa, Airtel, Mixx, HaloPesa, T-Pesa,
  EzyPesa, Visa/Mastercard. Chaguo la mtumiaji hapa ni dokezo tu; njia
  halisi anaichagua tena kwenye ukurasa wa Pesapal.
* **`gateway: "manual"`** — uhamisho wa benki. Unabaki `pending` hadi afisa
  athibitishe. Hakuna mahali mfumo unaposema pesa imeingia kabla ya hapo.

Njia isiyo na njia ya kukamilishwa haiwekwi kwenye orodha. PayPal iliondolewa
kwa sababu hiyo.

## Kwa nini callback haiaminiki

Pesapal inamrudisha mtu kwenye `/pesapal/callback/?OrderTrackingId=...`.
Mtu yeyote anaweza kuandika URL hiyo mwenyewe kwenye kivinjari. Kwa hiyo
hali **haichukuliwi kutoka kwenye URL** — inaulizwa Pesapal moja kwa moja
kwa `GetTransactionStatus`. Vivyo hivyo kwa IPN: inatuambia tu "kuna
mabadiliko", si mabadiliko yenyewe ni yapi.

## Kushindwa hakupotezi rekodi

Pesapal ikigoma, mchango unabaki `pending`, sababu inaandikwa kwenye log,
na mtumiaji anaambiwa wazi kwamba malipo hayajakamilika. Hakuna risiti
inayodai mafanikio yasiyokuwepo.
