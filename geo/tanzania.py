"""
Jiografia halisi ya Tanzania Bara.

Chanzo: mgawanyo wa kiutawala wa TAMISEMI (halmashauri) na Ofisi ya Taifa ya
Takwimu (NBS). Wilaya zote 26 za mikoa zimeorodheshwa kwa ukamilifu.

**Kata**: Tanzania Bara ina kata zaidi ya 3,900. Zilizoorodheshwa hapa ni
kata halisi kwa kila halmashauri, lakini si orodha kamili ya kila
halmashauri — ni kata kuu zinazojulikana. Kwa orodha kamili, tumia
`python manage.py leta_jiografia kata.csv` (angalia README).

Aina za halmashauri:
    DC = Wilaya    MC = Manispaa    CC = Jiji    TC = Mji
"""

# ===========================================================================
#  KANDA — kila kanda ina mratibu mmoja
# ===========================================================================
ZONES = [
    ("Kanda ya Mashariki", "Eastern Zone", "mashariki", "Dar es Salaam", 0),
    ("Kanda ya Kaskazini", "Northern Zone", "kaskazini", "Arusha", 1),
    ("Kanda ya Ziwa", "Lake Zone", "ziwa", "Mwanza", 2),
    ("Kanda ya Kati", "Central Zone", "kati", "Dodoma", 3),
    ("Kanda ya Magharibi", "Western Zone", "magharibi", "Kigoma", 4),
    ("Kanda ya Kusini na Nyanda za Juu Kusini",
     "Southern & Southern Highlands Zone", "kusini", "Mbeya", 5),
]

#: mkoa -> kanda
REGION_ZONE = {
    # Mashariki
    "Dar es Salaam": "mashariki", "Pwani": "mashariki",
    "Morogoro": "mashariki", "Tanga": "mashariki",
    # Kaskazini
    "Arusha": "kaskazini", "Kilimanjaro": "kaskazini", "Manyara": "kaskazini",
    # Ziwa
    "Mwanza": "ziwa", "Mara": "ziwa", "Kagera": "ziwa",
    "Geita": "ziwa", "Simiyu": "ziwa", "Shinyanga": "ziwa",
    # Kati
    "Dodoma": "kati", "Singida": "kati", "Tabora": "kati",
    # Magharibi
    "Kigoma": "magharibi", "Katavi": "magharibi", "Rukwa": "magharibi",
    # Kusini na Nyanda za Juu Kusini
    "Mbeya": "kusini", "Songwe": "kusini", "Iringa": "kusini", "Njombe": "kusini",
    "Lindi": "kusini", "Mtwara": "kusini", "Ruvuma": "kusini",
}

# ===========================================================================
#  MIKOA — jina, x, y kwenye ramani (0-100), mpangilio
# ===========================================================================
REGIONS = [
    ("Dar es Salaam", 78, 62), ("Pwani", 74, 56), ("Morogoro", 62, 62), ("Tanga", 72, 36),
    ("Arusha", 52, 22), ("Kilimanjaro", 64, 20), ("Manyara", 56, 34),
    ("Mwanza", 24, 26), ("Mara", 34, 16), ("Kagera", 16, 16),
    ("Geita", 20, 32), ("Simiyu", 36, 26), ("Shinyanga", 32, 36),
    ("Dodoma", 50, 52), ("Singida", 44, 44), ("Tabora", 34, 46),
    ("Kigoma", 14, 44), ("Katavi", 20, 58), ("Rukwa", 18, 68),
    ("Mbeya", 26, 74), ("Songwe", 24, 80), ("Iringa", 44, 68), ("Njombe", 40, 80),
    ("Lindi", 72, 76), ("Mtwara", 70, 86), ("Ruvuma", 52, 88),
]

