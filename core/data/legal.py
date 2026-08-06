"""
Maudhui ya kurasa za kisheria (Sera ya Faragha na Sera ya Vidakuzi).

Tofauti na kurasa nyingine, hati hizi hazitafsiriwi kwa `{% trans %}` kila
sentensi. Hati ya kisheria hutafsiriwa nzima na kupitishwa nzima, kwa hiyo
tunahifadhi matoleo mawili kamili na kuchagua kwa kutumia lugha ya mtumiaji.
Ukibadilisha toleo moja, kumbuka kubadilisha jingine.

Muundo wa kila hati:
    {
      "eyebrow", "title", "intro", "effective", "scene",
      "sections": [
          {"n", "h", "p": [...], "bullets": [...],
           "sub": [{"h", "p": [...], "bullets": [...]}], "note"}
      ],
      "contact": {"lines": [...]},
      "consent": {"h", "p"},
    }
"""

# ---------------------------------------------------------------------------
#  Taarifa za mawasiliano — chanzo kimoja kwa hati zote mbili
# ---------------------------------------------------------------------------
ORG_SW = [
    ("Jina", "Muslim Welfare Society of Tanzania (MWST)"),
    ("Anwani ya makazi", "Nkuhungu, Dodoma, Tanzania"),
    ("Anwani ya posta", "S.L.P. 0000, Dodoma"),
    ("Simu", "+255 769 600 102"),
    ("Barua pepe", "info@muslimwelfare.or.tz"),
    ("Tovuti", "www.muslimwelfare.or.tz"),
]

ORG_EN = [
    ("Name", "Muslim Welfare Society of Tanzania (MWST)"),
    ("Physical address", "Nkuhungu, Dodoma, Tanzania"),
    ("Postal address", "P.O. Box 0000, Dodoma"),
    ("Telephone", "+255 769 600 102"),
    ("Email", "info@muslimwelfare.or.tz"),
    ("Website", "www.muslimwelfare.or.tz"),
]

EFFECTIVE_SW = "08 Agosti 2026"
EFFECTIVE_EN = "08 August 2026"


