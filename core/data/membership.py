"""
Maudhui ya ukurasa wa Uanachama — kama yalivyo kwenye bango rasmi la MUWESTA
(MEMBERSHIP). Kiswahili na Kiingereza.

Bei za vifurushi HAZIPO hapa. Zinatoka `members.Category` na zinaonyeshwa
kwenye ukurasa wa Vifurushi (`/vifurushi/`) ili kuwe na chanzo kimoja tu
cha bei kwenye mfumo mzima.
"""

MEMBERSHIP_SW = {
    "about": {
        "label": "Kuhusu Uanachama",
        "paras": [
            "Uanachama wa MUWESTA ni ahadi ya kushiriki katika dhamira yetu ya "
            "kuhudumia binadamu kupitia imani, huruma na maendeleo.",
            "Kama mwanachama, unakuwa sehemu ya mtandao imara unaofanya kazi "
            "kwa pamoja kwa ustawi wa Umma wetu na jamii kwa ujumla.",
        ],
        "quote": "Waumini katika kupendana, kuhurumiana na kuoneana huruma ni "
                 "kama mwili mmoja; kiungo kimoja kikiumwa, mwili wote "
                 "huhisi maumivu.",
        "quote_ref": "(Sahih Bukhari)",
    },
    "join": {
        "label": "Jinsi ya Kujiunga",
        "steps": [
            {"n": "1", "title": "Omba", "icon": "edit",
             "text": "Jaza fomu ya maombi ya uanachama (mtandaoni au ofisini)."},
            {"n": "2", "title": "Wasilisha", "icon": "id-card",
             "text": "Wasilisha taarifa zako na nyaraka zinazohitajika."},
            {"n": "3", "title": "Ukaguzi", "icon": "search",
             "text": "Maombi yako yatapitiwa na Sekretarieti."},
            {"n": "4", "title": "Idhini", "icon": "check-circle",
             "text": "Yakikubaliwa, utaarifiwa na kusajiliwa."},
            {"n": "5", "title": "Karibu", "icon": "users",
             "text": "Pokea kitambulisho chako cha uanachama na kifurushi cha karibu."},
        ],
        "note": "Omba mtandaoni au tembelea ofisi yoyote ya MUWESTA iliyo karibu nawe.",
    },
    "types": {
        "label": "Aina za Uanachama",
        "items": [
            {"icon": "user", "tint": "green", "name": "Mwanachama wa Kawaida",
             "text": "Wazi kwa Waislamu wazima wanaounga mkono dhamira na malengo ya MUWESTA."},
            {"icon": "users", "tint": "gold", "name": "Mwanachama Mshiriki",
             "text": "Watu wanaotaka kuunga mkono shughuli za MUWESTA bila haki ya kupiga kura."},
            {"icon": "building", "tint": "navy", "name": "Mwanachama wa Taasisi",
             "text": "Misikiti, taasisi za Kiislamu, NGOs na mashirika yanayoendana na "
                     "malengo ya MUWESTA."},
            {"icon": "heart", "tint": "purple", "name": "Mwanachama wa Maisha",
             "text": "Wanachama wanaotoa mchango wa mara moja kama itakavyoamuliwa na "
                     "Shirika, na kufurahia uanachama wa maisha."},
            {"icon": "star", "tint": "red", "name": "Mwanachama wa Heshima",
             "text": "Watu wenye huduma au mchango wa kipekee waliokubaliwa na Bodi."},
        ],
    },
    "benefits": {
        "label": "Manufaa ya Uanachama",
        "items": [
            {"icon": "users", "text": "Kuwa sehemu ya dhamira tukufu na Umma wa dunia."},
            {"icon": "book", "text": "Kufikia programu, matukio na mafunzo ya MUWESTA."},
            {"icon": "hand-heart", "text": "Fursa ya kujitolea na kuongoza mabadiliko ya jamii."},
            {"icon": "check-circle", "text": "Haki ya kupiga kura (kwa wanachama wa Kawaida, "
                                             "Maisha na Taasisi)."},
            {"icon": "mail", "text": "Taarifa za mara kwa mara na jarida."},
            {"icon": "receipt", "text": "Punguzo kwenye machapisho, matukio na makongamano ya MUWESTA."},
            {"icon": "target", "text": "Mtandao na watu na washirika wenye mtazamo sawa."},
            {"icon": "heart", "text": "Kufikia zaka, sadaka na programu za ustawi."},
            {"icon": "trophy", "text": "Kutambuliwa na kuthaminiwa kwa wanachama hai."},
            {"icon": "chart-line", "text": "Kujenga uwezo na maendeleo ya uongozi."},
            {"icon": "megaphone", "text": "Kutoa mawazo na kushawishi maamuzi."},
            {"icon": "globe", "text": "Kuwa sehemu ya miradi ya maendeleo endelevu."},
            {"icon": "mosque", "text": "Thawabu za kiroho na matendo mema yanayoendelea."},
            {"icon": "shield", "text": "Msaada wakati wa shida kupitia programu za Shirika."},
            {"icon": "users", "text": "Kuimarisha umoja, amani na mshikamano wa kijamii."},
            {"icon": "gift", "text": "Kupokea kadi ya uanachama na kifurushi cha karibu."},
        ],
    },
    "duties": {
        "label": "Wajibu wa Mwanachama",
        "items": [
            "Kuzingatia dira, dhamira na maadili ya MUWESTA.",
            "Kufuata Katiba, kanuni na maamuzi ya Shirika.",
            "Kulipa ada za uanachama na kuhuisha kwa wakati.",
            "Kushiriki kwenye mikutano, programu na shughuli.",
            "Kukuza umoja na mwenendo mwema katika jamii.",
            "Kuunga mkono miradi ya MUWESTA kwa michango, mawazo au kujitolea.",
            "Kulinda taswira na heshima ya MUWESTA.",
            "Kuhamasisha wengine kujiunga na kuunga mkono dhamira.",
        ],
    },
    "ends": {
        "label": "Jinsi Uanachama Unavyokoma",
        "intro": "Uanachama unaweza kukoma kwa njia zifuatazo:",
        "items": [
            {"name": "Kujiuzulu", "text": "Kwa barua ya kujiuzulu kwa Sekretarieti."},
            {"name": "Kutolipa", "text": "Kushindwa kulipa ada baada ya taarifa rasmi."},
            {"name": "Ukiukaji", "text": "Kushiriki shughuli zinazopingana na malengo, "
                                         "kanuni au maadili ya MUWESTA."},
            {"name": "Utovu wa nidhamu", "text": "Kitendo chochote kinachoharibu au "
                                                 "kudhuru MUWESTA."},
            {"name": "Taarifa za uongo", "text": "Kutoa taarifa za uongo au za kupotosha "
                                                 "wakati wa usajili."},
            {"name": "Hatua za kinidhamu", "text": "Kusimamishwa au kufukuzwa kwa uamuzi "
                                                   "wa Bodi kwa utovu mkubwa wa nidhamu."},
            {"name": "Kifo", "text": "Kwa wanachama binafsi."},
            {"name": "Kuvunjwa", "text": "Kwa Wanachama wa Taasisi (taasisi ikivunjwa)."},
        ],
        "warning": "Mwanachama yeyote ambaye uanachama wake umekoma atarudisha kadi "
                   "yake ya uanachama na kuacha kuwakilisha MUWESTA.",
    },
    "why": {
        "label": "Kwa Nini Kujiunga na MUWESTA?",
        "items": [
            "Kuleta athari ya kudumu",
            "Kuwezesha jamii",
            "Kudumisha maadili ya Kiislamu",
            "Kubadilisha maisha pamoja",
            "Kupata radhi za Allah",
        ],
    },
}