# ===========================================================================
#  HALMASHAURI (wilaya) kwa kila mkoa
# ===========================================================================
DISTRICTS = {
    "Dar es Salaam": [
        ("Ilala", "MC"), ("Kinondoni", "MC"), ("Temeke", "MC"),
        ("Ubungo", "MC"), ("Kigamboni", "MC"),
    ],
    "Pwani": [
        ("Kibaha", "TC"), ("Kibaha", "DC"), ("Bagamoyo", "DC"), ("Chalinze", "DC"),
        ("Kisarawe", "DC"), ("Mkuranga", "DC"), ("Rufiji", "DC"), ("Mafia", "DC"),
    ],
    "Morogoro": [
        ("Morogoro", "MC"), ("Morogoro", "DC"), ("Kilosa", "DC"), ("Mvomero", "DC"),
        ("Kilombero", "DC"), ("Ulanga", "DC"), ("Gairo", "DC"),
        ("Malinyi", "DC"), ("Ifakara", "TC"),
    ],
    "Tanga": [
        ("Tanga", "CC"), ("Muheza", "DC"), ("Korogwe", "TC"), ("Korogwe", "DC"),
        ("Lushoto", "DC"), ("Handeni", "TC"), ("Handeni", "DC"), ("Pangani", "DC"),
        ("Kilindi", "DC"), ("Mkinga", "DC"), ("Bumbuli", "DC"),
    ],
    "Arusha": [
        ("Arusha", "CC"), ("Arusha", "DC"), ("Meru", "DC"), ("Karatu", "DC"),
        ("Monduli", "DC"), ("Longido", "DC"), ("Ngorongoro", "DC"),
    ],
    "Kilimanjaro": [
        ("Moshi", "MC"), ("Moshi", "DC"), ("Hai", "DC"), ("Siha", "DC"),
        ("Rombo", "DC"), ("Mwanga", "DC"), ("Same", "DC"),
    ],
    "Manyara": [
        ("Babati", "TC"), ("Babati", "DC"), ("Hanang", "DC"), ("Mbulu", "TC"),
        ("Mbulu", "DC"), ("Simanjiro", "DC"), ("Kiteto", "DC"),
    ],
    "Mwanza": [
        ("Nyamagana", "MC"), ("Ilemela", "MC"), ("Magu", "DC"), ("Sengerema", "DC"),
        ("Misungwi", "DC"), ("Kwimba", "DC"), ("Ukerewe", "DC"), ("Buchosa", "DC"),
    ],
    "Mara": [
        ("Musoma", "MC"), ("Musoma", "DC"), ("Bunda", "TC"), ("Bunda", "DC"),
        ("Tarime", "TC"), ("Tarime", "DC"), ("Serengeti", "DC"),
        ("Rorya", "DC"), ("Butiama", "DC"),
    ],
    "Kagera": [
        ("Bukoba", "MC"), ("Bukoba", "DC"), ("Muleba", "DC"), ("Karagwe", "DC"),
        ("Kyerwa", "DC"), ("Ngara", "DC"), ("Biharamulo", "DC"), ("Missenyi", "DC"),
    ],
    "Geita": [
        ("Geita", "TC"), ("Geita", "DC"), ("Chato", "DC"), ("Bukombe", "DC"),
        ("Mbogwe", "DC"), ("Nyang'hwale", "DC"),
    ],
    "Simiyu": [
        ("Bariadi", "TC"), ("Bariadi", "DC"), ("Maswa", "DC"), ("Meatu", "DC"),
        ("Busega", "DC"), ("Itilima", "DC"),
    ],
    "Shinyanga": [
        ("Shinyanga", "MC"), ("Shinyanga", "DC"), ("Kahama", "TC"), ("Msalala", "DC"),
        ("Ushetu", "DC"), ("Kishapu", "DC"),
    ],
    "Dodoma": [
        ("Dodoma", "CC"), ("Bahi", "DC"), ("Chamwino", "DC"), ("Chemba", "DC"),
        ("Kondoa", "TC"), ("Kondoa", "DC"), ("Kongwa", "DC"), ("Mpwapwa", "DC"),
    ],
    "Singida": [
        ("Singida", "MC"), ("Singida", "DC"), ("Iramba", "DC"), ("Mkalama", "DC"),
        ("Manyoni", "DC"), ("Ikungi", "DC"), ("Itigi", "DC"),
    ],
    "Tabora": [
        ("Tabora", "MC"), ("Uyui", "DC"), ("Igunga", "DC"), ("Nzega", "TC"),
        ("Nzega", "DC"), ("Sikonge", "DC"), ("Urambo", "DC"), ("Kaliua", "DC"),
    ],
    "Kigoma": [
        ("Kigoma-Ujiji", "MC"), ("Kigoma", "DC"), ("Kasulu", "TC"), ("Kasulu", "DC"),
        ("Kibondo", "DC"), ("Buhigwe", "DC"), ("Uvinza", "DC"), ("Kakonko", "DC"),
    ],
    "Katavi": [
        ("Mpanda", "MC"), ("Mpimbwe", "DC"), ("Tanganyika", "DC"),
        ("Mlele", "DC"), ("Nsimbo", "DC"),
    ],
    "Rukwa": [
        ("Sumbawanga", "MC"), ("Sumbawanga", "DC"), ("Nkasi", "DC"),
        ("Kalambo", "DC"),
    ],
    "Mbeya": [
        ("Mbeya", "CC"), ("Mbeya", "DC"), ("Rungwe", "DC"), ("Kyela", "DC"),
        ("Chunya", "DC"), ("Mbarali", "DC"), ("Busokelo", "DC"),
    ],
    "Songwe": [
        ("Tunduma", "TC"), ("Mbozi", "DC"), ("Momba", "DC"),
        ("Ileje", "DC"), ("Songwe", "DC"),
    ],
    "Iringa": [
        ("Iringa", "MC"), ("Iringa", "DC"), ("Mufindi", "DC"),
        ("Kilolo", "DC"), ("Mafinga", "TC"),
    ],
    "Njombe": [
        ("Njombe", "TC"), ("Njombe", "DC"), ("Makete", "DC"), ("Ludewa", "DC"),
        ("Wanging'ombe", "DC"), ("Makambako", "TC"),
    ],
    "Lindi": [
        ("Lindi", "MC"), ("Lindi", "DC"), ("Kilwa", "DC"), ("Nachingwea", "DC"),
        ("Liwale", "DC"), ("Ruangwa", "DC"), ("Mtama", "DC"),
    ],
    "Mtwara": [
        ("Mtwara", "MC"), ("Mtwara", "DC"), ("Masasi", "TC"), ("Masasi", "DC"),
        ("Newala", "TC"), ("Newala", "DC"), ("Tandahimba", "DC"), ("Nanyumbu", "DC"),
        ("Nanyamba", "TC"),
    ],
    "Ruvuma": [
        ("Songea", "MC"), ("Songea", "DC"), ("Mbinga", "TC"), ("Mbinga", "DC"),
        ("Tunduru", "DC"), ("Namtumbo", "DC"), ("Nyasa", "DC"), ("Madaba", "DC"),
    ],
}