# ===========================================================================
#  SERA YA FARAGHA — KISWAHILI
# ===========================================================================
PRIVACY_SW = {
    "eyebrow": "Kisheria",
    "title": "Sera ya Faragha",
    "scene": "mawasiliano",
    "effective": EFFECTIVE_SW,
    "intro": "Muslim Welfare Society of Tanzania (MWST) imejitolea kulinda faragha na "
             "usiri wa taarifa binafsi tunazokabidhiwa. Sera hii inaeleza jinsi "
             "tunavyokusanya, kutumia, kuhifadhi, kulinda na kutoa taarifa zako "
             "binafsi unapotembelea tovuti yetu, unapojiandikisha kama mwanachama, "
             "mtoa huduma wa kujitolea, mfadhili au mnufaika, unapotoa michango, au "
             "unapotumia huduma zetu za mtandaoni.",
    "sections": [
        {
            "n": "1",
            "h": "Taarifa Tunazokusanya",
            "sub": [
                {
                    "h": "Taarifa binafsi",
                    "bullets": [
                        "Jina kamili",
                        "Namba ya Kitambulisho cha Taifa (pale inapohitajika)",
                        "Namba ya Uanachama",
                        "Tarehe ya kuzaliwa",
                        "Jinsia",
                        "Uraia",
                        "Kazi au shughuli",
                        "Anwani ya posta na ya makazi",
                        "Mkoa na wilaya",
                        "Namba ya simu",
                        "Barua pepe",
                        "Picha ya pasipoti",
                        "Taarifa za mtu wa kuwasiliana naye dharura",
                    ],
                },
                {
                    "h": "Taarifa za kifedha",
                    "p": ["Pale inapohitajika, tunaweza kukusanya:"],
                    "bullets": [
                        "Kumbukumbu za malipo ya uanachama",
                        "Historia ya michango",
                        "Namba za marejeo ya miamala",
                        "Uthibitisho wa malipo ya simu (mobile money)",
                        "Uthibitisho wa malipo ya benki",
                    ],
                    "note": "MWST haihifadhi taarifa za kadi yako ya benki kwenye "
                            "seva zake. Malipo yanashughulikiwa na watoa huduma "
                            "za malipo walioidhinishwa.",
                },
                {
                    "h": "Taarifa za kiufundi",
                    "p": ["Unapotumia tovuti yetu, tunaweza kukusanya kiotomatiki:"],
                    "bullets": [
                        "Anwani ya IP",
                        "Aina ya kivinjari",
                        "Taarifa za kifaa",
                        "Mfumo wa uendeshaji",
                        "Takwimu za matumizi ya tovuti",
                        "Vidakuzi (cookies) na teknolojia zinazofanana",
                    ],
                },
            ],
        },
        {
            "n": "2",
            "h": "Jinsi Tunavyotumia Taarifa Zako",
            "p": ["Taarifa zako zinaweza kutumika kwa:"],
            "bullets": [
                "Kushughulikia maombi ya uanachama.",
                "Kuthibitisha utambulisho wa mwanachama.",
                "Kutoa Namba za Uanachama na Kadi za Uanachama.",
                "Kushughulikia ada za uanachama na michango.",
                "Kutuma jarida, matangazo, SMS na barua pepe.",
                "Kuandaa matukio, mafunzo na shughuli za kujitolea.",
                "Kujibu maswali na maombi ya msaada.",
                "Kuboresha utendaji wa tovuti na uzoefu wa mtumiaji.",
                "Kuandaa ripoti za takwimu na za kitaasisi.",
                "Kutimiza matakwa ya kisheria na kikanuni.",
            ],
        },
        {
            "n": "3",
            "h": "Msingi wa Kisheria wa Kuchakata Taarifa",
            "p": ["MWST inachakata taarifa binafsi pale ambapo:"],
            "bullets": [
                "Umetoa ridhaa yako.",
                "Uchakataji ni muhimu kwa usimamizi wa uanachama wako.",
                "Uchakataji ni muhimu kutimiza wajibu wa kisheria.",
                "Uchakataji unasaidia shughuli na malengo halali ya MWST.",
            ],
        },
        {
            "n": "4",
            "h": "Kushirikisha Taarifa",
            "p": ["MWST hauzi wala haikodishi taarifa binafsi.",
                  "Tunashirikisha taarifa pale tu inapobidi, na:"],
            "bullets": [
                "Mamlaka za serikali pale sheria inapotaka.",
                "Benki na watoa huduma za malipo kwa ajili ya kushughulikia malipo.",
                "Wakaguzi wa hesabu na washauri wa kitaaluma walio chini ya wajibu wa usiri.",
                "Watoa huduma za teknolojia wanaosaidia mifumo yetu.",
                "Taasisi nyingine pale ambapo umetoa ridhaa yako.",
            ],
        },
        {
            "n": "5",
            "h": "Usalama wa Taarifa",
            "p": ["MWST inatumia hatua stahiki za kiufundi na kiutawala kulinda "
                  "taarifa binafsi, zikiwemo:"],
            "bullets": [
                "Seva salama na miunganisho iliyosimbwa (HTTPS).",
                "Akaunti za watumiaji zenye ulinzi wa nenosiri.",
                "Udhibiti wa ufikiaji kulingana na majukumu ya mtumiaji.",
                "Ufuatiliaji wa mara kwa mara wa mfumo na nakala rudufu (backups).",
                "Wajibu wa usiri kwa watumishi.",
            ],
            "note": "Ingawa hatua stahiki za usalama zinatumika, hakuna njia ya "
                    "kutuma au kuhifadhi taarifa mtandaoni iliyo salama kwa asilimia mia moja.",
        },
        {
            "n": "6",
            "h": "Muda wa Kuhifadhi Taarifa",
            "p": ["Taarifa binafsi zitahifadhiwa kwa muda unaohitajika tu ili:"],
            "bullets": [
                "Kutunza kumbukumbu za uanachama.",
                "Kutimiza wajibu wa kisheria na kifedha.",
                "Kutatua migogoro.",
                "Kusaidia utunzaji wa kumbukumbu za kihistoria na kitaasisi.",
            ],
            "note": "Taarifa zisipohitajika tena, zitafutwa kwa usalama au "
                    "kuondolewa utambulisho pale inapofaa.",
        },
        {
            "n": "7",
            "h": "Vidakuzi (Cookies)",
            "p": ["Tovuti yetu inaweza kutumia vidakuzi ili:"],
            "bullets": [
                "Kuwaweka watumiaji wameingia kwenye akaunti zao.",
                "Kukumbuka mapendeleo ya mtumiaji.",
                "Kuboresha utendaji wa tovuti.",
                "Kupima utendaji na matumizi ya tovuti.",
                "Kuimarisha usalama.",
            ],
            "note": "Unaweza kuzima vidakuzi kupitia mipangilio ya kivinjari chako, "
                    "ingawa baadhi ya vipengele vya tovuti vinaweza visifanye kazi vizuri. "
                    "Maelezo kamili yapo kwenye Sera ya Vidakuzi.",
        },
        {
            "n": "8",
            "h": "Haki Zako",
            "p": ["Kwa mujibu wa sheria husika, unaweza:"],
            "bullets": [
                "Kuomba kuona taarifa zako binafsi.",
                "Kuomba kurekebishwa kwa taarifa zisizo sahihi.",
                "Kusasisha taarifa zako za mawasiliano.",
                "Kuomba kufutwa kwa taarifa pale sheria inaporuhusu.",
                "Kuondoa ridhaa pale uchakataji unapotegemea ridhaa.",
                "Kupinga baadhi ya shughuli za uchakataji.",
                "Kuomba nakala ya taarifa ulizotoa.",
            ],
            "note": "Maombi yawasilishwe kwa kutumia anwani za mawasiliano zilizo hapa chini.",
        },
        {
            "n": "9",
            "h": "Faragha ya Watoto",
            "p": ["MWST haikusanyi kwa kujua taarifa binafsi za watoto bila ridhaa "
                  "ya mzazi, mlezi au taasisi iliyoidhinishwa pale inapohitajika."],
        },
        {
            "n": "10",
            "h": "Huduma za Watu wa Tatu",
            "p": ["Tovuti yetu inaweza kuwa na viungo vya tovuti au huduma za watu "
                  "wa tatu. MWST haiwajibiki kwa taratibu za faragha wala maudhui ya "
                  "tovuti hizo. Watumiaji wanashauriwa kusoma sera za faragha za "
                  "tovuti hizo kabla ya kutoa taarifa binafsi."],
        },
        {
            "n": "11",
            "h": "Kuhamisha Taarifa Nje ya Nchi",
            "p": ["Pale taarifa binafsi zinapochakatwa au kuhifadhiwa nje ya Tanzania "
                  "kupitia watoa huduma wanaoaminika, MWST itachukua hatua stahiki "
                  "kuhakikisha ulinzi unaofaa upo kulinda taarifa zako."],
        },
        {
            "n": "12",
            "h": "Mabadiliko ya Sera Hii",
            "p": ["MWST inaweza kusasisha Sera hii ya Faragha mara kwa mara. "
                  "Mabadiliko yoyote yatachapishwa kwenye tovuti rasmi pamoja na "
                  "tarehe mpya ya kuanza kutumika.",
                  "Kuendelea kutumia tovuti baada ya kuchapishwa kwa mabadiliko "
                  "kunamaanisha umekubali Sera iliyorekebishwa."],
        },
    ],
    "contact": {
        "n": "13", "h": "Wasiliana Nasi",
        "p": "Kama una swali, wasiwasi au ombi lolote kuhusu Sera hii ya Faragha au "
             "taarifa zako binafsi, tafadhali wasiliana nasi:",
        "lines": ORG_SW,
    },
    "consent": {
        "h": "Ridhaa",
        "p": "Kwa kujiandikisha kuwa mwanachama, kutoa mchango, kujitolea au "
             "kutumia tovuti ya MWST, unathibitisha kuwa umesoma, umeelewa na "
             "umekubali Sera hii ya Faragha.",
    },
}