MEMBERSHIP_EN = {
    "about": {
        "label": "About Membership",
        "paras": [
            "Membership in MUWESTA is a commitment to our mission of serving "
            "humanity through faith, compassion and development.",
            "As a member, you become part of a strong network working together "
            "for the welfare of our Ummah and society at large.",
        ],
        "quote": "The believers, in their mutual kindness, compassion and "
                 "sympathy, are like one body; when one part suffers, the "
                 "whole body feels its pain.",
        "quote_ref": "(Sahih Bukhari)",
    },
    "join": {
        "label": "How to Join",
        "steps": [
            {"n": "1", "title": "Apply", "icon": "edit",
             "text": "Fill the membership application form (online or offline)."},
            {"n": "2", "title": "Submit", "icon": "id-card",
             "text": "Submit your details and required documents."},
            {"n": "3", "title": "Review", "icon": "search",
             "text": "Your application will be reviewed by the Secretariat."},
            {"n": "4", "title": "Approval", "icon": "check-circle",
             "text": "Once approved, you will be notified and registered."},
            {"n": "5", "title": "Welcome", "icon": "users",
             "text": "Receive your membership ID and welcome pack."},
        ],
        "note": "Apply online, or visit any MUWESTA office near you.",
    },
    "types": {
        "label": "Types of Membership",
        "items": [
            {"icon": "user", "tint": "green", "name": "Ordinary Member",
             "text": "Open to all Muslim adults who support the mission and "
                     "objectives of MUWESTA."},
            {"icon": "users", "tint": "gold", "name": "Associate Member",
             "text": "Individuals who wish to support MUWESTA activities without "
                     "voting rights."},
            {"icon": "building", "tint": "navy", "name": "Institutional Member",
             "text": "Mosques, Islamic institutions, NGOs and organizations that "
                     "align with MUWESTA goals."},
            {"icon": "heart", "tint": "purple", "name": "Life Member",
             "text": "Members who make a one-time contribution as determined by "
                     "the Society and enjoy lifetime membership."},
            {"icon": "star", "tint": "red", "name": "Honorary Member",
             "text": "Persons of exceptional service or contribution considered "
                     "and approved by the Board."},
        ],
    },
    "benefits": {
        "label": "Benefits of Membership",
        "items": [
            {"icon": "users", "text": "Be part of a noble mission and global Ummah."},
            {"icon": "book", "text": "Access to MUWESTA programs, events and trainings."},
            {"icon": "hand-heart", "text": "Opportunity to volunteer and lead community change."},
            {"icon": "check-circle", "text": "Voting rights (for Ordinary, Life and "
                                             "Institutional Members)."},
            {"icon": "mail", "text": "Regular updates and newsletter."},
            {"icon": "receipt", "text": "Discounts on MUWESTA publications, events and conferences."},
            {"icon": "target", "text": "Networking with like-minded individuals and partners."},
            {"icon": "heart", "text": "Access to zakat, charity and welfare programs."},
            {"icon": "trophy", "text": "Recognition and appreciation for active members."},
            {"icon": "chart-line", "text": "Capacity building and leadership development."},
            {"icon": "megaphone", "text": "Contribute ideas and influence decisions."},
            {"icon": "globe", "text": "Be part of sustainable development projects."},
            {"icon": "mosque", "text": "Spiritual reward and continuous good deeds."},
            {"icon": "shield", "text": "Support in times of need through society's programs."},
            {"icon": "users", "text": "Strengthen unity, peace and social harmony."},
            {"icon": "gift", "text": "Receive membership card and welcome pack."},
        ],
    },
    "duties": {
        "label": "Members' Responsibilities",
        "items": [
            "Uphold the vision, mission and values of MUWESTA.",
            "Abide by the Constitution, rules and decisions of the Society.",
            "Pay membership fees and renew on time.",
            "Participate in meetings, programs and activities.",
            "Promote unity and good conduct in the community.",
            "Support MUWESTA projects through donations, ideas or volunteering.",
            "Protect the image and reputation of MUWESTA.",
            "Encourage others to join and support the mission.",
        ],
    },
    "ends": {
        "label": "How Membership Ends",
        "intro": "Membership may end in the following ways:",
        "items": [
            {"name": "Resignation", "text": "By written notice addressed to the Secretariat."},
            {"name": "Non-payment", "text": "Failure to pay membership dues after "
                                            "official notice."},
            {"name": "Violation", "text": "Engaging in activities against the objectives, "
                                          "rules or values of MUWESTA."},
            {"name": "Misconduct", "text": "Any act that brings disrepute or harm to MUWESTA."},
            {"name": "False Information", "text": "Providing false or misleading information "
                                                  "during registration."},
            {"name": "Disciplinary Action", "text": "Suspension or expulsion by decision of "
                                                    "the Board for serious misconduct."},
            {"name": "Death", "text": "In the case of individual members."},
            {"name": "Dissolution", "text": "In the case of Institutional Members "
                                            "(upon dissolution)."},
        ],
        "warning": "Any member whose membership has ended shall surrender their membership "
                   "card and cease to represent MUWESTA.",
    },
    "why": {
        "label": "Why Join MUWESTA?",
        "items": [
            "Make a lasting impact",
            "Empower communities",
            "Uphold Islamic values",
            "Change lives together",
            "Earn the pleasure of Allah",
        ],
    },
}


def membership(lang="sw"):
    """Maudhui ya ukurasa wa Uanachama kwa lugha husika."""
    return MEMBERSHIP_EN if str(lang).startswith("en") else MEMBERSHIP_SW
