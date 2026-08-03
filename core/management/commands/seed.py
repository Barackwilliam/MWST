"""
Jaza database na data za mfano zinazolingana na muundo wa dashboards.

Endesha:  python manage.py seed
Kufuta na kuanza upya:  python manage.py seed --fresh
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import Role
from content.models import (Album, Announcement, Faq, Leader, MediaItem, Milestone,
                            News, NewsCategory, Pillar, Service, SiteSetting, Verse)
from finance.models import (Account, Campaign, Contribution, Donor, Expense, Fund,
                            Payment, PaymentMethod, PaymentStatus, Project)
from geo.models import Branch, District, Region, Ward, Zone
from geo import tanzania as tz
from members.models import (Application, ApplicationStatus, Card, Category, Member,
                            MemberStatus)
from programs.models import (AssistanceType, Event, EventRegistration, EventType,
                             PointRule, PointTransaction, Reward)

User = get_user_model()
random.seed(2026)

#: Idadi ya juu ya rekodi kwa kila sehemu ya data za mfano.
#: Data za msingi (mikoa, kategoria, mifuko, kanuni za pointi) hazipo hapa —
#: hizo ni mipangilio halisi, si data za majaribio.
LIMIT = 20

FIRST = ["Mohammed", "Aisha", "Juma", "Fatma", "Salim", "Hawa", "Abdul", "Zainab",
         "Yusuf", "Rehema", "Ali", "Mariam", "Hamisi", "Asha", "Said", "Halima",
         "Ibrahim", "Khadija", "Omari", "Amina", "Rashid", "Zuhura", "Bakari", "Neema"]
MIDDLE = ["K.", "M.", "S.", "H.", "A.", "R.", "J.", "O."]
LAST = ["Abdallah", "Salum", "Kapera", "Ali", "Hassan", "Juma", "Said", "Omar",
        "Simba", "Rashid", "Mwinyi", "Nassor", "Suleiman", "Khamis", "Mkuu", "Mbwana"]


def name():
    return f"{random.choice(FIRST)} {random.choice(MIDDLE)} {random.choice(LAST)}"


class Command(BaseCommand):
    help = "Jaza database na data za mfano"

    def add_arguments(self, parser):
        parser.add_argument("--fresh", action="store_true", help="Futa data zote kwanza")
        parser.add_argument("--limit", type=int, default=LIMIT,
                            help=f"Idadi ya juu kwa kila sehemu (chaguo-msingi: {LIMIT})")
        parser.add_argument("--mikoa-yote", action="store_true",
                            help="Weka mikoa yote 26 ya Tanzania (kwa matumizi halisi)")

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts["fresh"]:
            self.stdout.write("Inafuta data za zamani...")
            for model in (PointTransaction, EventRegistration, Event, Contribution, Payment,
                          Expense, Campaign, Project, Donor, Card, Application, Member,
                          Account, News, MediaItem, Album, Announcement):
                model.objects.all().delete()

        n = max(opts["limit"], 1)
        self.settings()
        self.verses()
        self.geo(None if opts["mikoa_yote"] else n)
        self.categories()
        self.funds()
        self.point_rules()
        self.staff()
        self.site_content()
        self.projects_campaigns()
        members = self.members(n)
        self.applications(n)
        # Leja hupata ingizo moja kwa kila malipo/mchango uliothibitishwa.
        # Kugawa kikomo kunazuia leja kuzidi 20.
        self.payments(members, n // 2)
        self.contributions(members, n - n // 2)
        self.events(members, n)
        self.media(n)
        self.news(n)
        # Ruhusa za /usimamizi/ kwa kila jukumu
        from django.core.management import call_command
        call_command("ruhusa", verbosity=0)
        self.stdout.write("  ruhusa za makundi")
        self.stdout.write(self.style.SUCCESS("\nData za mfano zimekamilika."))
        self.stdout.write("Watumiaji: admin/mwst2026, usajili/mwst2026, malipo/mwst2026, "
                          "michango/mwst2026, wadau/mwst2026, mwanachama/mwst2026")

    # ------------------------------------------------------------------
    def settings(self):
        s = SiteSetting.get()
        s.about = ("Tunatekeleza huduma za kijamii, kiuchumi na kiimani kwa mujibu wa "
                   "maadili ya Kiislamu kwa maendeleo ya jamii na ustawi wa binadamu.")
        s.about_en = ("We deliver social, economic and faith-based services in line with "
                      "Islamic values, for community development and human welfare.")
        s.phone_alt = "+255 754 321 654"
        s.email_alt = "msaada@muslimwelfare.or.tz"
        s.tagline_en = "Faith in Action, Service and Development for Humanity"
        s.address_en = "Nkuhungu, Dodoma, Tanzania"
        s.working_hours_en = "Monday - Friday: 08:00 - 17:00"
        s.fundraising_target = Decimal("2000000000")
        s.save()
        self.stdout.write("  mipangilio")

    def verses(self):
        data = [
            ("وَتَعَاوَنُوا۟ عَلَى ٱلْبِرِّ وَٱلتَّقْوَىٰ", "Na msaidiane katika heri na taqwa.",
             "And cooperate in righteousness and piety.", "Al-Ma'idah: 2"),
            ("وَمَا تُقَدِّمُوا۟ لِأَنفُسِكُم مِّنْ خَيْرٍ تَجِدُوهُ عِندَ ٱللَّهِ",
             "Na kheri yoyote mnayoitanguliza kwa ajili yenu, mtaikuta kwa Allah.",
             "And whatever good you put forward for yourselves, you will find it with Allah.",
             "Al-Baqarah: 110"),
        ]
        for i, (ar, sw, en, ref) in enumerate(data):
            Verse.objects.get_or_create(reference=ref, defaults={
                "arabic": ar, "swahili": sw, "swahili_en": en, "order": i})
        self.stdout.write("  aya")

    def geo(self, limit=None):
        """
        Jiografia halisi ya Tanzania Bara: kanda 6, mikoa 26,
        halmashauri 184 na kata zaidi ya 1,300.

        Data hizi si za mfano — ni mgawanyo halisi wa kiutawala.
        `limit` haitumiki hapa; jiografia daima inawekwa kwa ukamilifu.
        """
        # ---- Kanda ----
        zones = {}
        for nm, en, code, office, order in tz.ZONES:
            z, _c = Zone.objects.get_or_create(code=code, defaults={
                "name": nm, "name_en": en, "office": office, "order": order})
            zones[code] = z

        # ---- Mikoa, halmashauri na kata ----
        n_d = n_w = 0
        for i, (nm, x, y) in enumerate(tz.REGIONS):
            region, _c = Region.objects.get_or_create(name=nm, defaults={
                "map_x": x, "map_y": y, "order": i})
            zone = zones.get(tz.REGION_ZONE.get(nm))
            if region.zone_id != getattr(zone, "pk", None):
                region.zone = zone
                region.save(update_fields=["zone"])

            for dname, kind in tz.DISTRICTS.get(nm, []):
                district, _c = District.objects.get_or_create(
                    region=region, name=dname, kind=kind)
                n_d += 1
                key = tz.ward_key(nm, dname, kind)
                for wname in (tz.WARDS.get(key, []) if key else []):
                    Ward.objects.get_or_create(district=district, name=wname)
                    n_w += 1

        self.stdout.write(f"  kanda {Zone.objects.count()}, mikoa {Region.objects.count()}, "
                          f"halmashauri {n_d}, kata {n_w}")
        self.branches()

    def branches(self):
        """Ofisi kuu na ofisi ya kila kanda."""
        dodoma = Region.objects.get(name="Dodoma")
        Branch.objects.get_or_create(name="Ofisi Kuu - Dodoma", defaults={
            "region": dodoma, "address": "Nkuhungu, Dodoma",
            "phone": "+255 769 600 102", "is_head_office": True})

        # Ofisi moja kwa kila kanda
        offices = {
            "mashariki": ("Ofisi ya Kanda ya Mashariki", "Dar es Salaam",
                          "Kinondoni, Dar es Salaam", "+255 754 321 654"),
            "kaskazini": ("Ofisi ya Kanda ya Kaskazini", "Arusha",
                          "Arusha Mjini, Arusha", "+255 786 445 201"),
            "ziwa": ("Ofisi ya Kanda ya Ziwa", "Mwanza",
                     "Ilemela, Mwanza", "+255 762 118 990"),
            "kati": ("Ofisi ya Kanda ya Kati", "Dodoma",
                     "Nkuhungu, Dodoma", "+255 769 600 102"),
            "magharibi": ("Ofisi ya Kanda ya Magharibi", "Kigoma",
                          "Kigoma-Ujiji, Kigoma", "+255 767 220 118"),
            "kusini": ("Ofisi ya Kanda ya Kusini", "Mbeya",
                       "Mbeya Jiji, Mbeya", "+255 758 909 442"),
        }
        for code, (nm, rg, addr, ph) in offices.items():
            region = Region.objects.filter(name=rg).first()
            if region:
                Branch.objects.get_or_create(name=nm, defaults={
                    "region": region, "address": addr, "phone": ph})

    def categories(self):
        data = [
            ("Bronze", "B", 5000, 10, "#b45309", 0, False,
             "Kadi ya kidijitali\nAkaunti binafsi\nTaarifa na matangazo\nPointi 10 kwa kila malipo",
             "Digital card\nPersonal account\nNews and announcements\n10 points per payment"),
            ("Silver", "S", 10000, 25, "#64748b", 1, False,
             "Faida zote za Bronze\nMsaada wa ustawi\nAlika kwenye mafunzo\nPointi 25 kwa kila malipo",
             "All Bronze benefits\nWelfare support\nTraining invitations\n25 points per payment"),
            ("Gold", "G", 20000, 50, "#a9812a", 2, True,
             "Faida zote za Silver\nKipaumbele kwenye misaada\nCheti cha uanachama\n"
             "Pointi 50 kwa kila malipo\nHaki ya kupiga kura",
             "All Silver benefits\nPriority for assistance\nMembership certificate\n"
             "50 points per payment\nVoting rights"),
            ("Platinum", "P", 50000, 150, "#6d28d9", 3, False,
             "Faida zote za Gold\nUtambulisho kwenye ripoti ya mwaka\nUshauri wa kifedha\n"
             "Pointi 150 kwa kila malipo\nNafasi kwenye kamati",
             "All Gold benefits\nRecognition in the annual report\nFinancial advisory\n"
             "150 points per payment\nA seat on committees"),
            ("Tanzanite", "T", 100000, 200, "#1b3b6f", 4, False,
             "Faida zote za Platinum\nUtambulisho wa kudumu kwenye ukumbi wa heshima\n"
             "Nafasi kwenye Bodi ya Wadhamini\nKadi maalum ya Tanzanite\n"
             "Mwaliko kwenye mikutano ya uongozi",
             "All Platinum benefits\nPermanent recognition in the hall of honour\n"
             "A seat on the Board of Trustees\nSpecial Tanzanite card\n"
             "Invitation to leadership meetings"),
        ]
        for nm, code, fee, pts, col, order, feat, ben, ben_en in data:
            # Tanzanite ni daraja la heshima — mwombaji hawezi kulichagua.
            # Msimamizi ndiye humpandisha mwanachama huko.
            special = code == "T"
            Category.objects.update_or_create(code=code, defaults={
                "name": nm, "name_en": nm, "monthly_fee": fee, "points_per_payment": pts,
                "colour": col, "order": order, "is_featured": feat,
                "is_selectable": not special, "is_special": special,
                "benefits": ben, "benefits_en": ben_en})
        self.stdout.write("  kategoria 5")

    def funds(self):
        data = [
            ("Ada za Uanachama", "Membership Fees", "ada", False, "#12864a", "wallet", 0, 6450000000),
            ("Michango ya Hiari", "Voluntary Contributions", "hiari", False, "#1b3b6f", "hand-heart", 1, 2125000000),
            ("Zaka", "Zakat", "zaka", True, "#6d28d9", "coins", 2, 1520000000),
            ("Sadaqa", "Sadaqah", "sadaqa", False, "#d4af37", "heart", 3, 850000000),
            ("Waqf", "Waqf", "waqf", True, "#0891b2", "mosque", 4, 620000000),
            ("Miradi", "Projects", "miradi", True, "#ea580c", "building", 5, 1845320000),
            ("Fitrah", "Fitrah", "fitrah", True, "#4cbd83", "gift", 6, 180000000),
            ("Kafara", "Kafara", "kafara", True, "#dc2626", "star", 7, 120000000),
            ("Dharura", "Emergency", "dharura", False, "#b45309", "alert", 8, 300000000),
        ]
        for nm, en, code, restricted, col, icon, order, target in data:
            Fund.objects.get_or_create(code=code, defaults={
                "name": nm, "name_en": en, "is_restricted": restricted, "colour": col,
                "icon": icon, "order": order, "annual_target": target})
        self.stdout.write("  mifuko 9")

    def point_rules(self):
        data = [
            ("payment_on_time", "Kulipa ada kwa wakati", "Paying fees on time", 10, 0),
            ("full_year", "Mwaka mmoja bila kukatiza", "One uninterrupted year", 100, 1),
            ("donation", "Mchango wa hiari", "Voluntary contribution", 1, 2),
            ("volunteer", "Kujitolea kwenye shughuli", "Volunteering", 50, 3),
            ("agm", "Kuhudhuria Mkutano Mkuu", "Attending the AGM", 20, 4),
            ("referral", "Kumleta mwanachama mpya", "Referring a new member", 50, 5),
            ("training", "Kuhudhuria mafunzo au semina", "Attending training or a seminar", 15, 6),
        ]
        for code, sw, en, pts, order in data:
            PointRule.objects.get_or_create(code=code, defaults={
                "activity": sw, "activity_en": en, "points": pts, "order": order})
        for t, en, p in [("Cheti cha Utambulisho", "Recognition Certificate", 1000),
                         ("Nembo ya Dhahabu", "Gold Badge", 2500),
                         ("Safari ya Umrah", "Umrah Trip", 5000)]:
            Reward.objects.get_or_create(title=t, defaults={"title_en": en, "points_required": p})
        for t, en in [("Matibabu", "Medical"), ("Elimu", "Education"),
                      ("Dharura", "Emergency"), ("Chakula", "Food"), ("Makazi", "Housing")]:
            AssistanceType.objects.get_or_create(name=t, defaults={"name_en": en})
        self.stdout.write("  kanuni za pointi 7")

    def staff(self):
        dodoma = Region.objects.filter(name="Dodoma").first()
        hq = Branch.objects.filter(is_head_office=True).first()
        people = [
            ("admin", "Ali H.", "Suleiman", Role.SUPER_ADMIN, True),
            ("usimamizi", "Zainab K.", "Omar", Role.MANAGEMENT, False),
            ("usajili", "Fatma H.", "Ali", Role.REGISTRATION, False),
            ("malipo", "Juma K.", "Abdallah", Role.FINANCE, False),
            ("michango", "Salim R.", "Hassan", Role.CONTRIBUTIONS, False),
            ("ustawi", "Hawa M.", "Juma", Role.WELFARE, False),
            ("wadau", "Abdul A.", "Said", Role.OUTREACH, False),
        ]
        for un, fn, ln, role, is_su in people:
            u, _created = User.objects.get_or_create(username=un, defaults={
                "first_name": fn, "last_name": ln, "role": role,
                "email": f"{un}@muslimwelfare.or.tz", "phone": "+255 769 600 102",
                "region": dodoma, "branch": hq,
                "is_staff": True, "is_superuser": is_su})
            # Nenosiri linawekwa kila mara ili kuendesha seed tena kurekebishe
            # akaunti zilizoharibika badala ya kuziacha kama zilivyo.
            u.set_password("mwst2026")
            u.is_active = True
            u.save()
        # ---- Mratibu mmoja kwa kila kanda ----
        coordinators = [
            ("mratibu.mashariki", "Yusuf M.", "Simba", "mashariki"),
            ("mratibu.kaskazini", "Rehema S.", "Mbwana", "kaskazini"),
            ("mratibu.ziwa", "Bakari J.", "Nassor", "ziwa"),
            ("mratibu.kati", "Amina O.", "Khamis", "kati"),
            ("mratibu.magharibi", "Ibrahim A.", "Mkuu", "magharibi"),
            ("mratibu.kusini", "Khadija R.", "Mwinyi", "kusini"),
        ]
        for un, fn, ln, zone_code in coordinators:
            zone = Zone.objects.filter(code=zone_code).first()
            home = zone.regions.first() if zone else None
            u, _created = User.objects.get_or_create(username=un, defaults={
                "first_name": fn, "last_name": ln, "role": Role.COORDINATOR,
                "email": f"{zone_code}@muslimwelfare.or.tz",
                "phone": "+255 769 600 102", "region": home, "is_staff": True})
            u.set_password("mwst2026")
            u.role = Role.COORDINATOR
            u.region = home
            u.is_active = True
            u.is_staff = True
            u.save()
            if zone:
                zone.coordinator = u
                zone.save(update_fields=["coordinator"])

        self.stdout.write(f"  watumishi {len(people)}, waratibu {len(coordinators)}")

    def site_content(self):
        for t, ten, b, ben, icon, tint, o in [
            ("Dira Yetu", "Our Vision",
             "Kuwa jumuiya kinara ya huduma za kijamii Tanzania, inayoaminika na kuchangia "
             "maendeleo endelevu ya binadamu.",
             "To be Tanzania's leading community service organisation — trusted and "
             "contributing to sustainable human development.", "target", "green", 0),
            ("Dhamira Yetu", "Our Mission",
             "Kutoa huduma za elimu, afya, ustawi na uwezeshaji kiuchumi kwa mujibu wa "
             "maadili ya Kiislamu, bila ubaguzi.",
             "To provide education, health, welfare and economic empowerment services in "
             "line with Islamic values, without discrimination.", "heart", "navy", 1),
            ("Maadili Yetu", "Our Values",
             "Imani, Huruma, Huduma na Maendeleo. Haya ndiyo yanayoongoza kila uamuzi na "
             "kila huduma tunayoitoa.",
             "Faith, Compassion, Service and Development. These guide every decision and "
             "every service we deliver.", "shield", "gold", 2),
        ]:
            Pillar.objects.get_or_create(title=t, defaults={
                "title_en": ten, "body": b, "body_en": ben, "icon": icon, "tint": tint, "order": o})

        for y, t, ten, b, ben, o in [
            ("2015", "Kuanzishwa kwa MWST", "MWST Founded",
             "Jumuiya ilianzishwa Dodoma na wanachama waanzilishi 42 wenye lengo la kusaidia jamii.",
             "The society was founded in Dodoma by 42 founding members aiming to serve the community.", 0),
            ("2018", "Upanuzi wa Kitaifa", "National Expansion",
             "MWST ilifungua matawi katika mikoa 12 na kuanzisha mfumo wa uanachama wa kudumu.",
             "MWST opened branches in 12 regions and established a permanent membership system.", 1),
            ("2021", "Miradi ya Elimu na Afya", "Education and Health Projects",
             "Ujenzi wa shule tatu na vituo viwili vya afya ulikamilika katika mikoa ya kati.",
             "Three schools and two health centres were completed in the central regions.", 2),
            ("2024", "Mpango wa Ustawi wa Yatima", "Orphan Welfare Programme",
             "Mpango wa kudumu wa kusaidia yatima na wajane ulizinduliwa katika mikoa yote.",
             "A permanent programme supporting orphans and widows was launched across all regions.", 3),
            ("2026", "Mfumo wa Kidijitali", "Digital System",
             "Uzinduzi wa mfumo wa kidijitali wa usimamizi wa uanachama, malipo na michango.",
             "Launch of the digital system for managing membership, payments and contributions.", 4),
        ]:
            Milestone.objects.get_or_create(year=y, title=t, defaults={
                "title_en": ten, "body": b, "body_en": ben, "order": o})

        for n, r, ren, o in [("Mohammed Omari Kapera", "Mwenyekiti", "Chairperson", 0),
                             ("Ali H. Suleiman", "Katibu Mkuu", "Secretary General", 1),
                             ("Fatma H. Ali", "Mweka Hazina", "Treasurer", 2),
                             ("Juma K. Abdallah", "Afisa Miradi", "Projects Officer", 3)]:
            Leader.objects.get_or_create(full_name=n, defaults={"role": r, "role_en": ren, "order": o})

        for t, ten, s, sen, stat, staten, icon, tint, scene, cat, o in [
            ("Elimu na Mafunzo", "Education and Training",
             "Ufadhili wa masomo, ujenzi wa madarasa, vifaa vya shule na mafunzo ya ufundi kwa vijana.",
             "Scholarships, classroom construction, school supplies and vocational training for young people.",
             "1,240 wanafunzi wamefadhiliwa", "1,240 students sponsored", "book", "green", "elimu", "elimu", 0),
            ("Huduma za Afya", "Health Services",
             "Kambi za upimaji afya bure, msaada wa matibabu, na ujenzi wa vituo vya afya vijijini.",
             "Free health screening camps, medical assistance and rural health centre construction.",
             "18 kambi za afya mwaka huu", "18 health camps this year", "heart", "red", "afya", "afya", 1),
            ("Ustawi wa Jamii", "Community Welfare",
             "Msaada kwa yatima, wajane, wazee na familia zilizoathirika na majanga.",
             "Support for orphans, widows, the elderly and families affected by disasters.",
             "2,450 wanufaika kwa mwezi", "2,450 beneficiaries per month", "hand-heart", "navy", "yatima", "ustawi", 2),
            ("Maji Safi na Salama", "Clean and Safe Water",
             "Uchimbaji wa visima na ujenzi wa miundombinu ya maji katika maeneo yenye uhaba.",
             "Borehole drilling and water infrastructure in areas facing shortages.",
             "34 visima vimechimbwa", "34 boreholes drilled", "globe", "teal", "maji", "miradi", 3),
            ("Uwezeshaji Kiuchumi", "Economic Empowerment",
             "Mikopo midogo, mafunzo ya ujasiriamali na vikundi vya akiba kwa wanawake na vijana.",
             "Microloans, entrepreneurship training and savings groups for women and youth.",
             "860 wajasiriamali wamewezeshwa", "860 entrepreneurs supported", "briefcase", "gold", "uchumi", "uchumi", 4),
            ("Ujenzi wa Vituo vya Ibada", "Building Places of Worship",
             "Ujenzi na ukarabati wa misikiti, madrasa na vituo vya elimu ya dini.",
             "Construction and renovation of mosques, madrasas and religious education centres.",
             "12 miradi imekamilika", "12 projects completed", "mosque", "purple", "msikiti", "miradi", 5),
        ]:
            Service.objects.get_or_create(title=t, defaults={
                "title_en": ten, "summary": s, "summary_en": sen, "stats_line": stat,
                "stats_line_en": staten, "icon": icon, "tint": tint, "scene": scene,
                "category": cat, "order": o})

        faqs = [
            ("kuhusu", "MWST ni nini?", "What is MWST?",
             "MWST ni jumuiya ya kijamii isiyo ya kiserikali inayotoa huduma za elimu, afya, "
             "ustawi na uwezeshaji kiuchumi kwa jamii ya Watanzania.",
             "MWST is a non-governmental community organisation providing education, health, "
             "welfare and economic empowerment services to Tanzanian communities."),
            ("kuhusu", "Je, ni lazima uwe Mwislamu kupata huduma?",
             "Do you have to be Muslim to receive services?",
             "Hapana. Huduma zetu zinatolewa kwa kila mwenye uhitaji bila kujali dini, kabila "
             "au eneo analotoka.",
             "No. Our services are open to anyone in need, regardless of religion, ethnicity or location."),
            ("kuhusu", "Fedha za jumuiya zinatoka wapi?", "Where does the society's funding come from?",
             "Kutoka ada za wanachama, michango ya hiari, Zaka, Sadaqa, Waqf na ufadhili wa "
             "mashirika washirika ya ndani na kimataifa.",
             "From membership fees, voluntary contributions, Zakat, Sadaqah, Waqf and funding "
             "from local and international partner organisations."),
            ("kuhusu", "Nawezaje kufuatilia matumizi ya michango yangu?",
             "How can I track how my contributions are used?",
             "Kila mwanachama ana akaunti kwenye mfumo inayoonyesha michango yake yote na "
             "ripoti za matumizi zinachapishwa kila mwaka.",
             "Every member has an account showing all their contributions, and expenditure "
             "reports are published annually."),
            ("mawasiliano", "Nawezaje kujiunga na MWST?", "How do I join MWST?",
             "Tembelea ukurasa wa Uanachama, jaza fomu ya mtandaoni, chagua aina ya uanachama "
             "na ulipe ada. Utapokea namba ya uanachama na kadi ya kidijitali.",
             "Visit the Membership page, complete the online form, choose a tier and pay the "
             "fee. You will receive a membership number and digital card."),
            ("mawasiliano", "Naomba msaada wa ustawi, nifanyeje?",
             "How do I request welfare assistance?",
             "Wanachama wanaweza kuomba kupitia akaunti zao. Wasio wanachama wanaweza "
             "kuwasiliana na ofisi ya tawi lililo karibu nao.",
             "Members can apply through their account. Non-members should contact their "
             "nearest branch office."),
            ("mawasiliano", "Nataka kuchangia mradi maalum, inawezekana?",
             "Can I contribute to a specific project?",
             "Ndiyo. Unaweza kuchagua mradi unaotaka kuufadhili wakati wa kutoa mchango, na "
             "utapokea ripoti ya matumizi.",
             "Yes. You can choose which project to fund when contributing, and you will "
             "receive an expenditure report."),
            ("mawasiliano", "Mnapokea wafadhili wa kimataifa?", "Do you accept international donors?",
             "Ndiyo. Tunashirikiana na mashirika ya kimataifa. Wasiliana na ofisi kuu kwa "
             "taratibu za makubaliano.",
             "Yes. We partner with international organisations. Contact the head office for "
             "agreement procedures."),
        ]
        for i, (page, q, qen, a, aen) in enumerate(faqs):
            Faq.objects.get_or_create(question=q, defaults={
                "question_en": qen, "answer": a, "answer_en": aen, "page": page, "order": i})
        self.stdout.write("  maudhui ya tovuti")

    def projects_campaigns(self):
        data = [
            ("Ujenzi wa Shule ya Sekondari", "Secondary School Construction", "Dodoma",
             "ongoing", 12000000, "ujenzi"),
            ("Ujenzi wa Kituo cha Afya", "Health Centre Construction", "Singida",
             "ongoing", 9000000, "afya"),
            ("Msaada wa Wajane na Yatima", "Widows and Orphans Support", "Dar es Salaam",
             "ongoing", 8000000, "yatima"),
            ("Visima vya Maji Safi", "Clean Water Boreholes", "Dodoma", "ongoing", 6500000, "maji"),
            ("Masjid na Vituo vya Ibada", "Mosques and Prayer Centres", "Morogoro",
             "completed", 5000000, "msikiti"),
        ]
        for t, ten, rg, st, target, scene in data[:LIMIT]:
            Project.objects.get_or_create(title=t, defaults={
                "title_en": ten, "region": Region.objects.filter(name=rg).first(),
                "status": st, "target_amount": target, "scene": scene})
        today = timezone.localdate()
        camps = [
            ("Ujenzi wa Shule ya Msingi", "Primary School Construction", 200000000, 45, "ujenzi"),
            ("Maji Safi kwa Jamii", "Clean Water for the Community", 150000000, 30, "maji"),
            ("Wafadhili wa Yatima", "Orphan Sponsorship", 120000000, 52, "yatima"),
            ("Msaada wa Dharura", "Emergency Relief", 80000000, 20, "sadaka"),
        ]
        for t, ten, target, days, scene in camps[:LIMIT]:
            Campaign.objects.get_or_create(title=t, defaults={
                "title_en": ten, "target_amount": target, "scene": scene,
                "end_date": today + timedelta(days=days),
                "fund": Fund.objects.get(code="miradi")})

        donors = [
            ("Muslim Aid International", "organisation", True, 328500000),
            ("Islamic Relief Worldwide", "organisation", True, 245700000),
            ("Amaan Foundation", "organisation", True, 156300000),
            ("Hassan & Family Foundation", "organisation", False, 98650000),
            ("Al-Barakah Charity Org.", "organisation", True, 76400000),
            ("Baraka Group Ltd", "company", True, 42000000),
            ("Alh. Said Salim", "individual", False, 18000000),
            ("Abdallah Nassor", "individual", False, 9500000),
        ]
        regions = list(Region.objects.all()[:6])
        for nm, typ, partner, _amt in donors[:LIMIT]:
            Donor.objects.get_or_create(name=nm, defaults={
                "donor_type": typ, "is_partner": partner,
                "region": random.choice(regions)})
        self.stdout.write("  miradi, kampeni, wahisani")

    def members(self, count):
        cats = list(Category.objects.all())
        weights = [45, 32, 17, 5, 1]
        regions = list(Region.objects.all())
        today = timezone.localdate()
        created = []
        for i in range(count):
            cat = random.choices(cats, weights=weights)[0]
            region = random.choices(regions, weights=[r.order + 1 for r in regions][::-1])[0]
            district = random.choice(list(region.districts.all())) if region.districts.exists() else None
            joined = today - timedelta(days=random.randint(1, 900))
            status = random.choices(
                [MemberStatus.ACTIVE, MemberStatus.SUSPENDED, MemberStatus.EXPIRED],
                weights=[87, 8, 5])[0]
            m = Member.objects.create(
                full_name=name(), gender=random.choice(["male", "female"]),
                date_of_birth=today - timedelta(days=random.randint(7000, 20000)),
                national_id=str(random.randint(19700000000000, 20059999999999)),
                phone=f"07{random.randint(10,89)} {random.randint(100,999)} {random.randint(100,999)}",
                email=f"member{i}@mfano.com", region=region, district=district,
                street="Mtaa wa Mfano", address=f"S.L.P {random.randint(100,9999)}, {region.name}",
                category=cat, status=status, joined_on=joined,
                expires_on=joined.replace(year=joined.year + 5),
            )
            Account.objects.create(member=m)
            Card.issue(m)
            created.append(m)

        # Mwanachama wa mfano wa kuingia
        demo = created[0]
        demo.full_name = "Mohammed Omari Kapera"
        demo.category = Category.objects.get(code="T")
        demo.status = MemberStatus.ACTIVE
        demo.email = "mohammed.kapera@gmail.com"
        demo.phone = "0769 600 102"
        demo.national_id = "19901234567890"
        demo.save()
        u, _created_u = User.objects.get_or_create(username="mwanachama", defaults={
            "first_name": "Mohammed", "last_name": "Kapera", "role": Role.MEMBER,
            "email": demo.email, "phone": demo.phone})
        u.set_password("mwst2026")
        u.role = Role.MEMBER
        u.is_active = True
        u.save()
        # Ondoa uhusiano wa zamani kabla ya kuunganisha upya (OneToOne)
        Member.objects.filter(user=u).exclude(pk=demo.pk).update(user=None)
        demo.user = u
        demo.save(update_fields=["user"])
        self.stdout.write(f"  wanachama {len(created)}")
        return created

    def applications(self, limit):
        cats = list(Category.objects.all())
        regions = list(Region.objects.all()[:8])
        # Mchanganyiko wa hali, kisha kata kufikia kikomo
        pool = ([ApplicationStatus.PENDING] * 6 + [ApplicationStatus.APPROVED] * 3 +
                [ApplicationStatus.REVIEW] * 2 + [ApplicationStatus.REJECTED] * 1)
        statuses = (pool * ((limit // len(pool)) + 1))[:limit]
        for st in statuses:
            r = random.choice(regions)
            Application.objects.create(
                full_name=name(), phone=f"07{random.randint(10,89)} {random.randint(100,999)} {random.randint(100,999)}",
                email="maombi@mfano.com", region=r,
                district=random.choice(list(r.districts.all())) if r.districts.exists() else None,
                category=random.choice(cats), status=st)
        self.stdout.write(f"  maombi {Application.objects.count()}")

    def payments(self, members, limit):
        ada = Fund.objects.get(code="ada")
        methods = [PaymentMethod.MPESA] * 5 + [PaymentMethod.BANK] * 4 + \
                  [PaymentMethod.TIGO] * 2 + [PaymentMethod.AIRTEL] * 2 + [PaymentMethod.CASH]
        banks = ["CRDB", "NMB", "NBC", "CRDB"]
        now = timezone.now()
        n = 0
        for m in members:
            if n >= limit:
                break
            for _ in range(random.randint(1, 3)):
                if n >= limit:
                    break
                when = now - timedelta(days=random.randint(0, 365), hours=random.randint(0, 20))
                method = random.choice(methods)
                status = random.choices(
                    [PaymentStatus.CONFIRMED, PaymentStatus.PENDING,
                     PaymentStatus.FAILED, PaymentStatus.CANCELLED],
                    weights=[72, 9, 11, 8])[0]
                p = Payment.objects.create(
                    member=m, amount=m.category.monthly_fee, year=when.year,
                    period_month=when.month, method=method,
                    bank_name=random.choice(banks) if method == PaymentMethod.BANK else "",
                    status=status, paid_at=when,
                    reference=f"TX{random.randint(100000, 999999)}")
                if status == PaymentStatus.CONFIRMED:
                    p.post_to_ledger(ada.code)
                n += 1
        self.stdout.write(f"  malipo {n}")

    def contributions(self, members, limit):
        funds = list(Fund.objects.exclude(code="ada"))
        weights = [50, 23, 17, 6, 3, 1, 1, 1][:len(funds)]
        donors = list(Donor.objects.all())
        projects = list(Project.objects.all())
        campaigns = list(Campaign.objects.all())
        now = timezone.now()
        n = 0
        for _ in range(limit):
            when = now - timedelta(days=random.randint(0, 365), hours=random.randint(0, 22))
            use_donor = random.random() < 0.35
            fund = random.choices(funds, weights=weights)[0]
            amount = Decimal(random.choice([50000, 100000, 150000, 200000, 250000,
                                            500000, 750000, 1000000, 1500000,
                                            5000000, 25000000, 50000000]))
            c = Contribution.objects.create(
                fund=fund,
                donor=random.choice(donors) if use_donor else None,
                member=None if use_donor else random.choice(members),
                project=random.choice(projects) if random.random() < 0.4 else None,
                campaign=random.choice(campaigns) if random.random() < 0.5 else None,
                amount=amount,
                method=random.choice([PaymentMethod.MPESA, PaymentMethod.BANK,
                                      PaymentMethod.TIGO, PaymentMethod.AIRTEL]),
                bank_name=random.choice(["CRDB", "NMB", "NBC"]) if random.random() < 0.3 else "",
                status=PaymentStatus.CONFIRMED, received_at=when)
            c.post_to_ledger()
            n += 1
        for fund in list(Fund.objects.all())[:limit]:
            Expense.objects.create(
                fund=fund, title=f"Matumizi ya {fund.name}",
                amount=Decimal(random.randint(2000000, 40000000)),
                spent_on=timezone.localdate() - timedelta(days=random.randint(1, 300)))
        self.stdout.write(f"  michango {n}")

    def events(self, members, limit):
        types = [("Kongamano", "Conference", "kongamano", "#12864a", "tukio"),
                 ("Mafunzo", "Training", "mafunzo", "#2563eb", "elimu"),
                 ("Mikutano", "Meetings", "mikutano", "#6d28d9", "mkutano"),
                 ("Semina", "Seminar", "semina", "#d4af37", "mkutano"),
                 ("Shughuli za Kijamii", "Community Activities", "kijamii", "#0891b2", "jamii"),
                 ("Mahusiano na Jamii", "Community Relations", "mahusiano", "#ea580c", "yatima")]
        for nm, en, slug, col, scene in types:
            EventType.objects.get_or_create(slug=slug, defaults={
                "name": nm, "name_en": en, "colour": col, "scene": scene})
        et = list(EventType.objects.all())
        regions = list(Region.objects.all()[:12])
        now = timezone.now()
        titles = [
            ("Kongamano la Elimu ya Kiislamu", "Islamic Education Conference"),
            ("Mafunzo ya Uongozi kwa Vijana", "Youth Leadership Training"),
            ("Shughuli ya Kuwasaidia Yatima", "Orphan Support Activity"),
            ("Semina ya Uwezeshaji Kiuchumi", "Economic Empowerment Seminar"),
            ("Mkutano Mkuu wa MWST", "MWST Annual General Meeting"),
            ("Ziara ya Miradi", "Project Visit"),
            ("Mkutano na Wadau", "Stakeholder Meeting"),
            ("Mafunzo ya Afya ya Jamii", "Community Health Training"),
            ("Semina ya Elimu ya Wasichana", "Girls' Education Seminar"),
            ("Shughuli ya Msaada wa Chakula", "Food Aid Activity"),
            ("Zoezi la Upimaji Afya Bure", "Free Health Screening"),
            ("Semina ya Uongozi na Maadili", "Leadership and Ethics Seminar"),
        ]
        per_event = max(limit // max(min(len(titles), limit), 1), 1)
        registrations = 0
        for i, (t, ten) in enumerate(titles[:limit]):
            future = i % 2 == 0
            start = now + timedelta(days=random.randint(3, 60)) if future \
                else now - timedelta(days=random.randint(3, 90))
            region = random.choice(regions)
            ev = Event.objects.create(
                title=t, title_en=ten, event_type=random.choice(et),
                summary=f"Tukio la {t} litakalofanyika {region.name}.",
                summary_en=f"{ten} taking place in {region.name}.",
                venue=f"Ukumbi wa MWST - {region.name}",
                venue_en=f"MWST Hall - {region.name}",
                region=region, start_at=start,
                end_at=start + timedelta(hours=6),
                status="planned" if future else "done", capacity=random.randint(80, 400))
            take = min(len(members), per_event, max(limit - registrations, 0))
            for m in random.sample(members, take):
                EventRegistration.objects.get_or_create(
                    event=ev, member=m,
                    defaults={"full_name": m.full_name, "phone": m.phone,
                              "attended": not future})
                registrations += 1
        self.stdout.write(f"  matukio {Event.objects.count()}")

    def media(self, limit):
        albums = [("Misaada kwa Wenye Mahitaji", "Aid for Those in Need", "sadaka"),
                  ("Elimu na Mafunzo", "Education and Training", "elimu"),
                  ("Matukio na Mikutano", "Events and Meetings", "mkutano"),
                  ("Huduma za Afya", "Health Services", "afya"),
                  ("Miradi ya Maendeleo", "Development Projects", "ujenzi"),
                  ("Mazingira na Uhamasishaji", "Environment and Awareness", "maji")]
        for nm, en, scene in albums:
            Album.objects.get_or_create(name=nm, defaults={"name_en": en, "scene": scene})
        alb = list(Album.objects.all())
        photos = [
            ("Mkutano Mkuu wa MWST 2026", "MWST AGM 2026", "mkutano", "matukio", 2.4, 36),
            ("Ujenzi wa Zahanati - Dodoma", "Dispensary Construction - Dodoma", "ujenzi", "miradi", 1.9, 28),
            ("Semina ya Uwezeshaji Kiuchumi", "Economic Empowerment Seminar", "uchumi", "mafunzo", 2.1, 42),
            ("Misaada kwa Yatima - Arusha", "Orphan Aid - Arusha", "yatima", "misaada", 1.7, 31),
            ("Usafi wa Mazingira - Mwanza", "Environmental Cleanup - Mwanza", "maji", "ziara", 1.6, 26),
        ]
        for t, ten, scene, cat, size, views in photos[:max(limit // 2, 1)]:
            MediaItem.objects.get_or_create(title=t, kind="photo", defaults={
                "title_en": ten, "scene": scene, "category": cat, "size_mb": size,
                "views": views, "album": random.choice(alb)})
        videos = [
            ("Ujenzi wa Shule Mpya - Pwani.mp4", "New School Construction - Pwani.mp4", "ujenzi", "miradi", 24.6, "04:32"),
            ("Mkutano Mkuu wa MWST 2026.mp4", "MWST AGM 2026.mp4", "mkutano", "matukio", 15.3, "03:18"),
            ("Semina ya Uongozi - Dodoma.mp4", "Leadership Seminar - Dodoma.mp4", "mkutano", "mafunzo", 22.1, "05:07"),
            ("Ziara ya Miradi - Morogoro.mp4", "Project Visit - Morogoro.mp4", "ujenzi", "ziara", 18.7, "03:45"),
            ("Misaada ya Dharura - Pwani.mp4", "Emergency Aid - Pwani.mp4", "sadaka", "misaada", 20.4, "04:11"),
        ]
        for t, ten, scene, cat, size, dur in videos[:max(limit // 4, 1)]:
            MediaItem.objects.get_or_create(title=t, kind="video", defaults={
                "title_en": ten, "scene": scene, "category": cat, "size_mb": size,
                "duration": dur, "album": random.choice(alb)})
        # jaza hadi kufikia kikomo ili takwimu ziwe na maana
        remaining = max(limit - MediaItem.objects.count(), 0)
        for i in range(remaining):
            kind = "photo" if i % 6 else "video"
            MediaItem.objects.create(
                title=f"Picha ya shughuli {i+1}" if kind == "photo" else f"Video ya shughuli {i+1}.mp4",
                title_en=f"Activity photo {i+1}" if kind == "photo" else f"Activity video {i+1}.mp4",
                kind=kind, category=random.choice(["miradi", "matukio", "mafunzo", "misaada", "ziara", "nyingine"]),
                album=random.choice(alb), scene=random.choice(["elimu", "afya", "maji", "ujenzi", "jamii", "mkutano"]),
                size_mb=Decimal(str(round(random.uniform(0.8, 26), 1))),
                duration=f"0{random.randint(2,5)}:{random.randint(10,59)}" if kind == "video" else "",
                views=random.randint(5, 200), downloads=random.randint(0, 60),
                uploaded_on=timezone.localdate() - timedelta(days=random.randint(0, 300)))
        self.stdout.write(f"  picha na video {MediaItem.objects.count()}")

    def news(self, limit):
        for nm, en, slug in [("Misaada", "Aid", "misaada"), ("Elimu", "Education", "elimu"),
                             ("Miradi", "Projects", "miradi"),
                             ("Matangazo", "Announcements", "matangazo")]:
            NewsCategory.objects.get_or_create(slug=slug, defaults={"name": nm, "name_en": en})
        cats = {c.slug: c for c in NewsCategory.objects.all()}
        today = timezone.localdate()
        items = [
            ("MWST yatoa msaada kwa familia zilizoathiriwa na mafuriko Dodoma",
             "MWST delivers aid to flood-affected families in Dodoma",
             "MWST imekabidhi msaada wa vyakula, mavazi na vifaa muhimu kwa familia 120 "
             "zilizoathirika na mafuriko katika wilaya za Chamwino na Bahi. Msaada huu una "
             "thamani ya zaidi ya TZS 85 milioni.",
             "MWST has delivered food, clothing and essential supplies to 120 families "
             "affected by flooding in Chamwino and Bahi districts, worth over TZS 85 million.",
             "misaada", "sadaka", 2, True),
            ("Programu ya Scholarship 2026/2027", "Scholarship Programme 2026/2027",
             "Maombi ya scholarship kwa wanafunzi wa Kidato na Vyuo yanakaribishwa hadi 31 Agosti 2026.",
             "Scholarship applications for secondary and college students are open until 31 August 2026.",
             "elimu", "elimu", 4, False),
            ("Semina ya Uongozi na Maadili ya Kiislamu", "Islamic Leadership and Ethics Seminar",
             "Semina hii inalenga kuwajengea uwezo viongozi waamini katika uongozi bora na maadili.",
             "This seminar builds the capacity of leaders in good governance and ethics.",
             "matangazo", "mkutano", 12, False),
            ("Ujenzi wa Zahanati Dodoma waingia hatua ya mwisho",
             "Dodoma dispensary construction enters final phase",
             "Ujenzi wa zahanati ya Nkuhungu umefikia asilimia 85 na unatarajiwa kukamilika Oktoba.",
             "The Nkuhungu dispensary is 85% complete and is expected to finish in October.",
             "miradi", "ujenzi", 14, False),
            ("Ugawaji wa vifaa vya elimu kwa shule 15", "Learning materials distributed to 15 schools",
             "Vitabu, madawati na vifaa vya maabara vimekabidhiwa kwa shule 15 mkoani Mwanza.",
             "Books, desks and laboratory equipment were handed over to 15 schools in Mwanza region.",
             "elimu", "elimu", 17, False),
            ("Kambi ya upimaji afya bure Nkuhungu", "Free health screening camp at Nkuhungu",
             "Zaidi ya watu 800 walipimwa shinikizo la damu, kisukari na macho bila malipo.",
             "Over 800 people were screened for blood pressure, diabetes and eyesight free of charge.",
             "misaada", "afya", 22, False),
            ("Mkutano wa wadau kuhusu miradi ya maji", "Stakeholder meeting on water projects",
             "Wadau kutoka mashirika manne walikutana kujadili upanuzi wa miradi ya visima.",
             "Partners from four organisations met to discuss expanding borehole projects.",
             "miradi", "maji", 27, False),
        ]
        for t, ten, s, sen, cat, scene, days, feat in items[:limit]:
            News.objects.get_or_create(title=t, defaults={
                "title_en": ten, "summary": s, "summary_en": sen,
                "category": cats.get(cat), "scene": scene, "is_featured": feat,
                "published_on": today - timedelta(days=days)})

        anns = [
            ("Mkutano Mkuu wa MWST", "MWST Annual General Meeting",
             "Wote mnakaribishwa kwenye Mkutano Mkuu utakaofanyika Dodoma tarehe 30 Agosti 2026.",
             "All are welcome to the Annual General Meeting in Dodoma on 30 August 2026.",
             "megaphone", "green", 2),
            ("Fursa za Scholarship 2026", "Scholarship Opportunities 2026",
             "Maombi ya scholarship kwa wanafunzi wa kidato na vyuo yanapokelewa hadi 15 Agosti.",
             "Scholarship applications for secondary and college students close on 15 August.",
             "book", "navy", 4),
            ("Wito wa Misaada", "Call for Aid",
             "Tuendelee kusaidia ndugu zetu wenye uhitaji katika mikoa iliyoathirika na mafuriko.",
             "Let us keep supporting those in need in the flood-affected regions.",
             "hand-heart", "gold", 7),
        ]
        for t, ten, b, ben, icon, tint, days in anns[:limit]:
            Announcement.objects.get_or_create(title=t, defaults={
                "title_en": ten, "body": b, "body_en": ben, "icon": icon, "tint": tint,
                "published_on": today - timedelta(days=days)})
        self.stdout.write(f"  habari {News.objects.count()}, matangazo {Announcement.objects.count()}")