# ===========================================================================
#  PRIVACY POLICY — ENGLISH
# ===========================================================================
PRIVACY_EN = {
    "eyebrow": "Legal",
    "title": "Privacy Policy",
    "scene": "mawasiliano",
    "effective": EFFECTIVE_EN,
    "intro": "The Muslim Welfare Society of Tanzania (MWST) is committed to protecting "
             "the privacy and confidentiality of the personal information entrusted to "
             "us. This Privacy Policy explains how we collect, use, store, protect, and "
             "disclose your personal information when you visit our website, register as "
             "a member, volunteer, donor, or beneficiary, make donations, or use any of "
             "our online services.",
    "sections": [
        {
            "n": "1",
            "h": "Information We Collect",
            "sub": [
                {
                    "h": "Personal information",
                    "bullets": [
                        "Full name",
                        "National Identification Number (where applicable)",
                        "Membership Number",
                        "Date of birth",
                        "Gender",
                        "Nationality",
                        "Occupation",
                        "Postal and physical address",
                        "Region and district",
                        "Mobile phone number",
                        "Email address",
                        "Passport-size photograph",
                        "Emergency contact details",
                    ],
                },
                {
                    "h": "Financial information",
                    "p": ["Where applicable, we may collect:"],
                    "bullets": [
                        "Membership payment records",
                        "Donation history",
                        "Transaction references",
                        "Mobile money payment confirmations",
                        "Bank payment confirmations",
                    ],
                    "note": "MWST does not store your bank card details on its servers. "
                            "Payments are processed through authorised payment service providers.",
                },
                {
                    "h": "Technical information",
                    "p": ["When you use our website, we may automatically collect:"],
                    "bullets": [
                        "IP address",
                        "Browser type",
                        "Device information",
                        "Operating system",
                        "Website usage statistics",
                        "Cookies and similar technologies",
                    ],
                },
            ],
        },
        {
            "n": "2",
            "h": "How We Use Your Information",
            "p": ["Your information may be used to:"],
            "bullets": [
                "Process membership applications.",
                "Verify member identity.",
                "Issue Membership Numbers and Membership Cards.",
                "Process membership subscriptions and donations.",
                "Send newsletters, notices, SMS, and email communications.",
                "Organise events, training, and volunteer activities.",
                "Respond to inquiries and support requests.",
                "Improve website performance and user experience.",
                "Prepare statistical and organisational reports.",
                "Comply with legal and regulatory obligations.",
            ],
        },
        {
            "n": "3",
            "h": "Legal Basis for Processing",
            "p": ["MWST processes personal information where:"],
            "bullets": [
                "You have provided your consent.",
                "Processing is necessary to administer your membership.",
                "Processing is necessary to fulfil legal obligations.",
                "Processing supports the legitimate activities and objectives of MWST.",
            ],
        },
        {
            "n": "4",
            "h": "Information Sharing",
            "p": ["MWST does not sell or rent personal information.",
                  "We may share information only when necessary with:"],
            "bullets": [
                "Government authorities where required by law.",
                "Banks and payment service providers for payment processing.",
                "Auditors and professional advisers under confidentiality obligations.",
                "Technology service providers supporting our systems.",
                "Other organisations where you have provided consent.",
            ],
        },
        {
            "n": "5",
            "h": "Data Security",
            "p": ["MWST implements appropriate technical and organisational measures to "
                  "protect personal information, including:"],
            "bullets": [
                "Secure servers and encrypted connections (HTTPS).",
                "Password-protected user accounts.",
                "Access controls based on user roles.",
                "Regular system monitoring and backups.",
                "Staff confidentiality obligations.",
            ],
            "note": "Although reasonable security measures are applied, no internet "
                    "transmission or electronic storage method is completely secure.",
        },
        {
            "n": "6",
            "h": "Data Retention",
            "p": ["Personal information will be retained only for as long as necessary to:"],
            "bullets": [
                "Maintain membership records.",
                "Meet legal and financial obligations.",
                "Resolve disputes.",
                "Support historical and organisational record-keeping.",
            ],
            "note": "When information is no longer required, it will be securely deleted "
                    "or anonymised where appropriate.",
        },
        {
            "n": "7",
            "h": "Cookies",
            "p": ["Our website may use cookies to:"],
            "bullets": [
                "Keep users signed in.",
                "Remember user preferences.",
                "Improve website functionality.",
                "Measure website performance and usage.",
                "Enhance security.",
            ],
            "note": "You may disable cookies through your browser settings, although some "
                    "website features may not function properly. Full details are set out "
                    "in the Cookie Policy.",
        },
        {
            "n": "8",
            "h": "Your Rights",
            "p": ["Subject to applicable law, you may:"],
            "bullets": [
                "Request access to your personal information.",
                "Request correction of inaccurate information.",
                "Update your contact details.",
                "Request deletion of information where legally permissible.",
                "Withdraw consent where processing is based on consent.",
                "Object to certain processing activities.",
                "Request a copy of information you have provided.",
            ],
            "note": "Requests should be submitted using the contact details below.",
        },
        {
            "n": "9",
            "h": "Children's Privacy",
            "p": ["MWST does not knowingly collect personal information from children "
                  "without the consent of a parent, guardian, or authorised institution "
                  "where required."],
        },
        {
            "n": "10",
            "h": "Third-Party Services",
            "p": ["Our website may contain links to third-party websites or services. "
                  "MWST is not responsible for the privacy practices or content of "
                  "external websites. Users should review the privacy policies of those "
                  "websites before providing personal information."],
        },
        {
            "n": "11",
            "h": "International Data Transfers",
            "p": ["Where personal information is processed or stored outside Tanzania "
                  "through trusted service providers, MWST will take reasonable steps to "
                  "ensure appropriate safeguards are in place to protect your information."],
        },
        {
            "n": "12",
            "h": "Changes to this Privacy Policy",
            "p": ["MWST may update this Privacy Policy from time to time. Any changes "
                  "will be published on the official website with the updated effective date.",
                  "Continued use of the website after publication of changes constitutes "
                  "acceptance of the revised Privacy Policy."],
        },
    ],
    "contact": {
        "n": "13", "h": "Contact Us",
        "p": "If you have any questions, concerns, or requests regarding this Privacy "
             "Policy or your personal information, please contact:",
        "lines": ORG_EN,
    },
    "consent": {
        "h": "Consent",
        "p": "By registering for membership, making a donation, volunteering, or using "
             "the MWST website, you acknowledge that you have read, understood, and "
             "agreed to this Privacy Policy.",
    },
}


