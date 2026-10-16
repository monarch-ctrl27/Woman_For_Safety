import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from facilities.models import Facility
from hotspots.models import Hotspot
from accounts.models import EmergencyContact, Profile, InstitutionalAccount
from emergency.models import PanicAlert, ContactNotificationLog
from moderation.models import ModerationLog


class Command(BaseCommand):
    help = (
        "Seeds the Woman For Safety operations platform with comprehensive mock data "
        "across all Bloemfontein corridors — users, hotspots, facilities, "
        "panic simulations, moderation logs, and institutional accounts. "
        "(SRS v1.2 FR-PREV-1 through FR-PREV-6)"
    )

    def handle(self, *args, **options):
        self._seed_facilities()
        self._seed_users()
        self._seed_hotspots()
        self._seed_panic_simulations()
        self._seed_moderation_logs()
        self._seed_institutional_accounts()

        self.stdout.write(self.style.SUCCESS(
            "\n✅ Successfully seeded Woman For Safety operations database with full Preview Mode data!"
        ))
        self.stdout.write(self.style.SUCCESS(
            "   Login credentials:\n"
            "   • Admin:      admin / WFSAdmin2026!\n"
            "   • Moderator:  mod_thandi / WFSMod2026!\n"
            "   • User:       sarah / WFSPassword2026!\n"
            "   • Inst. User: ufs_safety / WFSUFS2026!\n"
        ))

    # ─────────────────────────────────────────────────────────
    # 1. FACILITIES — Police, hospitals, clinics, shelters
    # ─────────────────────────────────────────────────────────
    def _seed_facilities(self):
        self.stdout.write("\n[Facilities] Seeding safe facilities for Bloemfontein region...")

        facilities_data = [
            {
                "name": "SAPS Bloemfontein Central",
                "facility_type": Facility.FACILITY_POLICE,
                "address": "Corner of Charles and Henry Streets, Bloemfontein",
                "phone_number": "+27 51 406 4400",
                "emergency_hotline": "10111",
                "latitude": -29.1172,
                "longitude": 26.2163,
                "is_24_hours": True,
                "has_victim_support_room": True,
                "services_notes": "SAPS Victim Empowerment Room, female duty officers on 24/7 patrol.",
            },
            {
                "name": "SAPS Park Road Police Station",
                "facility_type": Facility.FACILITY_POLICE,
                "address": "Park Road, Willows, Bloemfontein",
                "phone_number": "+27 51 507 6000",
                "emergency_hotline": "10111",
                "latitude": -29.1245,
                "longitude": 26.2089,
                "is_24_hours": True,
                "has_victim_support_room": True,
                "services_notes": "Direct response unit, secure refuge zone for women.",
            },
            {
                "name": "SAPS Bayswater Police Station",
                "facility_type": Facility.FACILITY_POLICE,
                "address": "Bayswater Road, Universitas, Bloemfontein",
                "phone_number": "+27 51 401 2200",
                "emergency_hotline": "10111",
                "latitude": -29.1068,
                "longitude": 26.1890,
                "is_24_hours": True,
                "has_victim_support_room": False,
                "services_notes": "Community Policing Forum active, patrols Universitas/UFS corridor.",
            },
            {
                "name": "Universitas Academic Hospital (Trauma Center)",
                "facility_type": Facility.FACILITY_HOSPITAL,
                "address": "1 Hospital Road, Universitas, Bloemfontein",
                "phone_number": "+27 51 405 3911",
                "emergency_hotline": "10177",
                "latitude": -29.1118,
                "longitude": 26.1834,
                "is_24_hours": True,
                "has_victim_support_room": True,
                "services_notes": "Level 1 Emergency Trauma Unit, emergency medical response & forensic care.",
            },
            {
                "name": "Pelonomi Tertiary Hospital & Thuthuzela Care Centre",
                "facility_type": Facility.FACILITY_HOSPITAL,
                "address": "Dr Belcher Road, Heidedal, Bloemfontein",
                "phone_number": "+27 51 405 1911",
                "emergency_hotline": "10177",
                "latitude": -29.1396,
                "longitude": 26.2415,
                "is_24_hours": True,
                "has_victim_support_room": True,
                "services_notes": "Thuthuzela Care Centre for GBV, crisis trauma counseling.",
            },
            {
                "name": "National District Hospital",
                "facility_type": Facility.FACILITY_CLINIC,
                "address": "Roth Avenue, Willows, Bloemfontein",
                "phone_number": "+27 51 403 9600",
                "emergency_hotline": "10177",
                "latitude": -29.1147,
                "longitude": 26.2045,
                "is_24_hours": True,
                "has_victim_support_room": True,
                "services_notes": "24h outpatient trauma stabilisation and casualty ward.",
            },
            {
                "name": "Brandwag Day Clinic",
                "facility_type": Facility.FACILITY_CLINIC,
                "address": "Second Avenue, Brandwag, Bloemfontein",
                "phone_number": "+27 51 444 6700",
                "emergency_hotline": "",
                "latitude": -29.1040,
                "longitude": 26.2090,
                "is_24_hours": False,
                "has_victim_support_room": False,
                "services_notes": "Walk-in clinic 07:00–18:00. Basic trauma dressing and referrals.",
            },
            {
                "name": "Free State Women's Safe Haven Shelter",
                "facility_type": Facility.FACILITY_SHELTER,
                "address": "Confidential Safe Location, Bloemfontein Metro",
                "phone_number": "+27 80 015 0150",
                "emergency_hotline": "0800 150 150",
                "latitude": -29.1025,
                "longitude": 26.2150,
                "is_24_hours": True,
                "has_victim_support_room": True,
                "services_notes": "Secure residential sanctuary with 24-hour guarded security, social workers, legal aid.",
            },
            {
                "name": "LifeLine Bloemfontein Crisis Centre",
                "facility_type": Facility.FACILITY_SHELTER,
                "address": "Nelson Mandela Drive, CBD, Bloemfontein",
                "phone_number": "+27 51 447 3344",
                "emergency_hotline": "0861 322 322",
                "latitude": -29.1200,
                "longitude": 26.2195,
                "is_24_hours": True,
                "has_victim_support_room": True,
                "services_notes": "24h crisis counseling, GBV support, referral to shelter network.",
            },
        ]

        for item in facilities_data:
            fac, created = Facility.objects.update_or_create(
                name=item["name"],
                defaults=item,
            )
            status = "Created" if created else "Updated"
            self.stdout.write(f"  [{status}] Facility: {fac.name}")

    # ─────────────────────────────────────────────────────────
    # 2. USERS — Admin, Moderator, Regular, Institutional
    # ─────────────────────────────────────────────────────────
    def _seed_users(self):
        self.stdout.write("\n👤 Seeding user accounts with different roles...")

        users_data = [
            {
                "username": "admin",
                "password": "WFSAdmin2026!",
                "email": "admin@safeher.co.za",
                "first_name": "Sipho",
                "last_name": "Mokoena",
                "is_staff": True,
                "is_superuser": True,
                "role": Profile.ROLE_ADMIN,
                "phone": "+27 82 100 0001",
                "safe_pin": "9999",
            },
            {
                "username": "mod_thandi",
                "password": "WFSMod2026!",
                "email": "thandi.moderation@safeher.co.za",
                "first_name": "Thandi",
                "last_name": "Nkosi",
                "is_staff": True,
                "is_superuser": False,
                "role": Profile.ROLE_MODERATOR,
                "phone": "+27 82 200 0002",
                "safe_pin": "3456",
            },
            {
                "username": "mod_lerato",
                "password": "WFSMod2026!",
                "email": "lerato.moderation@safeher.co.za",
                "first_name": "Lerato",
                "last_name": "Moloi",
                "is_staff": True,
                "is_superuser": False,
                "role": Profile.ROLE_MODERATOR,
                "phone": "+27 82 200 0003",
                "safe_pin": "5678",
            },
            {
                "username": "sarah",
                "password": "WFSPassword2026!",
                "email": "sarah.khumalo@example.co.za",
                "first_name": "Sarah",
                "last_name": "Khumalo",
                "is_staff": False,
                "is_superuser": False,
                "role": Profile.ROLE_USER,
                "phone": "+27 82 555 1234",
                "safe_pin": "2468",
            },
            {
                "username": "zanele",
                "password": "WFSUser2026!",
                "email": "zanele.dube@example.co.za",
                "first_name": "Zanele",
                "last_name": "Dube",
                "is_staff": False,
                "is_superuser": False,
                "role": Profile.ROLE_USER,
                "phone": "+27 83 666 5678",
                "safe_pin": "1357",
            },
            {
                "username": "palesa",
                "password": "WFSUser2026!",
                "email": "palesa.m@example.co.za",
                "first_name": "Palesa",
                "last_name": "Mothibi",
                "is_staff": False,
                "is_superuser": False,
                "role": Profile.ROLE_USER,
                "phone": "+27 84 777 9012",
                "safe_pin": "0246",
            },
            {
                "username": "ufs_safety",
                "password": "WFSUFS2026!",
                "email": "safety@ufs.ac.za",
                "first_name": "Campus",
                "last_name": "Safety Officer",
                "is_staff": False,
                "is_superuser": False,
                "role": Profile.ROLE_INSTITUTIONAL,
                "phone": "+27 51 401 9111",
                "safe_pin": "7890",
            },
        ]

        for data in users_data:
            user, u_created = User.objects.update_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "is_staff": data["is_staff"],
                    "is_superuser": data["is_superuser"],
                },
            )
            user.set_password(data["password"])
            user.save()

            # Update or create profile
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = data["role"]
            profile.phone_number = data["phone"]
            profile.safe_pin = data["safe_pin"]
            profile.voice_trigger_enabled = True
            profile.triple_press_enabled = True
            profile.fall_detection_enabled = True
            profile.geofence_vibration_enabled = True
            profile.save()

            status = "Created" if u_created else "Updated"
            self.stdout.write(f"  [{status}] User: {user.username} [{data['role']}]")

        # Seed Emergency Contacts for Sarah
        self.stdout.write("\n📞 Seeding emergency contacts...")
        sarah = User.objects.get(username="sarah")
        sarah.profile.medical_notes = "Asthmatic, carries inhaler. Blood Type O Positive."
        sarah.profile.save()

        contacts_data = [
            {
                "phone_number": "+27829998877",
                "defaults": {
                    "name": "Nomsa Khumalo",
                    "relationship": "Mother (Next of Kin)",
                    "priority": 1,
                    "notify_on_panic": True,
                    "notify_on_standdown_expire": True,
                },
            },
            {
                "phone_number": "+27831112233",
                "defaults": {
                    "name": "Lindiwe Dlamini",
                    "relationship": "Sister",
                    "priority": 2,
                    "notify_on_panic": True,
                    "notify_on_standdown_expire": True,
                },
            },
            {
                "phone_number": "+27844445566",
                "defaults": {
                    "name": "Dr Mpho Ratsiu",
                    "relationship": "Friend & UFS Res Adviser",
                    "priority": 3,
                    "notify_on_panic": True,
                    "notify_on_standdown_expire": False,
                },
            },
        ]
        for c_data in contacts_data:
            ec, created = EmergencyContact.objects.update_or_create(
                user=sarah,
                phone_number=c_data["phone_number"],
                defaults=c_data["defaults"],
            )
            status = "Created" if created else "Updated"
            self.stdout.write(f"  [{status}] Contact: {ec.name} for sarah")

        # Contacts for zanele
        zanele = User.objects.get(username="zanele")
        EmergencyContact.objects.update_or_create(
            user=zanele,
            phone_number="+27851234567",
            defaults={
                "name": "Busi Dube",
                "relationship": "Mother",
                "priority": 1,
                "notify_on_panic": True,
                "notify_on_standdown_expire": True,
            },
        )

    # ─────────────────────────────────────────────────────────
    # 3. HOTSPOTS — 20+ across all Bloemfontein corridors
    # ─────────────────────────────────────────────────────────
    def _seed_hotspots(self):
        self.stdout.write("\n📍 Seeding crowd-sourced danger hotspots across all corridors...")

        sarah = User.objects.get(username="sarah")
        zanele = User.objects.get(username="zanele")
        palesa = User.objects.get(username="palesa")

        hotspots_data = [
            # ── WESTDENE CORRIDOR (4) ──
            {
                "title": "Westdene Taxi Corner & Alley",
                "category": "HARASSMENT",
                "corridor": "WESTDENE",
                "description": "Persistent aggressive catcalling, physical crowding, and intimidation of solo women walking towards campus.",
                "latitude": -29.1120,
                "longitude": 26.2080,
                "danger_radius_meters": 200,
                "severity": Hotspot.SEVERITY_MEDIUM,
                "risk_time": "RUSH",
                "confirmations_count": 19,
                "reported_by": sarah,
                "verification_status": Hotspot.STATUS_PUBLISHED,
            },
            {
                "title": "Dark Passage behind Westdene Shops",
                "category": "LIGHTING",
                "corridor": "WESTDENE",
                "description": "No working streetlights in the passage connecting President Reitz Ave to the student digs. Two mugging reports last month.",
                "latitude": -29.1105,
                "longitude": 26.2065,
                "danger_radius_meters": 180,
                "severity": Hotspot.SEVERITY_HIGH,
                "risk_time": "NIGHT",
                "confirmations_count": 11,
                "reported_by": zanele,
                "verification_status": Hotspot.STATUS_PUBLISHED,
            },
            {
                "title": "Westdene Vacant Lot (Proposed Parking)",
                "category": "ISOLATED",
                "corridor": "WESTDENE",
                "description": "Overgrown empty lot used as shortcut. Reports of men hiding in vehicles parked at the far end.",
                "latitude": -29.1098,
                "longitude": 26.2100,
                "danger_radius_meters": 150,
                "severity": Hotspot.SEVERITY_MEDIUM,
                "risk_time": "ALL",
                "confirmations_count": 6,
                "reported_by": palesa,
                "verification_status": Hotspot.STATUS_FLAGGED,
                "flag_reason": "Community user disputes accuracy — claims lot has been cleared and fenced off as of August 2026.",
            },
            {
                "title": "Jan Pierewiet St Student House Row",
                "category": "HARASSMENT",
                "corridor": "WESTDENE",
                "description": "Groups of men loitering on pavements harassing women walking to morning lectures between 6:30–8:00 AM.",
                "latitude": -29.1115,
                "longitude": 26.2050,
                "danger_radius_meters": 160,
                "severity": Hotspot.SEVERITY_LOW,
                "risk_time": "RUSH",
                "confirmations_count": 8,
                "reported_by": sarah,
                "verification_status": Hotspot.STATUS_PUBLISHED,
            },

            # ── WILLOWS / CUT STUDENT BELT (4) ──
            {
                "title": "Park Road Underpass near Willows",
                "category": "MUGGING",
                "corridor": "WILLOWS",
                "description": "Blind corner under bridge. Three knife-point phone robberies reported in the past fortnight between 19:00 and 22:00.",
                "latitude": -29.1280,
                "longitude": 26.2115,
                "danger_radius_meters": 300,
                "severity": Hotspot.SEVERITY_CRITICAL,
                "risk_time": "NIGHT",
                "confirmations_count": 27,
                "reported_by": zanele,
                "verification_status": Hotspot.STATUS_PUBLISHED,
            },
            {
                "title": "Willows Mall Back Parking Lot",
                "category": "MUGGING",
                "corridor": "WILLOWS",
                "description": "Dimly lit parking area behind Willows Shopping Centre. Smash-and-grab and bag-snatching reported after dark.",
                "latitude": -29.1260,
                "longitude": 26.2140,
                "danger_radius_meters": 220,
                "severity": Hotspot.SEVERITY_HIGH,
                "risk_time": "NIGHT",
                "confirmations_count": 15,
                "reported_by": palesa,
                "verification_status": Hotspot.STATUS_PUBLISHED,
            },
            {
                "title": "CUT Campus South Gate Approach",
                "category": "HARASSMENT",
                "corridor": "WILLOWS",
                "description": "Informal traders and loiterers creating a gauntlet of catcalling near the south entrance. Women report feeling unsafe walking alone.",
                "latitude": -29.1300,
                "longitude": 26.2095,
                "danger_radius_meters": 200,
                "severity": Hotspot.SEVERITY_MEDIUM,
                "risk_time": "RUSH",
                "confirmations_count": 12,
                "reported_by": sarah,
                "verification_status": Hotspot.STATUS_PUBLISHED,
            },
            {
                "title": "Willows Stormwater Drain Path",
                "category": "ISOLATED",
                "corridor": "WILLOWS",
                "description": "Secluded footpath along the stormwater drain. Used as shortcut but extremely isolated with no visibility from road.",
                "latitude": -29.1275,
                "longitude": 26.2055,
                "danger_radius_meters": 250,
                "severity": Hotspot.SEVERITY_HIGH,
                "risk_time": "ALL",
                "confirmations_count": 9,
                "reported_by": zanele,
                "verification_status": Hotspot.STATUS_FLAGGED,
                "flag_reason": "Flagged for radius review — moderator suggests reducing radius to 150m as the dangerous section is shorter than reported.",
            },

            # ── UNIVERSITAS / UFS CAMPUS FRINGE (4) ──
            {
                "title": "UFS South Campus Gate (Soetdoring Rd)",
                "category": "ASSAULT",
                "corridor": "UNIVERSITAS",
                "description": "Two reported physical assaults on female students returning from night study sessions. Poorly lit stretch between gate and residence cluster.",
                "latitude": -29.1050,
                "longitude": 26.1870,
                "danger_radius_meters": 350,
                "severity": Hotspot.SEVERITY_CRITICAL,
                "risk_time": "NIGHT",
                "confirmations_count": 22,
                "reported_by": palesa,
                "verification_status": Hotspot.STATUS_PUBLISHED,
            },
            {
                "title": "Universitas Residential Back Streets",
                "category": "LIGHTING",
                "corridor": "UNIVERSITAS",
                "description": "Multiple residential streets between Kellner St and the hospital with broken streetlights. Reported stalking incidents.",
                "latitude": -29.1085,
                "longitude": 26.1850,
                "danger_radius_meters": 280,
                "severity": Hotspot.SEVERITY_HIGH,
                "risk_time": "NIGHT",
                "confirmations_count": 16,
                "reported_by": sarah,
                "verification_status": Hotspot.STATUS_PUBLISHED,
            },
            {
                "title": "Open Field Near UFS Engineering Block",
                "category": "ISOLATED",
                "corridor": "UNIVERSITAS",
                "description": "Large open field with no perimeter control. Students report men loitering at the edges, especially during early evening.",
                "latitude": -29.1035,
                "longitude": 26.1900,
                "danger_radius_meters": 200,
                "severity": Hotspot.SEVERITY_MEDIUM,
                "risk_time": "NIGHT",
                "confirmations_count": 7,
                "reported_by": zanele,
                "verification_status": Hotspot.STATUS_DISPUTED,
                "flag_reason": "UFS Campus Protection disputes — states new flood lights installed Sept 2026 and regular campus patrol covers this area.",
            },
            {
                "title": "UFS Callie Human Centre Bus Stop",
                "category": "TRANSPORT",
                "corridor": "UNIVERSITAS",
                "description": "Unstructured minibus taxi stop with aggressive touting. Female students harassed waiting for transport after 17:00.",
                "latitude": -29.1060,
                "longitude": 26.1920,
                "danger_radius_meters": 180,
                "severity": Hotspot.SEVERITY_MEDIUM,
                "risk_time": "RUSH",
                "confirmations_count": 14,
                "reported_by": palesa,
                "verification_status": Hotspot.STATUS_PUBLISHED,
            },

            # ── BRANDWAG RETAIL CORRIDOR (4) ──
            {
                "title": "Second Avenue Alley (Behind Brandwag Centre)",
                "category": "MUGGING",
                "corridor": "BRANDWAG",
                "description": "Narrow service alley behind retail strip. At least four bag-snatching incidents reported in Aug-Sep 2026.",
                "latitude": -29.1030,
                "longitude": 26.2110,
                "danger_radius_meters": 170,
                "severity": Hotspot.SEVERITY_HIGH,
                "risk_time": "ALL",
                "confirmations_count": 18,
                "reported_by": sarah,
                "verification_status": Hotspot.STATUS_PUBLISHED,
            },
            {
                "title": "Brandwag Park Walkthrough",
                "category": "LIGHTING",
                "corridor": "BRANDWAG",
                "description": "Park path used as shortcut has no lighting after dusk. Trees create blind spots. Reports of flashers and stalkers.",
                "latitude": -29.1020,
                "longitude": 26.2130,
                "danger_radius_meters": 230,
                "severity": Hotspot.SEVERITY_HIGH,
                "risk_time": "NIGHT",
                "confirmations_count": 13,
                "reported_by": zanele,
                "verification_status": Hotspot.STATUS_PUBLISHED,
            },
            {
                "title": "Kellner Street Intersection Crossing",
                "category": "HARASSMENT",
                "corridor": "BRANDWAG",
                "description": "Busy intersection where car guards and informal workers aggressively accost women. Several verbal threat reports.",
                "latitude": -29.1045,
                "longitude": 26.2085,
                "danger_radius_meters": 140,
                "severity": Hotspot.SEVERITY_LOW,
                "risk_time": "RUSH",
                "confirmations_count": 5,
                "reported_by": palesa,
                "verification_status": Hotspot.STATUS_FLAGGED,
                "flag_reason": "Reported severity seems low for the described behaviour. Moderator should verify if this should be upgraded to MEDIUM.",
            },
            {
                "title": "Brandwag ATM Cluster (FNB/ABSA)",
                "category": "MUGGING",
                "corridor": "BRANDWAG",
                "description": "ATM area targeted by card-skimming and follow-robbery gangs. Women followed after withdrawals.",
                "latitude": -29.1055,
                "longitude": 26.2100,
                "danger_radius_meters": 150,
                "severity": Hotspot.SEVERITY_HIGH,
                "risk_time": "ALL",
                "confirmations_count": 10,
                "reported_by": sarah,
                "verification_status": Hotspot.STATUS_PUBLISHED,
            },

            # ── CBD / STATION FRINGE (4) ──
            {
                "title": "Unlit Walkway behind Central Railway Corridor",
                "category": "LIGHTING",
                "corridor": "CBD",
                "description": "Completely broken streetlights for 300 meters. Multiple reports of men loitering in shadows and aggressive stalking after 18:30.",
                "latitude": -29.1205,
                "longitude": 26.2210,
                "danger_radius_meters": 280,
                "severity": Hotspot.SEVERITY_HIGH,
                "risk_time": "NIGHT",
                "confirmations_count": 14,
                "reported_by": zanele,
                "verification_status": Hotspot.STATUS_PUBLISHED,
            },
            {
                "title": "Abandoned Building Lot off Harvey Road",
                "category": "ISOLATED",
                "corridor": "CBD",
                "description": "Derelict warehouse with no perimeter fence or security. Avoid walking alone here at all hours.",
                "latitude": -29.1265,
                "longitude": 26.2260,
                "danger_radius_meters": 250,
                "severity": Hotspot.SEVERITY_HIGH,
                "risk_time": "ALL",
                "confirmations_count": 8,
                "reported_by": palesa,
                "verification_status": Hotspot.STATUS_PUBLISHED,
            },
            {
                "title": "Bloemfontein Station Taxi Rank",
                "category": "TRANSPORT",
                "corridor": "CBD",
                "description": "Chaotic informal taxi rank. Women report groping, bag-snatching, and aggressive touting. Very dangerous solo after 17:00.",
                "latitude": -29.1220,
                "longitude": 26.2245,
                "danger_radius_meters": 300,
                "severity": Hotspot.SEVERITY_CRITICAL,
                "risk_time": "ALL",
                "confirmations_count": 31,
                "reported_by": sarah,
                "verification_status": Hotspot.STATUS_PUBLISHED,
            },
            {
                "title": "Maitland Street Underpass",
                "category": "ASSAULT",
                "corridor": "CBD",
                "description": "Subway passage under railway. One reported rape attempt in July 2026. Extremely isolated, no CCTV, no foot traffic at night.",
                "latitude": -29.1235,
                "longitude": 26.2230,
                "danger_radius_meters": 200,
                "severity": Hotspot.SEVERITY_CRITICAL,
                "risk_time": "NIGHT",
                "confirmations_count": 25,
                "reported_by": zanele,
                "verification_status": Hotspot.STATUS_PUBLISHED,
            },
        ]

        for item in hotspots_data:
            h, created = Hotspot.objects.update_or_create(
                title=item["title"],
                defaults=item,
            )
            status = "Created" if created else "Updated"
            self.stdout.write(f"  [{status}] [{item['corridor']}] {h.title}")

    # ─────────────────────────────────────────────────────────
    # 4. PANIC SIMULATIONS — Demonstrate the escalation pipeline
    # ─────────────────────────────────────────────────────────
    def _seed_panic_simulations(self):
        self.stdout.write("\n🚨 Seeding simulated panic events and NOK notification logs...")

        sarah = User.objects.get(username="sarah")
        zanele = User.objects.get(username="zanele")
        now = timezone.now()

        # Get some hotspots for association
        cbd_hotspot = Hotspot.objects.filter(corridor="CBD").first()
        willows_hotspot = Hotspot.objects.filter(corridor="WILLOWS").first()
        universitas_hotspot = Hotspot.objects.filter(corridor="UNIVERSITAS").first()

        panic_events = [
            # 1. Resolved false alarm — Sarah walked near hotspot, stood down
            {
                "user": sarah,
                "trigger_source": PanicAlert.TRIGGER_GEOFENCE,
                "status": PanicAlert.STATUS_FALSE_ALARM,
                "latitude": -29.1210,
                "longitude": 26.2215,
                "accuracy_meters": 8.5,
                "battery_level": 72,
                "hotspot_approached": cbd_hotspot,
                "started_at_offset": timedelta(days=3, hours=14),
                "escalated_at": None,
                "stood_down_at_offset": timedelta(days=3, hours=14, seconds=35),
            },
            # 2. Escalated — Zanele triggered voice, went to NOK
            {
                "user": zanele,
                "trigger_source": PanicAlert.TRIGGER_VOICE,
                "status": PanicAlert.STATUS_ACTIVE,
                "latitude": -29.1285,
                "longitude": 26.2110,
                "accuracy_meters": 12.0,
                "battery_level": 45,
                "hotspot_approached": willows_hotspot,
                "started_at_offset": timedelta(days=2, hours=21),
                "escalated_at_offset": timedelta(days=2, hours=21, minutes=1),
                "stood_down_at": None,
            },
            # 3. Resolved safe — Sarah manual SOS, later resolved
            {
                "user": sarah,
                "trigger_source": PanicAlert.TRIGGER_MANUAL,
                "status": PanicAlert.STATUS_RESOLVED,
                "latitude": -29.1055,
                "longitude": 26.1875,
                "accuracy_meters": 6.0,
                "battery_level": 88,
                "hotspot_approached": universitas_hotspot,
                "started_at_offset": timedelta(days=5, hours=19, minutes=30),
                "escalated_at_offset": timedelta(days=5, hours=19, minutes=31),
                "resolved_at_offset": timedelta(days=5, hours=19, minutes=45),
            },
            # 4. Fall detection simulation — Sarah
            {
                "user": sarah,
                "trigger_source": PanicAlert.TRIGGER_FALL,
                "status": PanicAlert.STATUS_FALSE_ALARM,
                "latitude": -29.1120,
                "longitude": 26.2080,
                "accuracy_meters": 15.0,
                "battery_level": 55,
                "hotspot_approached": None,
                "started_at_offset": timedelta(days=1, hours=8),
                "stood_down_at_offset": timedelta(days=1, hours=8, seconds=42),
            },
            # 5. Triple-press simulation — Zanele
            {
                "user": zanele,
                "trigger_source": PanicAlert.TRIGGER_TRIPLE_PRESS,
                "status": PanicAlert.STATUS_RESOLVED,
                "latitude": -29.1030,
                "longitude": 26.2110,
                "accuracy_meters": 10.0,
                "battery_level": 30,
                "hotspot_approached": None,
                "started_at_offset": timedelta(days=7, hours=22, minutes=15),
                "escalated_at_offset": timedelta(days=7, hours=22, minutes=16),
                "resolved_at_offset": timedelta(days=7, hours=22, minutes=40),
            },
            # 6. Geofence approach — still pending (recent)
            {
                "user": sarah,
                "trigger_source": PanicAlert.TRIGGER_GEOFENCE,
                "status": PanicAlert.STATUS_STAND_DOWN_PENDING,
                "latitude": -29.1225,
                "longitude": 26.2240,
                "accuracy_meters": 9.0,
                "battery_level": 62,
                "hotspot_approached": cbd_hotspot,
                "started_at_offset": timedelta(minutes=2),
            },
        ]

        for i, p_data in enumerate(panic_events):
            started_at = now - p_data.get("started_at_offset", timedelta())
            alert = PanicAlert(
                user=p_data["user"],
                trigger_source=p_data["trigger_source"],
                status=p_data["status"],
                latitude=p_data["latitude"],
                longitude=p_data["longitude"],
                accuracy_meters=p_data["accuracy_meters"],
                battery_level=p_data["battery_level"],
                hotspot_approached=p_data.get("hotspot_approached"),
            )
            alert.save()
            # Override auto_now_add timestamps
            PanicAlert.objects.filter(pk=alert.pk).update(started_at=started_at)

            if p_data.get("escalated_at_offset"):
                escalated = now - p_data["escalated_at_offset"]
                PanicAlert.objects.filter(pk=alert.pk).update(escalated_at=escalated)

            if p_data.get("stood_down_at_offset"):
                stood_down = now - p_data["stood_down_at_offset"]
                PanicAlert.objects.filter(pk=alert.pk).update(stood_down_at=stood_down)

            if p_data.get("resolved_at_offset"):
                resolved = now - p_data["resolved_at_offset"]
                PanicAlert.objects.filter(pk=alert.pk).update(resolved_at=resolved)

            self.stdout.write(
                f"  [Created] Panic #{alert.id}: {p_data['trigger_source']} → {p_data['status']} "
                f"({p_data['user'].username})"
            )

            # Create notification logs for escalated events
            if p_data["status"] in [PanicAlert.STATUS_ACTIVE, PanicAlert.STATUS_RESOLVED]:
                contacts = EmergencyContact.objects.filter(user=p_data["user"])
                for contact in contacts:
                    ContactNotificationLog.objects.create(
                        panic_alert=alert,
                        recipient_name=contact.name,
                        recipient_phone=contact.phone_number,
                        channel=ContactNotificationLog.CHANNEL_CALL if contact.priority == 1 else ContactNotificationLog.CHANNEL_SMS,
                        status=ContactNotificationLog.STATUS_SIMULATED,
                        message_body=(
                            f"[SIMULATED] WFS NOK Alert: {p_data['user'].first_name} "
                            f"{p_data['user'].last_name} triggered a {alert.get_trigger_source_display()} alert. "
                            f"Location: {p_data['latitude']}, {p_data['longitude']}. "
                            f"Google Maps: https://maps.google.com/?q={p_data['latitude']},{p_data['longitude']}"
                        ),
                    )
                    self.stdout.write(f"    → NOK notification: {contact.name} ({contact.phone_number})")

    # ─────────────────────────────────────────────────────────
    # 5. MODERATION LOGS — Show moderator review actions
    # ─────────────────────────────────────────────────────────
    def _seed_moderation_logs(self):
        self.stdout.write("\n📋 Seeding moderation audit logs...")

        mod_thandi = User.objects.get(username="mod_thandi")
        mod_lerato = User.objects.get(username="mod_lerato")

        # Get specific hotspots for moderation actions
        published_hotspots = Hotspot.objects.filter(verification_status=Hotspot.STATUS_PUBLISHED)[:5]
        flagged_hotspots = Hotspot.objects.filter(verification_status=Hotspot.STATUS_FLAGGED)

        logs_data = []

        # Published hotspots reviewed and kept
        for i, h in enumerate(published_hotspots):
            moderator = mod_thandi if i % 2 == 0 else mod_lerato
            logs_data.append({
                "moderator": moderator,
                "hotspot": h,
                "action": ModerationLog.ACTION_KEPT,
                "reason": f"Verified via community confirmations ({h.confirmations_count} confirms). "
                          f"Cross-referenced with SAPS sector reports. Pin data matches reported incidents.",
            })

        # One radius adjustment
        if published_hotspots.count() > 0:
            logs_data.append({
                "moderator": mod_thandi,
                "hotspot": published_hotspots[0],
                "action": ModerationLog.ACTION_RADIUS_ADJUSTED,
                "reason": "Adjusted danger radius from 280m to 350m based on follow-up reports extending the hazard zone further along the corridor.",
            })

        # Flagged hotspots have review actions
        for h in flagged_hotspots:
            logs_data.append({
                "moderator": mod_lerato,
                "hotspot": h,
                "action": ModerationLog.ACTION_FLAGGED,
                "reason": f"Community dispute received. Flag reason: '{h.flag_reason[:80]}...' "
                          f"Requires site visit verification before resolution.",
            })

        # One removed hotspot example — create an extra hotspot and remove it
        removed_hotspot, _ = Hotspot.objects.update_or_create(
            title="False Report: Nelson Mandela Drive (Retracted)",
            defaults={
                "category": "MUGGING",
                "corridor": "CBD",
                "description": "Originally reported as mugging site but investigation found no corroborating reports. Reporter retracted claim.",
                "latitude": -29.1195,
                "longitude": 26.2200,
                "danger_radius_meters": 200,
                "severity": Hotspot.SEVERITY_MEDIUM,
                "risk_time": "NIGHT",
                "confirmations_count": 1,
                "verification_status": Hotspot.STATUS_REMOVED,
                "active": False,
                "reported_by": User.objects.get(username="sarah"),
                "flag_reason": "Reporter retracted. No corroborating evidence from community or SAPS.",
            },
        )
        logs_data.append({
            "moderator": mod_thandi,
            "hotspot": removed_hotspot,
            "action": ModerationLog.ACTION_REMOVED,
            "reason": "Reporter retracted claim. Cross-check with SAPS sector report and community patrol found no evidence. "
                      "Removed from live map to maintain community trust in data quality.",
        })

        for log_data in logs_data:
            log, created = ModerationLog.objects.get_or_create(
                moderator=log_data["moderator"],
                hotspot=log_data["hotspot"],
                action=log_data["action"],
                defaults={"reason": log_data["reason"]},
            )
            status = "Created" if created else "Exists"
            self.stdout.write(
                f"  [{status}] {log.action} on '{log.hotspot.title[:50]}' by {log.moderator.username}"
            )

    # ─────────────────────────────────────────────────────────
    # 6. INSTITUTIONAL ACCOUNTS — University, BID, NGO
    # ─────────────────────────────────────────────────────────
    def _seed_institutional_accounts(self):
        self.stdout.write("\n🏛️ Seeding institutional partner accounts...")

        accounts_data = [
            {
                "name": "UFS Campus Protection Services",
                "institution_type": "university",
                "contact_person": "Prof. Johan van Rooyen",
                "contact_email": "safety@ufs.ac.za",
                "contact_phone": "+27 51 401 9111",
                "plan": "institutional_campus",
                "status": "active",
                "covered_corridor": "Universitas / UFS Campus Fringe",
                "active_students_protected": 8500,
                "monthly_subscription_zar": 8500.00,
            },
            {
                "name": "CUT Student Affairs & Safety",
                "institution_type": "university",
                "contact_person": "Ms. Palesa Morake",
                "contact_email": "safety@cut.ac.za",
                "contact_phone": "+27 51 507 3911",
                "plan": "institutional_campus",
                "status": "active",
                "covered_corridor": "Willows / CUT Student Belt",
                "active_students_protected": 4200,
                "monthly_subscription_zar": 8500.00,
            },
            {
                "name": "Westdene Residence Committee",
                "institution_type": "residence",
                "contact_person": "Themba Tshabalala",
                "contact_email": "safety@westdene-res.co.za",
                "contact_phone": "+27 82 900 1234",
                "plan": "institutional_standard",
                "status": "active",
                "covered_corridor": "Westdene Corridor",
                "active_students_protected": 450,
                "monthly_subscription_zar": 2500.00,
            },
            {
                "name": "Brandwag Business Improvement District",
                "institution_type": "retailer_bid",
                "contact_person": "André Pretorius",
                "contact_email": "andre@brandwag-bid.co.za",
                "contact_phone": "+27 51 444 7000",
                "plan": "active_zone_sponsor",
                "status": "active",
                "covered_corridor": "Brandwag Retail Corridor",
                "active_students_protected": 0,
                "monthly_subscription_zar": 1200.00,
            },
            {
                "name": "Free State GBV Action Network",
                "institution_type": "ngo",
                "contact_person": "Advocate Dikeledi Mothibe",
                "contact_email": "info@fs-gbv-action.org.za",
                "contact_phone": "+27 80 015 0150",
                "plan": "free_pilot",
                "status": "trial",
                "covered_corridor": "All Bloemfontein Metro Corridors",
                "active_students_protected": 0,
                "monthly_subscription_zar": 0.00,
            },
        ]

        for data in accounts_data:
            acct, created = InstitutionalAccount.objects.update_or_create(
                name=data["name"],
                defaults=data,
            )
            status = "Created" if created else "Updated"
            self.stdout.write(f"  [{status}] {acct.name} ({acct.get_status_display()})")