# ===========================================================================
#  KATA halisi kwa kila halmashauri
#  Ufunguo: "Mkoa|Wilaya"
# ===========================================================================
WARDS = {
    # ---------------- Dar es Salaam ----------------
    "Dar es Salaam|Ilala": ["Upanga Mashariki", "Upanga Magharibi", "Kariakoo", "Jangwani",
                            "Gerezani", "Kisutu", "Mchikichini", "Buguruni", "Ilala",
                            "Vingunguti", "Tabata", "Segerea", "Kipawa", "Kiwalani",
                            "Ukonga", "Pugu", "Msongola", "Chanika"],
    "Dar es Salaam|Kinondoni": ["Msasani", "Kinondoni", "Hananasif", "Mzimuni", "Magomeni",
                                "Makumbusho", "Mikocheni", "Kijitonyama", "Ndugumbi",
                                "Tandale", "Mwananyamala", "Kigogo", "Upanga", "Oysterbay"],
    "Dar es Salaam|Temeke": ["Keko", "Kurasini", "Mtoni", "Temeke", "Miburani", "Azimio",
                             "Chang'ombe", "Sandali", "Yombo Vituka", "Toangoma",
                             "Mbagala", "Mbagala Kuu", "Charambe", "Kibondemaji"],
    "Dar es Salaam|Ubungo": ["Ubungo", "Manzese", "Sinza", "Kimara", "Mburahati",
                             "Makuburi", "Mabibo", "Kibamba", "Msigani", "Saranga",
                             "Goba", "Mbezi", "Kwembe", "Makurumla"],
    "Dar es Salaam|Kigamboni": ["Kigamboni", "Vijibweni", "Kibada", "Tungi", "Mjimwema",
                                "Kisarawe II", "Somangila", "Pembamnazi", "Kimbiji"],
    # ---------------- Pwani ----------------
    "Pwani|Kibaha (TC)": ["Maili Moja", "Tumbi", "Picha ya Ndege", "Mkuza", "Visiga"],
    "Pwani|Kibaha": ["Mlandizi", "Kwala", "Ruvu", "Magindu", "Soga", "Dutumi"],
    "Pwani|Bagamoyo": ["Dunda", "Magomeni", "Zinga", "Kiromo", "Yombo", "Makurunge",
                       "Mkange", "Kerege", "Zegereni"],
    "Pwani|Chalinze": ["Chalinze", "Msata", "Miono", "Lugoba", "Talawanda", "Mbwewe",
                       "Kibindu", "Ubenazomozi"],
    "Pwani|Kisarawe": ["Kisarawe", "Maneromango", "Marumbo", "Masaki", "Msimbu",
                       "Cholesamvula", "Vikumburu"],
    "Pwani|Mkuranga": ["Mkuranga", "Vikindu", "Kisiju", "Mkamba", "Tambani",
                       "Kitomondo", "Shungubweni"],
    "Pwani|Rufiji": ["Utete", "Ikwiriri", "Kibiti", "Mohoro", "Mkongo", "Bungu", "Ngorongo"],
    "Pwani|Mafia": ["Kilindoni", "Baleni", "Kirongwe", "Jibondo", "Bweni", "Kanga"],
    # ---------------- Morogoro ----------------
    "Morogoro|Morogoro (MC)": ["Sabasaba", "Kilakala", "Boma", "Kichangani", "Uwanja wa Taifa",
                               "Mafiga", "Mwembesongo", "Kihonda", "Mji Mkuu", "Mbuyuni"],
    "Morogoro|Morogoro": ["Mikese", "Mkuyuni", "Matombo", "Kisemu", "Bwakira", "Tegetero",
                          "Kinole", "Mvuha", "Ngerengere"],
    "Morogoro|Kilosa": ["Kilosa", "Magole", "Mikumi", "Kimamba", "Msowero", "Rudewa",
                        "Ulaya", "Zombo", "Dumila"],
    "Morogoro|Mvomero": ["Mvomero", "Turiani", "Mtibwa", "Melela", "Dakawa", "Hembeti",
                         "Mlali", "Doma"],
    "Morogoro|Kilombero": ["Mang'ula", "Mlimba", "Mchombe", "Idete", "Signali",
                           "Kisawasawa", "Mkula"],
    "Morogoro|Ulanga": ["Mahenge", "Lupiro", "Vigoi", "Ruaha", "Iragua", "Mtimbira"],
    "Morogoro|Gairo": ["Gairo", "Nongwe", "Chakwale", "Idibo", "Msowero", "Rubeho"],
    "Morogoro|Malinyi": ["Malinyi", "Kilosa kwa Mpepo", "Ngoheranga", "Usangule", "Igawa"],
    "Morogoro|Ifakara (TC)": ["Ifakara", "Lipangalala", "Katindiuka", "Viwanja Sitini",
                              "Kibaoni", "Michenga"],
    # ---------------- Tanga ----------------
    "Tanga|Tanga (CC)": ["Chumbageni", "Ngamiani Kaskazini", "Ngamiani Kati", "Makorora",
                         "Mzizima", "Nguvumali", "Msambweni", "Mabawa", "Duga", "Pongwe"],
    "Tanga|Muheza": ["Muheza", "Majengo", "Ngomeni", "Amani", "Mtindiro", "Kwafungo",
                     "Kicheba", "Magila"],
    "Tanga|Korogwe (TC)": ["Korogwe Mjini", "Magoma", "Old Korogwe", "Manundu", "Msambiazi"],
    "Tanga|Korogwe": ["Mombo", "Bungu", "Kwashemshi", "Dindira", "Makuyuni", "Mkalamo"],
    "Tanga|Lushoto": ["Lushoto", "Soni", "Mlalo", "Mlola", "Gare", "Ubiri", "Malindi",
                      "Ngwelo", "Mtae"],
    "Tanga|Handeni (TC)": ["Chanika", "Kwamsisi", "Mkata", "Mzundu", "Konje"],
    "Tanga|Handeni": ["Kwamgwe", "Kwaluguru", "Segera", "Misima", "Kabuku", "Komkonga"],
    "Tanga|Pangani": ["Pangani Magharibi", "Pangani Mashariki", "Mkwaja", "Bushiri",
                      "Mwera", "Madanga"],
    "Tanga|Kilindi": ["Songe", "Kwediboma", "Kikunde", "Lwande", "Masagalu", "Tunguli"],
    "Tanga|Mkinga": ["Kasera", "Duga", "Moa", "Boma", "Mtimbwani", "Manza", "Doda"],
    "Tanga|Bumbuli": ["Bumbuli", "Soni", "Baga", "Funta", "Mponde", "Tamota"],
    # ---------------- Arusha ----------------
    "Arusha|Arusha (CC)": ["Kaloleni", "Levolosi", "Sekei", "Themi", "Ngarenaro",
                           "Sombetini", "Unga Limited", "Elerai", "Kimandolu",
                           "Lemara", "Daraja Mbili", "Sokon I"],
    "Arusha|Arusha": ["Mateves", "Oldonyosambu", "Olkokola", "Musa", "Ilkiding'a",
                      "Sambasha", "Kimnyaki", "Bwawani"],
    "Arusha|Meru": ["Usa River", "Poli", "Maji ya Chai", "King'ori", "Nkoaranga",
                    "Akheri", "Nkoanrua", "Songoro", "Leguruki"],
    "Arusha|Karatu": ["Karatu", "Mbulumbulu", "Endabash", "Rhotia", "Ganako",
                      "Qurus", "Baray", "Buger"],
    "Arusha|Monduli": ["Monduli Mjini", "Engaruka", "Mto wa Mbu", "Esilalei",
                       "Sepeko", "Lolkisale", "Makuyuni"],
    "Arusha|Longido": ["Longido", "Engarenaibor", "Kimokouwa", "Namanga",
                       "Tingatinga", "Ol Molog", "Elerai"],
    "Arusha|Ngorongoro": ["Ngorongoro", "Endulen", "Nainokanoka", "Olbalbal",
                          "Enguserosambu", "Soitsambu", "Loliondo", "Sale"],
    # ---------------- Kilimanjaro ----------------
    "Kilimanjaro|Moshi (MC)": ["Kiusa", "Mji Mpya", "Msaranga", "Njoro", "Pasua",
                               "Rau", "Karanga", "Longuo", "Bondeni", "Kilimanjaro"],
    "Kilimanjaro|Moshi": ["Mabogini", "Kahe", "Old Moshi", "Kirua Vunjo", "Mwika",
                          "Marangu", "Kilema", "Uru", "Arusha Chini"],
    "Kilimanjaro|Hai": ["Hai", "Boma Ng'ombe", "Machame", "Masama", "Bomang'ombe",
                        "Rundugai", "Mnadani"],
    "Kilimanjaro|Siha": ["Sanya Juu", "Ngarenairobi", "Kashashi", "Biriri",
                         "Makiwaru", "Karansi"],
    "Kilimanjaro|Rombo": ["Mkuu", "Tarakea", "Mengwe", "Mahida", "Useri",
                          "Katangara", "Holili"],
    "Kilimanjaro|Mwanga": ["Mwanga", "Kifula", "Lembeni", "Jipe", "Kigonigoni",
                           "Msangeni", "Chomvu"],
    "Kilimanjaro|Same": ["Same", "Hedaru", "Mwembe", "Kisiwani", "Mabilioni",
                         "Kihurio", "Ndungu", "Makanya"],
    # ---------------- Manyara ----------------
    "Manyara|Babati (TC)": ["Babati", "Bagara", "Bonga", "Sigino", "Singe", "Maisaka"],
    "Manyara|Babati": ["Magugu", "Dareda", "Galapo", "Mamire", "Riroda", "Endagaw",
                       "Gorowa", "Kiru"],
    "Manyara|Hanang": ["Katesh", "Endasak", "Bassotu", "Gendabi", "Ganana",
                       "Nangwa", "Dirma"],
    "Manyara|Mbulu (TC)": ["Mbulu Mjini", "Tlawi", "Nahasey", "Imboru", "Ayamohe"],
    "Manyara|Mbulu": ["Dongobesh", "Haydom", "Endagikot", "Maretadu", "Daudi", "Yaeda"],
    "Manyara|Simanjiro": ["Orkesumet", "Naberera", "Terrat", "Loiborsoit", "Emboreet",
                          "Msitu wa Tembo", "Ruvu Remit"],
    "Manyara|Kiteto": ["Kibaya", "Dongo", "Kijungu", "Namelock", "Partimbo",
                       "Sunya", "Engusero"],
    # ---------------- Mwanza ----------------
    "Mwanza|Nyamagana (MC)": ["Mbugani", "Nyamagana", "Mkuyuni", "Isamilo", "Pamba",
                              "Mirongo", "Butimba", "Igoma", "Buhongwa", "Nyegezi"],
    "Mwanza|Ilemela (MC)": ["Ilemela", "Nyakato", "Kirumba", "Pasiansi", "Kitangiri",
                            "Buswelu", "Sangabuye", "Kayenze", "Bugogwa"],
    "Mwanza|Magu": ["Magu", "Kisesa", "Nyanguge", "Ng'haya", "Lutale", "Nyigogo",
                    "Sukuma", "Kabila"],
    "Mwanza|Sengerema": ["Sengerema", "Nyehunge", "Katunguru", "Buyagu", "Kagunga",
                         "Nyampande", "Busisi", "Tabaruka"],
    "Mwanza|Misungwi": ["Misungwi", "Usagara", "Mbarika", "Ilujamate", "Koromije",
                        "Mabuki", "Sumve", "Nyang'homango"],
    "Mwanza|Kwimba": ["Ngudu", "Malya", "Nyambiti", "Sumve", "Mwamala", "Hungumalwa",
                      "Nkalalo", "Bupamwa"],
    "Mwanza|Ukerewe": ["Nansio", "Bukindo", "Muriti", "Bwiro", "Ilangala",
                       "Namilembe", "Ukara", "Bukongo"],
    "Mwanza|Buchosa": ["Nyakaliro", "Kasenyi", "Nyamazugo", "Bukokwa", "Chifunfu",
                       "Kahunda", "Nyakasasa"],
    # ---------------- Mara ----------------
    "Mara|Musoma (MC)": ["Mukendo", "Nyasho", "Kitaji", "Mwisenge", "Iringo",
                         "Bweri", "Makoko", "Kigera"],
    "Mara|Musoma": ["Bukima", "Bugwema", "Nyambono", "Kiriba", "Etaro", "Busambara"],
    "Mara|Bunda (TC)": ["Bunda Mjini", "Kunzugu", "Balili", "Wariku", "Guta"],
    "Mara|Bunda": ["Nansimo", "Mugeta", "Kibara", "Namhula", "Salama", "Nyamuswa"],
    "Mara|Tarime (TC)": ["Nyamisangura", "Turwa", "Bomani", "Nkende", "Sabasaba"],
    "Mara|Tarime": ["Sirari", "Susuni", "Nyamwaga", "Muriba", "Gorong'a",
                    "Kemambo", "Nyanungu"],
    "Mara|Serengeti": ["Mugumu", "Ring'wani", "Nyambureti", "Machochwe", "Issenye",
                       "Kisaka", "Natta", "Rung'abure"],
    "Mara|Rorya": ["Ingri Juu", "Shirati", "Nyamagaro", "Roche", "Kigunga",
                   "Nyathorogo", "Bukura"],
    "Mara|Butiama": ["Butiama", "Buhemba", "Nyamimange", "Kyanyari", "Bisumwa",
                     "Masaba", "Etaro"],
    # ---------------- Kagera ----------------
    "Kagera|Bukoba (MC)": ["Bakoba", "Kahororo", "Nyanga", "Miembeni", "Kashai",
                           "Buhembe", "Rwamishenye", "Hamugembe"],
    "Kagera|Bukoba": ["Katoro", "Kanyangereko", "Rubale", "Kaagya", "Karabagaine",
                      "Ibwera", "Kikomelo"],
    "Kagera|Muleba": ["Muleba", "Kamachumu", "Nshamba", "Kimwani", "Bureza",
                      "Kibanga", "Ruhanga", "Izigo"],
    "Kagera|Karagwe": ["Kayanga", "Nyakasimbi", "Bugene", "Nyabiyonza", "Kihanga",
                       "Chonyonyo", "Ihanda"],
    "Kagera|Kyerwa": ["Kyerwa", "Nkwenda", "Rukuraijo", "Businde", "Kaisho",
                      "Murongo", "Isingiro"],
    "Kagera|Ngara": ["Ngara Mjini", "Rulenge", "Murusagamba", "Nyamiaga", "Mbuba",
                     "Bugarama", "Kabanga"],
    "Kagera|Biharamulo": ["Biharamulo", "Nyabusozi", "Nyakahura", "Nyantakara",
                          "Runazi", "Lusahunga"],
    "Kagera|Missenyi": ["Bunazi", "Kakunyu", "Mutukula", "Kilimilile", "Bugorora",
                        "Kassambya", "Minziro"],
    # ---------------- Geita ----------------
    "Geita|Geita (TC)": ["Bombambili", "Kalangalala", "Mtakuja", "Nyakabale",
                         "Nyankumbu", "Buhalahala"],
    "Geita|Geita": ["Katoro", "Bukoli", "Nzera", "Kaseme", "Chikobe", "Nyachiluluma",
                    "Bugulula", "Butobela"],
    "Geita|Chato": ["Chato", "Buseresere", "Muganza", "Bwanga", "Bukome",
                    "Katende", "Nyamirembe"],
    "Geita|Bukombe": ["Ushirombo", "Uyovu", "Bugelenga", "Namonge", "Butinzya",
                      "Runzewe", "Iyogelo"],
    "Geita|Mbogwe": ["Mbogwe", "Masumbwe", "Nyasato", "Ilolangulu", "Lulembela",
                     "Nanda", "Bukandwe"],
    "Geita|Nyang'hwale": ["Kharumwa", "Nyang'hwale", "Bukwimba", "Izunya",
                          "Nyijundu", "Kakola"],
    # ---------------- Simiyu ----------------
    "Simiyu|Bariadi (TC)": ["Bariadi Mjini", "Nyakabindi", "Somanda", "Isanga", "Malambo"],
    "Simiyu|Bariadi": ["Dutwa", "Bunamhala", "Kasoli", "Sapiwi", "Mhango", "Nkindwabiye"],
    "Simiyu|Maswa": ["Maswa", "Nyalikungu", "Sengerema", "Buchambi", "Shishiyu",
                     "Malampaka", "Nguliguli"],
    "Simiyu|Meatu": ["Mwanhuzi", "Kisesa", "Mwabuzo", "Lubiga", "Bukundi",
                     "Mwamishali", "Imalaseko"],
    "Simiyu|Busega": ["Nyashimo", "Lamadi", "Kabita", "Nyaluhande", "Badugu",
                      "Mkula", "Ngasamo"],
    "Simiyu|Itilima": ["Lagangabilili", "Nkoma", "Mwaswale", "Budalabujiga",
                       "Chinamili", "Sagata"],
    # ---------------- Shinyanga ----------------
    "Shinyanga|Shinyanga (MC)": ["Ndala", "Kambarage", "Chibe", "Ngokolo", "Mwawaza",
                                 "Old Shinyanga", "Ibadakuli"],
    "Shinyanga|Shinyanga": ["Tinde", "Didia", "Usanda", "Mwakitolyo", "Samuye",
                            "Nsalala", "Puni"],
    "Shinyanga|Kahama (TC)": ["Kahama Mjini", "Mhungula", "Nyihogo", "Ngogwa",
                              "Zongomera", "Malunga"],
    "Shinyanga|Msalala": ["Bulyanhulu", "Segese", "Isaka", "Ntobo", "Jana",
                          "Bugarama", "Lunguya"],
    "Shinyanga|Ushetu": ["Ushetu", "Ulowa", "Ubagwe", "Chambo", "Igwamanoni",
                         "Nyankende", "Uyogo"],
    "Shinyanga|Kishapu": ["Kishapu", "Mwadui", "Ngofila", "Mondo", "Talaga",
                          "Somagedi", "Uchunga"],
    # ---------------- Dodoma ----------------
    "Dodoma|Dodoma (CC)": ["Makole", "Kilimani", "Viwandani", "Majengo", "Chamwino",
                           "Kikuyu Kusini", "Kikuyu Kaskazini", "Miyuji", "Nkuhungu",
                           "Ipagala", "Hazina", "Mkonze", "Zuzu", "Msalato"],
    "Dodoma|Bahi": ["Bahi", "Mundemu", "Chipanga", "Mpamantwa", "Chibelela",
                    "Zanka", "Kigwe", "Nondwa"],
    "Dodoma|Chamwino": ["Chamwino", "Buigiri", "Mvumi Mission", "Handali", "Msanga",
                        "Manchali", "Idifu", "Membe"],
    "Dodoma|Chemba": ["Chemba", "Kwamtoro", "Farkwa", "Goima", "Mrijo",
                      "Paranga", "Makorongo"],
    "Dodoma|Kondoa (TC)": ["Kondoa Mjini", "Bolisa", "Suruke", "Kingale", "Serya"],
    "Dodoma|Kondoa": ["Kolo", "Bereko", "Pahi", "Masange", "Bumbuta", "Mnenia",
                      "Kikore", "Haubi"],
    "Dodoma|Kongwa": ["Kongwa", "Mpwapwa", "Kibaigwa", "Sejeli", "Chamkoroma",
                      "Ugogoni", "Zoissa", "Mlali"],
    "Dodoma|Mpwapwa": ["Mpwapwa", "Kibakwe", "Rudi", "Mazae", "Berege",
                       "Chipogoro", "Lupeta", "Mlembule"],
    # ---------------- Singida ----------------
    "Singida|Singida (MC)": ["Mandewa", "Utemini", "Mtipa", "Mwankoko", "Unyianga",
                             "Ipembe", "Uhamaka", "Mungumaji"],
    "Singida|Singida": ["Ilongero", "Mgori", "Merya", "Mudida", "Ntonge",
                        "Mtinko", "Msisi", "Makuro"],
    "Singida|Iramba": ["Kiomboi", "Shelui", "Ndago", "Kinampanda", "Urughu",
                       "Kisiriri", "Mtoa"],
    "Singida|Mkalama": ["Nduguti", "Gumanga", "Kinyangiri", "Iguguno", "Mwangeza",
                        "Msingi", "Ilunda"],
    "Singida|Manyoni": ["Manyoni", "Chikuyu", "Heka", "Sanjaranda", "Mwamagembe",
                        "Makuru", "Sasilo"],
    "Singida|Ikungi": ["Ikungi", "Sepuka", "Ihanja", "Mungaa", "Mkiwa",
                       "Puma", "Ntuntu", "Dung'unyi"],
    "Singida|Itigi": ["Itigi", "Kitaraka", "Rungwa", "Mitundu", "Majengo"],
    # ---------------- Tabora ----------------
    "Tabora|Tabora (MC)": ["Cheyo", "Gongoni", "Kanyenye", "Isevya", "Ipuli",
                           "Ng'ambo", "Tambukareli", "Kitete", "Malolo"],
    "Tabora|Uyui": ["Isikizya", "Igalula", "Ilolangulu", "Upuge", "Loya",
                    "Nsololo", "Kizengi", "Goweko"],
    "Tabora|Igunga": ["Igunga", "Nanga", "Ziba", "Choma", "Simbo", "Mbutu",
                      "Igurubi", "Itumba"],
    "Tabora|Nzega (TC)": ["Nzega Mjini", "Itobo", "Bukene", "Mwangoye", "Miguwa"],
    "Tabora|Nzega": ["Mogwa", "Puge", "Semembela", "Utwigu", "Ndala",
                     "Mwakashanhala", "Isagenhe"],
    "Tabora|Sikonge": ["Sikonge", "Kitunda", "Kipanga", "Usoke", "Mibono",
                       "Tutuo", "Kiloli"],
    "Tabora|Urambo": ["Urambo", "Usisya", "Kaliua", "Muungano", "Songambele",
                      "Vumilia", "Ussoke"],
    "Tabora|Kaliua": ["Kaliua", "Igwisi", "Ushokola", "Zugimlole", "Ukumbisiganga",
                      "Silambo", "Usinge"],
    # ---------------- Kigoma ----------------
    "Kigoma|Kigoma-Ujiji (MC)": ["Bangwe", "Buzebazeba", "Gungu", "Kagera", "Kibirizi",
                                 "Kipampa", "Mwanga Kaskazini", "Rusimbi", "Katubuka"],
    "Kigoma|Kigoma": ["Kalinzi", "Mkongoro", "Mwandiga", "Bitale", "Kagunga",
                      "Mahembe", "Simbo", "Kidahwe"],
    "Kigoma|Kasulu (TC)": ["Kasulu Mjini", "Muzye", "Murufiti", "Kitagata", "Nyansha"],
    "Kigoma|Kasulu": ["Kabanga", "Heru Juu", "Muhunga", "Nyakitonto", "Titye",
                      "Makere", "Rusesa"],
    "Kigoma|Kibondo": ["Kibondo", "Bitale", "Kitahana", "Mabamba", "Kizazi",
                       "Nengo", "Busagara"],
    "Kigoma|Buhigwe": ["Buhigwe", "Janda", "Muyama", "Kibande", "Munzeze",
                       "Mugera", "Biharu"],
    "Kigoma|Uvinza": ["Uvinza", "Nguruka", "Ilagala", "Mtegowanoti", "Basanza",
                      "Sunuka", "Kandaga"],
    "Kigoma|Kakonko": ["Kakonko", "Nyabibuye", "Gwarama", "Kasanda", "Muhange",
                       "Kiziguzigu"],
    # ---------------- Katavi ----------------
    "Katavi|Mpanda (MC)": ["Makanyagio", "Shanwe", "Kashaulili", "Misunkumilo",
                           "Nsemulwa", "Ilembo"],
    "Katavi|Mpimbwe": ["Mamba", "Ikola", "Mwese", "Kabungu", "Usevya", "Majimoto"],
    "Katavi|Tanganyika": ["Karema", "Kabungu", "Mwese", "Ikola", "Sibwesa", "Kalema"],
    "Katavi|Mlele": ["Inyonga", "Utende", "Mgombe", "Ilela", "Kamsisi"],
    "Katavi|Nsimbo": ["Nsimbo", "Machimboni", "Ugalla", "Sitalike", "Katumba", "Kapalala"],
    # ---------------- Rukwa ----------------
    "Rukwa|Sumbawanga (MC)": ["Katandala", "Mazwi", "Milanzi", "Senga", "Chanji",
                              "Izia", "Malangali", "Mollo"],
    "Rukwa|Sumbawanga": ["Laela", "Kaengesa", "Mpui", "Kipeta", "Msanda Muungano",
                         "Miangalua", "Kilangawana"],
    "Rukwa|Nkasi": ["Namanyere", "Kirando", "Wampembe", "Kate", "Chala",
                    "Kipande", "Isale"],
    "Rukwa|Kalambo": ["Matai", "Kasanga", "Mwazye", "Kasu", "Mkowe",
                      "Ulumi", "Legeza Mwendo"],
    # ---------------- Mbeya ----------------
    "Mbeya|Mbeya (CC)": ["Sisimba", "Ruanda", "Iyunga", "Mwakibete", "Forest",
                         "Nzovwe", "Itende", "Iganjo", "Maanga", "Ilomba"],
    "Mbeya|Mbeya": ["Mbalizi", "Santilya", "Ilungu", "Inyala", "Iwiji",
                    "Isuto", "Utengule", "Ijombe"],
    "Mbeya|Rungwe": ["Tukuyu", "Kiwira", "Ikuti", "Masukulu", "Suma",
                     "Bulyaga", "Kisondela", "Lufingo"],
    "Mbeya|Kyela": ["Kyela", "Ipinda", "Ngonga", "Matema", "Ikolo",
                    "Bujonde", "Kajunjumele"],
    "Mbeya|Chunya": ["Chunya", "Makongolosi", "Mkwajuni", "Kiwanja", "Matundasi",
                     "Lupa Tingatinga", "Mbugani"],
    "Mbeya|Mbarali": ["Rujewa", "Chimala", "Igurusi", "Ubaruku", "Mahongole",
                      "Utengule Usangu", "Madibira"],
    "Mbeya|Busokelo": ["Lwangwa", "Kandete", "Itete", "Lupata", "Isange", "Kabula"],
    # ---------------- Songwe ----------------
    "Songwe|Tunduma (TC)": ["Tunduma", "Mpemba", "Chapwa", "Ntungwa", "Mwanjelwa"],
    "Songwe|Mbozi": ["Vwawa", "Iyula", "Mlowo", "Isansa", "Ihanda",
                     "Nambinzo", "Halungu", "Msia"],
    "Songwe|Momba": ["Chitete", "Ndalambo", "Kamsamba", "Msangano", "Ivuna",
                     "Nkangamo", "Myunga"],
    "Songwe|Ileje": ["Itumba", "Isongole", "Luswisi", "Ikinga", "Bupigu",
                     "Malangali", "Sange"],
    "Songwe|Songwe": ["Mkwajuni", "Galula", "Mbangala", "Namkukwe", "Saza", "Totowe"],
    # ---------------- Iringa ----------------
    "Iringa|Iringa (MC)": ["Mkwawa", "Kihesa", "Mtwivila", "Mlandege", "Kitwiru",
                           "Mivinjeni", "Ruaha", "Gangilonga", "Nduli"],
    "Iringa|Iringa": ["Kalenga", "Ismani", "Idodi", "Nduli", "Mlolo",
                      "Mgama", "Wasa", "Maboga"],
    "Iringa|Mufindi": ["Mafinga", "Sadani", "Ifwagi", "Kibengu", "Igowole",
                       "Malangali", "Mtwango", "Nyololo"],
    "Iringa|Kilolo": ["Kilolo", "Ilula", "Mtitu", "Ukumbi", "Ruaha Mbuyuni",
                      "Idete", "Mahenge"],
    "Iringa|Mafinga (TC)": ["Mafinga Mjini", "Bumilayinga", "Rungemba", "Upendo", "Ifingo"],
    # ---------------- Njombe ----------------
    "Njombe|Njombe (TC)": ["Njombe Mjini", "Mjimwema", "Ramadhani", "Uwemba",
                           "Yakobi", "Matola", "Luponde"],
    "Njombe|Njombe": ["Igominyi", "Lupembe", "Kichiwa", "Mfriga", "Idamba",
                      "Ikondo", "Matembwe"],
    "Njombe|Makete": ["Makete", "Bulongwa", "Iwawa", "Lupalilo", "Ipepo",
                      "Mang'oto", "Kipagalo"],
    "Njombe|Ludewa": ["Ludewa", "Mlangali", "Mavanga", "Lupanga", "Manda",
                      "Mawengi", "Lugarawa"],
    "Njombe|Wanging'ombe": ["Wanging'ombe", "Igwachanya", "Ilembula", "Imalinyi",
                            "Ulembwe", "Saja", "Kijombe"],
    "Njombe|Makambako (TC)": ["Makambako", "Mahongole", "Ubena", "Kitandililo",
                              "Utengule", "Mlowa"],
    # ---------------- Lindi ----------------
    "Lindi|Lindi (MC)": ["Mikumbi", "Rasbura", "Mitandi", "Msinjahili", "Ndoro",
                         "Matopeni", "Wailes", "Jamhuri"],
    "Lindi|Lindi": ["Nyangao", "Mchinga", "Kiwawa", "Mnolela", "Rutamba",
                    "Sudi", "Milola"],
    "Lindi|Kilwa": ["Kilwa Masoko", "Kivinje", "Njinjo", "Miteja", "Kipatimu",
                    "Somanga", "Nanjirinji"],
    "Lindi|Nachingwea": ["Nachingwea", "Mbondo", "Naipanga", "Mkoka", "Kilimarondo",
                         "Ruponda", "Namapwia"],
    "Lindi|Liwale": ["Liwale Mjini", "Mlembwe", "Kibutuka", "Mbaya", "Mkutano",
                     "Ngongowele", "Nangano"],
    "Lindi|Ruangwa": ["Ruangwa", "Nandagala", "Chienjere", "Namichiga", "Mandawa",
                      "Nkowe", "Likunja"],
    "Lindi|Mtama": ["Mtama", "Mnara", "Chiponda", "Namangale", "Kitomanga", "Mipingo"],
    # ---------------- Mtwara ----------------
    "Mtwara|Mtwara (MC)": ["Shangani", "Chikongola", "Magomeni", "Likombe", "Ufukoni",
                           "Rahaleo", "Naliendele", "Mitengo", "Chuno"],
    "Mtwara|Mtwara": ["Nanyamba", "Mayanga", "Ziwani", "Mahurunga", "Dihimba",
                      "Msimbati", "Kitaya"],
    "Mtwara|Masasi (TC)": ["Masasi Mjini", "Mkuti", "Mwenge", "Mumbaka", "Chikundi"],
    "Mtwara|Masasi": ["Nangoo", "Chiungutwa", "Namajani", "Lisekese", "Mkululu",
                      "Mbuyuni", "Namalenga"],
    "Mtwara|Newala (TC)": ["Newala Mjini", "Mkwiti", "Luchingu", "Mnyambe", "Mtopwa"],
    "Mtwara|Newala": ["Kitangari", "Chilangala", "Mahuta", "Mkoma", "Nanguruwe",
                      "Chihangu", "Malatu"],
    "Mtwara|Tandahimba": ["Tandahimba", "Mahuta", "Litehu", "Mkoreha", "Namikupa",
                          "Milongodi", "Ngoji"],
    "Mtwara|Nanyumbu": ["Mangaka", "Nanyumbu", "Mkonona", "Michiga", "Maratani",
                        "Nangomba", "Chipuputa"],
    "Mtwara|Nanyamba (TC)": ["Nanyamba", "Kitama", "Njengwa", "Mnima", "Hinju"],
    # ---------------- Ruvuma ----------------
    "Ruvuma|Songea (MC)": ["Ruhuwiko", "Bombambili", "Mfaranyaki", "Lizaboni",
                           "Mshangano", "Majengo", "Ruvuma", "Mjimwema"],
    "Ruvuma|Songea": ["Peramiho", "Mpitimbi", "Madaba", "Litisha", "Gumbiro",
                      "Mgazini", "Luhira"],
    "Ruvuma|Mbinga (TC)": ["Mbinga Mjini", "Mpepai", "Kigonsera", "Litembo", "Utiri"],
    "Ruvuma|Mbinga": ["Mbamba Bay", "Mkumbi", "Kihagara", "Ruanda", "Mapera",
                      "Kilimani", "Mbuji"],
    "Ruvuma|Tunduru": ["Tunduru Mjini", "Nalasi", "Mchoteka", "Nampungu", "Mtina",
                       "Matemanga", "Namasakata"],
    "Ruvuma|Namtumbo": ["Namtumbo", "Mkongo", "Ligera", "Mchomoro", "Msindo",
                        "Hanga", "Lusewa"],
    "Ruvuma|Nyasa": ["Mbamba Bay", "Kilosa", "Lituhi", "Mpepo", "Chiwanda",
                     "Liuli", "Ngumbo"],
    "Ruvuma|Madaba": ["Madaba", "Gumbiro", "Mpitimbi", "Lipumburu", "Matimira"],
}


def ward_key(region, district, kind):
    """
    Tafuta ufunguo wa kata. Halmashauri zenye jina moja (mfano Korogwe TC na
    Korogwe DC) zinatofautishwa kwa aina.
    """
    with_kind = f"{region}|{district} ({kind})"
    if with_kind in WARDS:
        return with_kind
    plain = f"{region}|{district}"
    return plain if plain in WARDS else None