# ===========================================================================
#  SERA YA VIDAKUZI — KISWAHILI
# ===========================================================================
COOKIES_SW = {
    "eyebrow": "Kisheria",
    "title": "Sera ya Vidakuzi",
    "scene": "mkutano",
    "effective": EFFECTIVE_SW,
    "intro": "Sera hii inaeleza jinsi Muslim Welfare Society of Tanzania (MWST) "
             "inavyotumia vidakuzi (cookies) na teknolojia zinazofanana unapotembelea "
             "au kutumia tovuti yetu. Kwa kuendelea kutumia tovuti ya MWST, unakubali "
             "matumizi ya vidakuzi kama yalivyoelezwa hapa, isipokuwa ukiyazima kupitia "
             "mipangilio ya kivinjari chako au kupitia kidirisha chetu cha mapendeleo "
             "ya vidakuzi.",
    "sections": [
        {
            "n": "1",
            "h": "Vidakuzi ni Nini?",
            "p": ["Vidakuzi ni faili ndogo za maandishi zinazowekwa kwenye kompyuta, "
                  "simu, tableti au kifaa kingine unapotembelea tovuti. Vidakuzi "
                  "husaidia tovuti kufanya kazi vizuri, kuimarisha usalama, kukumbuka "
                  "mapendeleo ya mtumiaji, na kutoa taarifa kuhusu matumizi ya tovuti.",
                  "Kwa kawaida vidakuzi havina taarifa zinazokutambua moja kwa moja, "
                  "lakini vinaweza kuunganishwa na taarifa ulizotoa kwa MWST."],
        },
        {
            "n": "2",
            "h": "Kwa Nini Tunatumia Vidakuzi",
            "p": ["MWST inatumia vidakuzi ili:"],
            "bullets": [
                "Kuhakikisha tovuti inafanya kazi ipasavyo.",
                "Kuwaweka wanachama wameingia salama kwenye akaunti zao.",
                "Kukumbuka mapendeleo ya lugha na ufikivu.",
                "Kuboresha utendaji na kasi ya tovuti.",
                "Kuchambua trafiki ya tovuti na tabia za wageni.",
                "Kulinda dhidi ya udanganyifu na ufikiaji usioidhinishwa.",
                "Kusaidia usajili wa uanachama na huduma za michango mtandaoni.",
                "Kuboresha uzoefu wa jumla wa mtumiaji.",
            ],
        },
        {
            "n": "3",
            "h": "Aina za Vidakuzi Tunavyotumia",
            "sub": [
                {
                    "h": "a) Vidakuzi vya lazima",
                    "p": ["Hivi ni muhimu kwa uendeshaji wa tovuti na kwa kawaida "
                          "haviwezi kuzimwa. Vinatumika kwa:"],
                    "bullets": [
                        "Vipindi salama vya kuingia (login sessions).",
                        "Uthibitishaji wa mtumiaji.",
                        "Usalama wa tovuti.",
                        "Kutuma fomu.",
                        "Kuhama kutoka ukurasa mmoja hadi mwingine.",
                    ],
                },
                {
                    "h": "b) Vidakuzi vya utendaji kazi",
                    "p": ["Hivi hukumbuka mapendeleo yako ili kutoa uzoefu binafsi zaidi. Mfano:"],
                    "bullets": [
                        "Lugha unayopendelea.",
                        "Uchaguzi wa mkoa.",
                        "Mipangilio ya ufikivu.",
                        "Kukumbuka taarifa ulizojaza awali pale inapofaa.",
                    ],
                },
                {
                    "h": "c) Vidakuzi vya utendaji na uchambuzi",
                    "p": ["Hivi hutusaidia kuelewa jinsi wageni wanavyotumia tovuti kwa "
                          "kukusanya taarifa zisizo na utambulisho kama vile:"],
                    "bullets": [
                        "Idadi ya wageni.",
                        "Kurasa zinazotembelewa zaidi.",
                        "Muda unaotumika kwenye kurasa.",
                        "Utendaji wa tovuti.",
                        "Ripoti za hitilafu.",
                    ],
                    "note": "Taarifa hizi husaidia MWST kuboresha huduma zake.",
                },
                {
                    "h": "d) Vidakuzi vya usalama",
                    "p": ["Hivi husaidia:"],
                    "bullets": [
                        "Kugundua shughuli za kutiliwa shaka.",
                        "Kuzuia ufikiaji usioidhinishwa.",
                        "Kulinda akaunti za wanachama.",
                        "Kudumisha uadilifu wa tovuti.",
                    ],
                },
            ],
        },
        {
            "n": "4",
            "h": "Vidakuzi vya Watu wa Tatu",
            "p": ["Baadhi ya huduma zilizounganishwa kwenye tovuti yetu zinaweza kuweka "
                  "vidakuzi vyake, zikiwemo:"],
            "bullets": [
                "Watoa huduma za malipo.",
                "Video zilizopachikwa.",
                "Ramani shirikishi.",
                "Vitufe vya kushiriki mitandao ya kijamii.",
                "Huduma za uchambuzi wa tovuti.",
            ],
            "note": "Watu hawa wa tatu wana sera zao za faragha na vidakuzi, na MWST "
                    "haidhibiti vidakuzi vyao.",
        },
        {
            "n": "5",
            "h": "Kudhibiti Vidakuzi",
            "p": ["Unaweza kuchagua:"],
            "bullets": [
                "Kukubali vidakuzi vyote.",
                "Kukataa vidakuzi visivyo vya lazima pale chaguo hilo linapopatikana.",
                "Kufuta vidakuzi vilivyohifadhiwa kwenye kifaa chako.",
                "Kusanidi kivinjari chako kuzuia vidakuzi.",
            ],
            "note": "Tafadhali fahamu kuwa kuzima baadhi ya vidakuzi kunaweza "
                    "kuathiri utendaji wa tovuti, ikiwemo kuingia kwa mwanachama, "
                    "usajili wa uanachama, michango mtandaoni, mapendeleo ya mtumiaji, "
                    "na baadhi ya vipengele shirikishi.",
        },
        {
            "n": "6",
            "h": "Muda wa Kuhifadhi Vidakuzi",
            "p": ["Baadhi ya vidakuzi hufutwa unapofunga kivinjari (vidakuzi vya kipindi), "
                  "wakati vingine hubaki kwenye kifaa chako kwa muda maalum (vidakuzi vya "
                  "kudumu) ili kukumbuka mapendeleo yako kwa ziara zijazo."],
        },
        {
            "n": "7",
            "h": "Mabadiliko ya Sera Hii",
            "p": ["MWST inaweza kusasisha Sera hii ya Vidakuzi mara kwa mara ili kuendana "
                  "na mabadiliko ya teknolojia, matakwa ya kisheria, au utendaji wa tovuti.",
                  "Toleo la hivi karibuni litapatikana daima kwenye tovuti ya MWST na "
                  "litaonyesha tarehe ya kuanza kutumika."],
        },
    ],
    "contact": {
        "n": "8", "h": "Taarifa za Mawasiliano",
        "p": "Kama una swali lolote kuhusu Sera hii ya Vidakuzi au matumizi ya vidakuzi "
             "kwenye tovuti yetu, tafadhali wasiliana nasi:",
        "lines": ORG_SW,
    },
    "consent": {
        "h": "Ridhaa",
        "p": "Kwa kuendelea kutumia tovuti ya MWST, unathibitisha kuwa vidakuzi vya "
             "lazima vinahitajika ili tovuti ifanye kazi na vitakuwa vinatumika daima, "
             "wakati vidakuzi visivyo vya lazima (vya utendaji kazi, uchambuzi na "
             "matangazo) vinatumika tu kwa ridhaa yako. Unaweza kukubali au kukataa "
             "vidakuzi visivyo vya lazima kupitia kidirisha cha mapendeleo ya vidakuzi, "
             "au kudhibiti na kuondoa ridhaa yako wakati wowote kwa kubadilisha "
             "mipangilio ya kivinjari chako au kurudi kwenye kidirisha hicho.",
    },
}


