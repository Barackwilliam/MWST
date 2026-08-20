"""
Nukuu za Qur'an na Hadith kuhusu kutoa — zinazoteleza kwenye ukurasa wa mwanzo.

Maandishi ya Kiarabu yamewekwa kama yalivyo. Yasibadilishwe bila kuthibitisha
na mtaalamu; kosa dogo la herufi kwenye aya linabadilisha maana.

`kind` inaamua lebo inayoonyeshwa: "quran" au "hadith".

`image` ni jina la poster iliyoko `static/img/nukuu/`. Kila nukuu ina faili
tatu: `<jina>.webp` (kubwa, inaonekana ikibofywa), `<jina>-sm.webp` na
`<jina>-sm.jpg` (ndogo, ndizo zinazopakiwa kwenye slider).

MUHIMU: posters zenyewe zina maandishi yote ndani yake, lakini maandishi
hayo hayasomeki kwenye simu wala hayatafsiriwi. Ndiyo maana `text` na
`text_en` zinabaki hapa — ndizo mtu anazosoma; poster ni nyongeza ya
kuangalia, si mbadala.
"""

VERSES = [
    {
        "kind": "quran",
        "label": "Qur'an",
        "source": "Surat Aal-Imran 3:92",
        "arabic": "لَن تَنَالُوا الْبِرَّ حَتَّىٰ تُنفِقُوا مِمَّا تُحِبُّونَ ۚ "
                  "وَمَا تُنفِقُوا مِن شَيْءٍ فَإِنَّ اللَّهَ بِهِ عَلِيمٌ",
        "text": "Hamtaweza kuufikia wema mpaka mtumie katika vile mnavyovipenda. "
                "Na chochote mtakachokitoa, basi hakika Mwenyezi Mungu anakijua.",
        "text_en": "You will never attain righteousness until you spend from that "
                   "which you love. And whatever you spend, indeed Allah knows it.",
        "ref": "(Qur'an 3:92)",
        "image": "aali-imran",
        "alt": "Aya ya Aali Imran 3:92 pamoja na huduma za MUWESTA",
        "alt_en": "Qur'an 3:92 alongside MUWESTA's areas of service",
    },
    {
        "kind": "hadith",
        "label": "Hadith",
        "source": "Sahih al-Bukhari 1442, Sahih Muslim 1010",
        "intro": "Mtume ﷺ amesema:",
        "intro_en": "The Prophet ﷺ said:",
        "arabic": "اَللَّهُمَّ أَعْطِ مُنْفِقًا خَلَفًا، وَيَقُولُ الآخَرُ "
                  "اَللَّهُمَّ أَعْطِ مُمْسِكًا تَلَفًا",
        "text": "Hakuna siku ambayo watu huamka isipokuwa Malaika wawili hushuka. "
                "Mmoja husema: \u2018Ewe Mwenyezi Mungu! Mlipe anayetoa.\u2019 Na mwingine "
                "husema: \u2018Ewe Mwenyezi Mungu! Mwangamize anayezuilia.\u2019",
        "text_en": "There is no day upon which the people rise except that two angels "
                   "descend. One says: \u2018O Allah, give back to the one who spends.\u2019 "
                   "And the other says: \u2018O Allah, bring ruin to the one who withholds.\u2019",
        "ref": "— Sahih al-Bukhari 1442, Sahih Muslim 1010",
        "image": "malaika",
        "alt": "Ulinganisho wa anayetoa na anayezuia mali",
        "alt_en": "A comparison of the one who gives and the one who withholds",
    },
    {
        "kind": "hadith",
        "label": "Hadith",
        "source": "Sahih al-Bukhari 1417, Sahih Muslim 1016",
        "intro": "Mtume ﷺ amesema:",
        "intro_en": "The Prophet ﷺ said:",
        "arabic": "اتَّقُوا النَّارَ وَلَوْ بِشِقِّ تَمْرَةٍ",
        "text": "Jilindeni na Moto hata kwa kutoa nusu ya tende.",
        "text_en": "Protect yourselves from the Fire, even with half a date.",
        "ref": "— Sahih al-Bukhari 1417, Sahih Muslim 1016",
        "image": "tende",
        "alt": "Mkono ukishika nusu ya tende — sadaka ndogo yenye ikhlasi",
        "alt_en": "A hand holding half a date — a small gift given sincerely",
    },
    {
        "kind": "hadith",
        "label": "Hadith",
        "source": "Sahih Muslim 2588",
        "intro": "Mtume ﷺ amesema:",
        "intro_en": "The Prophet ﷺ said:",
        "arabic": "مَا نَقَصَتْ صَدَقَةٌ مِنْ مَالٍ",
        "text": "Sadaka haipunguzi mali. Maana yake ni kwamba kutoa kwa ajili ya "
                "Allah hakumfanyi mtu kuwa mwenye hasara; kuna baraka na malipo "
                "kutoka kwa Mwenyezi Mungu.",
        "text_en": "Charity does not decrease wealth. Giving for the sake of Allah "
                   "leaves no one at a loss; there is blessing and reward from Allah.",
        "ref": "— Sahih Muslim 2588",
        "image": "haipunguzi",
        "alt": "Masanduku ya msaada wa chakula, elimu na huduma za MUWESTA",
        "alt_en": "MUWESTA parcels for food aid, education and community service",
    },
    {
        "kind": "quran",
        "label": "Qur'an",
        "source": "Surat At-Tawbah 9:34",
        "arabic": "وَالَّذِينَ يَكْنِزُونَ الذَّهَبَ وَالْفِضَّةَ وَلَا يُنفِقُونَهَا "
                  "فِي سَبِيلِ اللَّهِ فَبَشِّرْهُم بِعَذَابٍ أَلِيمٍ",
        "text": "Na wale wanaokusanya dhahabu na fedha wala hawazitumii katika njia "
                "ya Mwenyezi Mungu, wape habari ya adhabu yenye uchungu.",
        "text_en": "And those who hoard gold and silver and do not spend it in the "
                   "way of Allah — give them tidings of a painful punishment.",
        "ref": "(Qur'an 9:34)",
        "image": "dhahabu",
        "alt": "Mali iliyofungiwa dhidi ya mali inayotumika kusaidia jamii",
        "alt_en": "Hoarded wealth set against wealth spent to help the community",
    },
]


def verses(lang="sw"):
    """Nukuu kwa lugha husika. Kiarabu na chanzo havitafsiriwi."""
    english = str(lang).startswith("en")
    out = []
    for v in VERSES:
        row = dict(v)
        if english:
            row["text"] = v.get("text_en", v["text"])
            if "intro_en" in v:
                row["intro"] = v["intro_en"]
            if "alt_en" in v:
                row["alt"] = v["alt_en"]
        out.append(row)
    return out
