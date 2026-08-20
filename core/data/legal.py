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
    ("Jina", "Muslim Welfare Society of Tanzania (MUWESTA)"),
    ("Anwani ya makazi", "Shariff PBZ House, Kiwanja Na. 4, Kitalu M, Ghorofa ya Tatu, S.L.P 450, Dodoma, Tanzania"),
    ("Anwani ya posta", "S.L.P. 0000, Dodoma"),
    ("Simu", "+255 769 600 102"),
    ("Barua pepe", "info@muslimwelfare.or.tz"),
    ("Tovuti", "https://mwiso.onrender.com"),
]

ORG_EN = [
    ("Name", "Muslim Welfare Society of Tanzania (MUWESTA)"),
    ("Physical address", "Shariff PBZ House, Plot No. 4, Block M, Third Floor, P.O. Box 450, Dodoma, Tanzania"),
    ("Postal address", "P.O. Box 0000, Dodoma"),
    ("Telephone", "+255 769 600 102"),
    ("Email", "info@muslimwelfare.or.tz"),
    ("Website", "https://mwiso.onrender.com"),
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
    "intro": "Muslim Welfare Society of Tanzania (MUWESTA) imejitolea kulinda faragha na "
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
                    "note": "MUWESTA haihifadhi taarifa za kadi yako ya benki kwenye "
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
            "p": ["MUWESTA inachakata taarifa binafsi pale ambapo:"],
            "bullets": [
                "Umetoa ridhaa yako.",
                "Uchakataji ni muhimu kwa usimamizi wa uanachama wako.",
                "Uchakataji ni muhimu kutimiza wajibu wa kisheria.",
                "Uchakataji unasaidia shughuli na malengo halali ya MUWESTA.",
            ],
        },
        {
            "n": "4",
            "h": "Kushirikisha Taarifa",
            "p": ["MUWESTA hauzi wala haikodishi taarifa binafsi.",
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
            "p": ["MUWESTA inatumia hatua stahiki za kiufundi na kiutawala kulinda "
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
            "p": ["MUWESTA haikusanyi kwa kujua taarifa binafsi za watoto bila ridhaa "
                  "ya mzazi, mlezi au taasisi iliyoidhinishwa pale inapohitajika."],
        },
        {
            "n": "10",
            "h": "Huduma za Watu wa Tatu",
            "p": ["Tovuti yetu inaweza kuwa na viungo vya tovuti au huduma za watu "
                  "wa tatu. MUWESTA haiwajibiki kwa taratibu za faragha wala maudhui ya "
                  "tovuti hizo. Watumiaji wanashauriwa kusoma sera za faragha za "
                  "tovuti hizo kabla ya kutoa taarifa binafsi."],
        },
        {
            "n": "11",
            "h": "Kuhamisha Taarifa Nje ya Nchi",
            "p": ["Pale taarifa binafsi zinapochakatwa au kuhifadhiwa nje ya Tanzania "
                  "kupitia watoa huduma wanaoaminika, MUWESTA itachukua hatua stahiki "
                  "kuhakikisha ulinzi unaofaa upo kulinda taarifa zako."],
        },
        {
            "n": "12",
            "h": "Mabadiliko ya Sera Hii",
            "p": ["MUWESTA inaweza kusasisha Sera hii ya Faragha mara kwa mara. "
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
             "kutumia tovuti ya MUWESTA, unathibitisha kuwa umesoma, umeelewa na "
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
    "intro": "The Muslim Welfare Society of Tanzania (MUWESTA) is committed to protecting "
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
                    "note": "MUWESTA does not store your bank card details on its servers. "
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
            "p": ["MUWESTA processes personal information where:"],
            "bullets": [
                "You have provided your consent.",
                "Processing is necessary to administer your membership.",
                "Processing is necessary to fulfil legal obligations.",
                "Processing supports the legitimate activities and objectives of MUWESTA.",
            ],
        },
        {
            "n": "4",
            "h": "Information Sharing",
            "p": ["MUWESTA does not sell or rent personal information.",
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
            "p": ["MUWESTA implements appropriate technical and organisational measures to "
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
            "p": ["MUWESTA does not knowingly collect personal information from children "
                  "without the consent of a parent, guardian, or authorised institution "
                  "where required."],
        },
        {
            "n": "10",
            "h": "Third-Party Services",
            "p": ["Our website may contain links to third-party websites or services. "
                  "MUWESTA is not responsible for the privacy practices or content of "
                  "external websites. Users should review the privacy policies of those "
                  "websites before providing personal information."],
        },
        {
            "n": "11",
            "h": "International Data Transfers",
            "p": ["Where personal information is processed or stored outside Tanzania "
                  "through trusted service providers, MUWESTA will take reasonable steps to "
                  "ensure appropriate safeguards are in place to protect your information."],
        },
        {
            "n": "12",
            "h": "Changes to this Privacy Policy",
            "p": ["MUWESTA may update this Privacy Policy from time to time. Any changes "
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
             "the MUWESTA website, you acknowledge that you have read, understood, and "
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
    "intro": "Sera hii inaeleza jinsi Muslim Welfare Society of Tanzania (MUWESTA) "
             "inavyotumia vidakuzi (cookies) na teknolojia zinazofanana unapotembelea "
             "au kutumia tovuti yetu. Kwa kuendelea kutumia tovuti ya MUWESTA, unakubali "
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
                  "lakini vinaweza kuunganishwa na taarifa ulizotoa kwa MUWESTA."],
        },
        {
            "n": "2",
            "h": "Kwa Nini Tunatumia Vidakuzi",
            "p": ["MUWESTA inatumia vidakuzi ili:"],
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
                    "note": "Taarifa hizi husaidia MUWESTA kuboresha huduma zake.",
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
            "note": "Watu hawa wa tatu wana sera zao za faragha na vidakuzi, na MUWESTA "
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
            "p": ["MUWESTA inaweza kusasisha Sera hii ya Vidakuzi mara kwa mara ili kuendana "
                  "na mabadiliko ya teknolojia, matakwa ya kisheria, au utendaji wa tovuti.",
                  "Toleo la hivi karibuni litapatikana daima kwenye tovuti ya MUWESTA na "
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
        "p": "Kwa kuendelea kutumia tovuti ya MUWESTA, unathibitisha kuwa vidakuzi vya "
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
             "(MUWESTA) uses cookies and similar technologies when you visit or use our "
             "website. By continuing to use the MUWESTA website, you agree to the use of "
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
                  "you, but they may be linked to information you provide to MUWESTA."],
        },
        {
            "n": "2",
            "h": "Why We Use Cookies",
            "p": ["MUWESTA uses cookies to:"],
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
                    "note": "This information helps MUWESTA improve its services.",
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
                    "MUWESTA does not control their cookies.",
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
            "p": ["MUWESTA may update this Cookie Policy from time to time to reflect changes "
                  "in technology, legal requirements, or website functionality.",
                  "The latest version will always be available on the MUWESTA website and "
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
        "p": "By continuing to use the MUWESTA website, you acknowledge that strictly "
             "necessary cookies are required for the website to function and will always "
             "be active, while non-essential cookies (such as functional, analytics, and "
             "marketing cookies) are only used with your consent. You may accept or reject "
             "non-essential cookies through the cookie preference panel on our website, or "
             "manage and withdraw your consent at any time by adjusting your browser "
             "settings or revisiting that panel.",
    },
}


# ===========================================================================
#  MASHARTI YA HUDUMA — KISWAHILI
# ===========================================================================
TERMS_SW = {
    "eyebrow": "Kisheria",
    "title": "Masharti ya Huduma",
    "scene": "mkutano",
    "effective": EFFECTIVE_SW,
    "intro": "Masharti haya yanaeleza makubaliano kati yako na MUWESTA unapotumia "
             "tovuti yetu, unapojiunga kama mwanachama, unapotoa michango au "
             "unapotumia huduma zetu za mtandaoni. "
             "Tafadhali yasome kwa makini kabla ya kutumia huduma zetu. "
             "Kwa kuendelea kutumia mfumo huu, unakubali kufungwa na masharti haya.",
    "sections": [
        {
            "n": "1",
            "h": "Kuhusu MUWESTA",
            "p": [
                "MUWESTA ni jumuiya ya hisani isiyo ya kiserikali iliyosajiliwa nchini "
                "Tanzania, inayofanya kazi za ustawi wa jamii katika elimu, afya, maji, "
                "malezi ya yatima na wajane, misaada ya dharura na maendeleo ya jamii.",
                "Shughuli zetu zinaongozwa na Katiba ya MUWESTA pamoja na sheria za "
                "Tanzania, ikiwemo Sheria ya Mashirika Yasiyo ya Kiserikali. Pale "
                "masharti haya yanapotofautiana na Katiba ya jumuiya, Katiba ndiyo "
                "yenye kauli ya mwisho.",
            ],
        },
        {
            "n": "2",
            "h": "Uanachama",
            "p": [
                "Uanachama ni wa hiari na uko wazi kwa mtu yeyote anayekubali malengo "
                "na Katiba ya MUWESTA.",
            ],
            "sub": [
                {
                    "h": "Jinsi uanachama unavyoanza",
                    "bullets": [
                        "Unajaza fomu ya maombi mtandaoni na kupewa namba ya ombi.",
                        "Afisa wa MUWESTA anahakiki taarifa ulizotoa.",
                        "Ombi likihakikiwa, unalipa ada ya usajili na ada ya kipindi.",
                        "Malipo yakithibitishwa, unapewa namba ya uanachama, kadi ya "
                        "kidijitali na taarifa za kuingia kwenye mfumo.",
                    ],
                },
                {
                    "h": "Muda wa uanachama",
                    "bullets": [
                        "Kipindi kimoja cha uanachama ni MIAKA MITATU.",
                        "Utakumbushwa kabla kipindi hakijaisha ili uweze kulipia tena.",
                        "Kipindi kikiisha bila malipo, uanachama unabaki umesimama "
                        "hadi utakapolipia — huufuti, lakini huwezi kutumia huduma "
                        "za wanachama katika kipindi hicho.",
                    ],
                },
                {
                    "h": "Wajibu wako kama mwanachama",
                    "bullets": [
                        "Kutoa taarifa za kweli na kuzisasisha zinapobadilika.",
                        "Kulipa ada kwa wakati.",
                        "Kuzingatia Katiba, kanuni na maadili ya jumuiya.",
                        "Kutunza siri ya taarifa za kuingia; usimpe mtu mwingine.",
                        "Kutotumia jina la MUWESTA kwa manufaa binafsi bila idhini.",
                    ],
                },
            ],
        },
        {
            "n": "3",
            "h": "Michango na Malipo",
            "p": [
                "Michango yote inayotolewa kupitia mfumo huu ni ya hiari na haina "
                "malipo ya kurudishwa isipokuwa kwa mujibu wa kifungu cha 4.",
            ],
            "sub": [
                {
                    "h": "Njia za malipo",
                    "p": [
                        "Malipo yanashughulikiwa na watoa huduma wa nje: Selcom kwa "
                        "malipo ya simu, na Pesapal kwa kadi za benki. Namba yako ya "
                        "kadi au PIN yako ya mtandao HAVIPITI wala HAVIHIFADHIWI "
                        "kwenye mifumo ya MUWESTA hata kidogo.",
                        "Malipo yanahesabiwa kuwa yamekamilika pale tu mtoa huduma "
                        "atakapothibitisha. Kupokea ujumbe wa kutuma pesa peke yake "
                        "hakuthibitishi kuwa MUWESTA imepokea.",
                    ],
                },
                {
                    "h": "Matumizi ya michango",
                    "bullets": [
                        "Mchango unaotolewa kwa aina fulani hutumika kwa aina hiyo.",
                        "Zakat huhifadhiwa kwenye akaunti yake tofauti na kutolewa "
                        "kwa mujibu wa Sharia.",
                        "Kama mradi utakamilika au kusitishwa, MUWESTA inaweza "
                        "kuelekeza kilichobaki kwenye shughuli inayofanana nayo, na "
                        "hilo litatangazwa kwenye ripoti zetu.",
                    ],
                },
                {
                    "h": "Risiti",
                    "p": [
                        "Kila mchango uliothibitishwa hupata namba ya risiti. Hifadhi "
                        "namba hiyo — ndiyo uthibitisho wako wa malipo.",
                    ],
                },
            ],
        },
        {
            "n": "4",
            "h": "Kurudishiwa Fedha",
            "p": [
                "Michango ya hiari kwa kawaida hairudishwi, kwa sababu hutumika mara "
                "moja kwa shughuli za ustawi.",
            ],
            "bullets": [
                "Kama umelipa mara mbili kwa bahati mbaya, wasiliana nasi ndani ya "
                "siku 14 na tutarudisha kiasi cha ziada.",
                "Kama malipo yamefanyika kwa kosa la kiufundi la mfumo wetu, "
                "tutarudisha kiasi chote.",
                "Ada ya usajili wa uanachama hairudishwi baada ya namba ya uanachama "
                "na kadi kutolewa.",
            ],
            "note": "Maombi ya kurudishiwa fedha yanatumwa kwa barua pepe yetu "
                    "yakiwa na namba ya risiti. Tunajibu ndani ya siku 14 za kazi.",
        },
        {
            "n": "5",
            "h": "Pointi za MUWESTA",
            "p": [
                "Mfumo wa pointi ni njia ya kutambua ushiriki na mchango wako kwenye "
                "jumuiya. Pointi hupatikana kwa michango, kulipa ada na kushiriki "
                "shughuli za jumuiya.",
            ],
            "bullets": [
                "Pointi SI FEDHA. Hazina thamani ya kifedha, haziwezi kubadilishwa "
                "kuwa pesa taslimu, wala haziwezi kuhamishwa kwa mtu mwingine.",
                "Pointi hazidaiwi kama haki. Ni utambuzi wa hiari wa jumuiya.",
                "Kiwango cha mwanachama huhesabiwa kwa pointi za miaka mitatu "
                "iliyopita; pointi za maisha huhifadhiwa kwa ajili ya vyeti na heshima.",
                "MUWESTA inaweza kurekebisha pointi zilizotolewa kimakosa, na kila "
                "marekebisho huachwa kwenye kumbukumbu.",
                "Viwango na kanuni za pointi vinaweza kubadilishwa na Bodi, na "
                "mabadiliko hutangazwa kabla ya kuanza kutumika.",
            ],
        },
        {
            "n": "6",
            "h": "Matumizi Yanayokubalika",
            "p": ["Unapotumia mfumo huu, unakubali kutofanya yafuatayo:"],
            "bullets": [
                "Kutoa taarifa za uongo au kutumia kitambulisho cha mtu mwingine.",
                "Kujaribu kuingia kwenye akaunti au sehemu za mfumo usizoruhusiwa.",
                "Kuvuruga, kuharibu au kupakia programu hasidi kwenye mfumo.",
                "Kutumia mfumo kwa utapeli, utakatishaji fedha au shughuli haramu.",
                "Kukusanya taarifa za wanachama wengine bila idhini yao.",
                "Kutumia mfumo kwa njia inayokiuka maadili ya Kiislamu au sheria "
                "za Tanzania.",
            ],
            "note": "Tukibaini ukiukwaji, tunaweza kusimamisha akaunti yako, "
                    "kufuta uanachama, na pale inapohitajika kutoa taarifa kwa "
                    "mamlaka husika.",
        },
        {
            "n": "7",
            "h": "Akaunti Yako",
            "bullets": [
                "Wewe ndiye mwenye jukumu la kutunza siri ya nenosiri lako.",
                "Ubadilishe nenosiri la muda mara tu unapoingia kwa mara ya kwanza.",
                "Tuarifu haraka ukishuku kuwa mtu amepata akaunti yako.",
                "Vitendo vyote vinavyofanywa kwa akaunti yako vinahesabiwa kuwa "
                "vimefanywa na wewe, isipokuwa umeturifu mapema kuhusu tatizo.",
            ],
        },
        {
            "n": "8",
            "h": "Upatikanaji wa Huduma",
            "p": [
                "Tunajitahidi kuhakikisha mfumo unapatikana wakati wote, lakini "
                "hatuwezi kuahidi utakuwa hauna hitilafu au kukatika.",
                "Huduma inaweza kusimama kwa muda kwa ajili ya matengenezo, "
                "kuboreshwa, au kwa sababu zisizo ndani ya uwezo wetu kama vile "
                "kukatika kwa mtandao au huduma za watoa huduma wa malipo.",
            ],
        },
        {
            "n": "9",
            "h": "Umiliki wa Maudhui",
            "p": [
                "Nembo, jina, muundo na maudhui ya tovuti hii ni mali ya MUWESTA. "
                "Hayaruhusiwi kutumiwa kibiashara bila idhini ya maandishi.",
                "Taarifa unazoweka wewe (jina, picha, ujumbe) zinabaki zako. "
                "Unatupa ruhusa ya kuzitumia kwa ajili ya kuendesha huduma "
                "ulizoziomba, kwa mujibu wa Sera yetu ya Faragha.",
            ],
        },
        {
            "n": "10",
            "h": "Ulinzi wa Taarifa Binafsi",
            "p": [
                "Ukusanyaji na matumizi ya taarifa zako binafsi yanaelezwa kwenye "
                "Sera yetu ya Faragha, ambayo ni sehemu ya masharti haya. "
                "Tunazingatia Sheria ya Ulinzi wa Taarifa Binafsi ya mwaka 2022 "
                "ya Tanzania.",
            ],
        },
        {
            "n": "11",
            "h": "Kikomo cha Dhima",
            "p": [
                "MUWESTA haiwajibiki kwa hasara isiyo ya moja kwa moja itokanayo na "
                "kutopatikana kwa mfumo, kucheleweshwa kwa malipo na mtoa huduma, "
                "au kukatika kwa mtandao.",
                "Hakuna kifungu hapa kinachoondoa dhima ambayo, kwa mujibu wa sheria "
                "ya Tanzania, haiwezi kuondolewa — ikiwemo dhima kwa udanganyifu au "
                "uzembe mkubwa.",
            ],
        },
        {
            "n": "12",
            "h": "Kusitisha Huduma",
            "bullets": [
                "Unaweza kujiondoa kwenye uanachama wakati wowote kwa kutuandikia.",
                "Tunaweza kusimamisha au kufuta akaunti yako ukikiuka masharti haya "
                "au Katiba ya jumuiya.",
                "Kufutwa kwa uanachama hakukurudishii ada uliyokwisha lipa.",
                "Taarifa zako zitahifadhiwa kwa muda unaotakiwa na sheria hata baada "
                "ya kusitisha, kama inavyoelezwa kwenye Sera ya Faragha.",
            ],
        },
        {
            "n": "13",
            "h": "Mabadiliko ya Masharti",
            "p": [
                "Tunaweza kubadilisha masharti haya mara kwa mara. Toleo jipya "
                "litawekwa kwenye ukurasa huu likiwa na tarehe ya kuanza kutumika.",
                "Mabadiliko makubwa yatatangazwa kwa wanachama kwa barua pepe au "
                "ujumbe kwenye mfumo kabla hayajaanza kutumika.",
                "Kuendelea kutumia mfumo baada ya mabadiliko kunahesabiwa kama "
                "kukubali toleo jipya.",
            ],
        },
        {
            "n": "14",
            "h": "Sheria Inayotumika na Utatuzi wa Migogoro",
            "p": [
                "Masharti haya yanaongozwa na sheria za Jamhuri ya Muungano wa "
                "Tanzania.",
                "Mgogoro wowote utajaribiwa kutatuliwa kwa mazungumzo ya kirafiki "
                "kwanza. Ikishindikana, utapelekwa kwenye mahakama zenye mamlaka "
                "nchini Tanzania.",
            ],
        },
    ],
    "contact": {
        "n": "15",
        "h": "Taarifa za Mawasiliano",
        "p": "Kama una swali lolote kuhusu masharti haya, tafadhali wasiliana nasi:",
        "lines": ORG_SW,
    },
    "consent": {
        "h": "Kukubali Masharti",
        "p": "Kwa kujisajili kama mwanachama, kutoa mchango, au kuendelea kutumia "
             "tovuti ya MUWESTA, unathibitisha kuwa umeyasoma masharti haya, "
             "umeyaelewa, na unakubali kufungwa nayo pamoja na Sera yetu ya "
             "Faragha na Sera ya Vidakuzi.",
    },
}

# ===========================================================================
#  TERMS OF SERVICE — ENGLISH
# ===========================================================================
TERMS_EN = {
    "eyebrow": "Legal",
    "title": "Terms of Service",
    "scene": "mkutano",
    "effective": EFFECTIVE_EN,
    "intro": "These terms set out the agreement between you and MUWESTA when you "
             "use our website, join as a member, make a contribution, or use our "
             "online services. Please read "
             "them carefully before using our services. By continuing to use this "
             "system, you agree to be bound by these terms.",
    "sections": [
        {
            "n": "1",
            "h": "About MUWESTA",
            "p": [
                "MUWESTA is a non-governmental charitable society registered in "
                "Tanzania, working in community welfare across education, health, "
                "water, care for orphans and widows, emergency relief and community "
                "development.",
                "Our activities are governed by the MUWESTA Constitution together "
                "with the laws of Tanzania, including the Non-Governmental "
                "Organisations Act. Where these terms differ from the Constitution, "
                "the Constitution prevails.",
            ],
        },
        {
            "n": "2",
            "h": "Membership",
            "p": [
                "Membership is voluntary and open to anyone who accepts the aims and "
                "Constitution of MUWESTA.",
            ],
            "sub": [
                {
                    "h": "How membership begins",
                    "bullets": [
                        "You complete an application form online and receive an "
                        "application number.",
                        "A MUWESTA officer verifies the details you provided.",
                        "Once verified, you pay the registration fee and the term fee.",
                        "Once payment is confirmed, you receive your membership "
                        "number, digital card and login details.",
                    ],
                },
                {
                    "h": "Length of membership",
                    "bullets": [
                        "One membership term is THREE YEARS.",
                        "You will be reminded before the term ends so you can renew.",
                        "If the term ends without payment, membership is suspended "
                        "rather than cancelled — but member services are unavailable "
                        "during that period.",
                    ],
                },
                {
                    "h": "Your responsibilities as a member",
                    "bullets": [
                        "Give truthful information and keep it up to date.",
                        "Pay your fees on time.",
                        "Observe the Constitution, rules and ethics of the society.",
                        "Keep your login details private; do not share them.",
                        "Do not use the MUWESTA name for personal gain without "
                        "permission.",
                    ],
                },
            ],
        },
        {
            "n": "3",
            "h": "Contributions and Payments",
            "p": [
                "All contributions made through this system are voluntary and are "
                "non-refundable except as set out in section 4.",
            ],
            "sub": [
                {
                    "h": "Payment methods",
                    "p": [
                        "Payments are handled by third-party providers: Selcom for "
                        "phone payments and Pesapal for bank cards. Your card number "
                        "and your mobile money PIN never pass through, and are never "
                        "stored on, MUWESTA systems.",
                        "A payment counts as complete only once the provider confirms "
                        "it. Receiving a transfer message on your phone alone does not "
                        "confirm that MUWESTA has received the funds.",
                    ],
                },
                {
                    "h": "Use of contributions",
                    "bullets": [
                        "A contribution given for a particular purpose is used for "
                        "that purpose.",
                        "Zakat is held in its own separate account and disbursed in "
                        "accordance with Sharia.",
                        "If a project is completed or discontinued, MUWESTA may "
                        "direct any balance to similar work, and this will be "
                        "disclosed in our reports.",
                    ],
                },
                {
                    "h": "Receipts",
                    "p": [
                        "Every confirmed contribution receives a receipt number. Keep "
                        "that number — it is your proof of payment.",
                    ],
                },
            ],
        },
        {
            "n": "4",
            "h": "Refunds",
            "p": [
                "Voluntary contributions are generally not refunded, because they are "
                "put to welfare use promptly.",
            ],
            "bullets": [
                "If you paid twice by mistake, contact us within 14 days and we will "
                "refund the duplicate amount.",
                "If a payment occurred because of a technical fault on our side, we "
                "will refund it in full.",
                "Membership registration fees are not refunded once the membership "
                "number and card have been issued.",
            ],
            "note": "Refund requests should be emailed to us with the receipt number. "
                    "We respond within 14 working days.",
        },
        {
            "n": "5",
            "h": "MUWESTA Points",
            "p": [
                "The points system is a way of recognising your participation and "
                "contribution to the society. Points are earned through "
                "contributions, fee payments and taking part in community activities.",
            ],
            "bullets": [
                "Points ARE NOT MONEY. They hold no monetary value, cannot be "
                "converted to cash, and cannot be transferred to another person.",
                "Points are not claimable as a right. They are a voluntary form of "
                "recognition by the society.",
                "A member's level is calculated from points earned in the last three "
                "years; lifetime points are retained for certificates and honours.",
                "MUWESTA may reverse points awarded in error, and every reversal is "
                "kept on record.",
                "Point rates and rules may be changed by the Board, and changes are "
                "announced before they take effect.",
            ],
        },
        {
            "n": "6",
            "h": "Acceptable Use",
            "p": ["In using this system, you agree not to do any of the following:"],
            "bullets": [
                "Provide false information or use another person's identity.",
                "Attempt to access accounts or areas of the system you are not "
                "permitted to use.",
                "Disrupt, damage or upload malicious software to the system.",
                "Use the system for fraud, money laundering or any unlawful activity.",
                "Collect other members' information without their consent.",
                "Use the system in a way that breaches Islamic ethics or the laws of "
                "Tanzania.",
            ],
            "note": "Where we identify a breach, we may suspend your account, "
                    "terminate membership, and where necessary report the matter to "
                    "the relevant authorities.",
        },
        {
            "n": "7",
            "h": "Your Account",
            "bullets": [
                "You are responsible for keeping your password confidential.",
                "Change your temporary password as soon as you first log in.",
                "Tell us promptly if you suspect someone has accessed your account.",
                "All activity carried out under your account is treated as your own, "
                "unless you have notified us of a problem beforehand.",
            ],
        },
        {
            "n": "8",
            "h": "Service Availability",
            "p": [
                "We work to keep the system available at all times, but we cannot "
                "promise it will be free of faults or interruption.",
                "Service may pause for maintenance or improvement, or for reasons "
                "outside our control such as network outages or payment provider "
                "downtime.",
            ],
        },
        {
            "n": "9",
            "h": "Ownership of Content",
            "p": [
                "The logo, name, design and content of this website belong to "
                "MUWESTA. They may not be used commercially without written "
                "permission.",
                "Information you provide (your name, photo, messages) remains yours. "
                "You give us permission to use it to run the services you have "
                "requested, in line with our Privacy Policy.",
            ],
        },
        {
            "n": "10",
            "h": "Protection of Personal Data",
            "p": [
                "How we collect and use your personal information is set out in our "
                "Privacy Policy, which forms part of these terms. We observe "
                "Tanzania's Personal Data Protection Act, 2022.",
            ],
        },
        {
            "n": "11",
            "h": "Limitation of Liability",
            "p": [
                "MUWESTA is not liable for indirect loss arising from the system "
                "being unavailable, from delays by a payment provider, or from "
                "network outages.",
                "Nothing here excludes liability that cannot be excluded under "
                "Tanzanian law, including liability for fraud or gross negligence.",
            ],
        },
        {
            "n": "12",
            "h": "Ending the Service",
            "bullets": [
                "You may withdraw from membership at any time by writing to us.",
                "We may suspend or close your account if you breach these terms or "
                "the Constitution of the society.",
                "Termination of membership does not entitle you to a refund of fees "
                "already paid.",
                "Your information will be retained for as long as the law requires "
                "even after termination, as explained in the Privacy Policy.",
            ],
        },
        {
            "n": "13",
            "h": "Changes to These Terms",
            "p": [
                "We may amend these terms from time to time. A new version will be "
                "published on this page with the date it takes effect.",
                "Significant changes will be announced to members by email or by a "
                "message in the system before they take effect.",
                "Continuing to use the system after a change means you accept the "
                "new version.",
            ],
        },
        {
            "n": "14",
            "h": "Governing Law and Dispute Resolution",
            "p": [
                "These terms are governed by the laws of the United Republic of "
                "Tanzania.",
                "Any dispute will first be addressed through good-faith discussion. "
                "If that does not resolve it, the matter will be referred to the "
                "courts of competent jurisdiction in Tanzania.",
            ],
        },
    ],
    "contact": {
        "n": "15",
        "h": "Contact Information",
        "p": "If you have any question about these terms, please contact us:",
        "lines": ORG_EN,
    },
    "consent": {
        "h": "Acceptance of Terms",
        "p": "By registering as a member, making a contribution, or continuing to "
             "use the MUWESTA website, you confirm that you have read these terms, "
             "understood them, and agree to be bound by them together with our "
             "Privacy Policy and Cookie Policy.",
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


def terms(lang="sw"):
    """Masharti ya Huduma kwa lugha husika."""
    return TERMS_EN if str(lang).startswith("en") else TERMS_SW