# ===========================================================================
#  COOKIE POLICY — ENGLISH
# ===========================================================================
COOKIES_EN = {
    "eyebrow": "Legal",
    "title": "Cookie Policy",
    "scene": "mkutano",
    "effective": EFFECTIVE_EN,
    "intro": "This Cookie Policy explains how the Muslim Welfare Society of Tanzania "
             "(MWST) uses cookies and similar technologies when you visit or use our "
             "website. By continuing to use the MWST website, you agree to the use of "
             "cookies as described in this Policy, unless you disable them through your "
             "browser settings or our cookie preference panel.",
    "sections": [
        {
            "n": "1",
            "h": "What Are Cookies?",
            "p": ["Cookies are small text files that are placed on your computer, "
                  "smartphone, tablet, or other device when you visit a website. Cookies "
                  "help websites function efficiently, improve security, remember user "
                  "preferences, and provide information about website usage.",
                  "Cookies do not generally contain information that directly identifies "
                  "you, but they may be linked to information you provide to MWST."],
        },
        {
            "n": "2",
            "h": "Why We Use Cookies",
            "p": ["MWST uses cookies to:"],
            "bullets": [
                "Ensure the website functions properly.",
                "Keep members securely logged into their accounts.",
                "Remember language and accessibility preferences.",
                "Improve website performance and speed.",
                "Analyse website traffic and visitor behaviour.",
                "Protect against fraud and unauthorised access.",
                "Support online membership registration and donation services.",
                "Enhance the overall user experience.",
            ],
        },
        {
            "n": "3",
            "h": "Types of Cookies We Use",
            "sub": [
                {
                    "h": "a) Strictly necessary cookies",
                    "p": ["These cookies are essential for the operation of the website "
                          "and cannot normally be disabled. They are used for:"],
                    "bullets": [
                        "Secure login sessions.",
                        "User authentication.",
                        "Website security.",
                        "Form submissions.",
                        "Navigation between pages.",
                    ],
                },
                {
                    "h": "b) Functional cookies",
                    "p": ["These cookies remember your preferences to provide a more "
                          "personalised experience. Examples include:"],
                    "bullets": [
                        "Preferred language.",
                        "Region selection.",
                        "Accessibility settings.",
                        "Remembering previously entered information where appropriate.",
                    ],
                },
                {
                    "h": "c) Performance and analytics cookies",
                    "p": ["These cookies help us understand how visitors use our website "
                          "by collecting anonymous information such as:"],
                    "bullets": [
                        "Number of visitors.",
                        "Most visited pages.",
                        "Time spent on pages.",
                        "Website performance.",
                        "Error reports.",
                    ],
                    "note": "This information helps MWST improve its services.",
                },
                {
                    "h": "d) Security cookies",
                    "p": ["These cookies help:"],
                    "bullets": [
                        "Detect suspicious activity.",
                        "Prevent unauthorised access.",
                        "Protect member accounts.",
                        "Maintain website integrity.",
                    ],
                },
            ],
        },
        {
            "n": "4",
            "h": "Third-Party Cookies",
            "p": ["Some services integrated into our website may place their own cookies, "
                  "including:"],
            "bullets": [
                "Payment service providers.",
                "Embedded videos.",
                "Interactive maps.",
                "Social media sharing tools.",
                "Website analytics services.",
            ],
            "note": "These third parties have their own privacy and cookie policies, and "
                    "MWST does not control their cookies.",
        },
        {
            "n": "5",
            "h": "Managing Cookies",
            "p": ["You may choose to:"],
            "bullets": [
                "Accept all cookies.",
                "Reject non-essential cookies where such options are available.",
                "Delete cookies already stored on your device.",
                "Configure your browser to block cookies.",
            ],
            "note": "Please note that disabling certain cookies may affect website "
                    "functionality, including member login, membership registration, "
                    "online donations, user preferences, and some interactive features.",
        },
        {
            "n": "6",
            "h": "Cookie Retention",
            "p": ["Some cookies are deleted when you close your browser (session cookies), "
                  "while others remain on your device for a specified period (persistent "
                  "cookies) to remember your preferences for future visits."],
        },
        {
            "n": "7",
            "h": "Updates to This Cookie Policy",
            "p": ["MWST may update this Cookie Policy from time to time to reflect changes "
                  "in technology, legal requirements, or website functionality.",
                  "The latest version will always be available on the MWST website and "
                  "will indicate the effective date."],
        },
    ],
    "contact": {
        "n": "8", "h": "Contact Information",
        "p": "If you have any questions regarding this Cookie Policy or the use of "
             "cookies on our website, please contact:",
        "lines": ORG_EN,
    },
    "consent": {
        "h": "Consent",
        "p": "By continuing to use the MWST website, you acknowledge that strictly "
             "necessary cookies are required for the website to function and will always "
             "be active, while non-essential cookies (such as functional, analytics, and "
             "marketing cookies) are only used with your consent. You may accept or reject "
             "non-essential cookies through the cookie preference panel on our website, or "
             "manage and withdraw your consent at any time by adjusting your browser "
             "settings or revisiting that panel.",
    },
}


# ---------------------------------------------------------------------------
#  API
# ---------------------------------------------------------------------------
def privacy(lang="sw"):
    """Sera ya Faragha kwa lugha husika."""
    return PRIVACY_EN if str(lang).startswith("en") else PRIVACY_SW


def cookies(lang="sw"):
    """Sera ya Vidakuzi kwa lugha husika."""
    return COOKIES_EN if str(lang).startswith("en") else COOKIES_SW
