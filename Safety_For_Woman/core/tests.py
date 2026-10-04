from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile, EmergencyContact
from facilities.models import Facility
from hotspots.models import Hotspot
from emergency.models import PanicAlert, ContactNotificationLog
from emergency.services import dispatch_emergency


class SafeHerSystemTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create test user
        self.user = User.objects.create_user(
            username="lindam",
            password="StrongPassword2026!",
            first_name="Linda",
            last_name="Molefe",
            email="linda@example.com"
        )
        self.user.profile.safe_pin = "9876"
        self.user.profile.save()

        # Create emergency contact
        self.contact = EmergencyContact.objects.create(
            user=self.user,
            name="Grace Molefe",
            relationship="Mother",
            phone_number="+27821110000",
            priority=1,
            notify_on_panic=True,
            notify_on_standdown_expire=True,
        )

        # Create safe facility
        self.police = Facility.objects.create(
            name="SAPS Bloemfontein Central",
            facility_type=Facility.FACILITY_POLICE,
            address="Charles & Henry St",
            phone_number="+27514064400",
            latitude=-29.1172,
            longitude=26.2163,
            is_24_hours=True,
        )

        # Create danger hotspot
        self.hotspot = Hotspot.objects.create(
            title="Unlit Train Footbridge",
            category="LIGHTING",
            description="Dark passage, past robbery reports.",
            latitude=-29.1200,
            longitude=26.2200,
            danger_radius_meters=300,
            severity=Hotspot.SEVERITY_HIGH,
            reported_by=self.user,
        )

    def test_user_profile_and_pin(self):
        self.assertEqual(self.user.profile.safe_pin, "9876")
        self.assertTrue(self.user.profile.voice_trigger_enabled)
        self.assertTrue(self.user.profile.triple_press_enabled)
        self.assertTrue(self.user.profile.fall_detection_enabled)

    def test_hotspot_geofence_proximity(self):
        # Point within 200m of hotspot (well within 600m geofence)
        close_lat = -29.1205
        close_lon = 26.2205
        self.assertTrue(self.hotspot.is_within_geofence(close_lat, close_lon, geofence_radius_km=0.6))

        # Far away point (> 5km)
        far_lat = -29.2000
        far_lon = 26.3000
        self.assertFalse(self.hotspot.is_within_geofence(far_lat, far_lon, geofence_radius_km=0.6))

    def test_api_check_geofence_endpoint(self):
        response = self.client.get(reverse("hotspots:api_check_geofence"), {
            "lat": -29.1202,
            "lon": 26.2202,
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "warning")
        self.assertTrue(data["approaching_danger"])
        self.assertEqual(data["hotspot"]["id"], self.hotspot.id)

    def test_api_safe_route_bypasses_hotspot(self):
        # Straight route passing directly through the hotspot
        response = self.client.get(reverse("hotspots:api_safe_route"), {
            "start_lat": -29.1150,
            "start_lon": 26.2200,
            "dest_lat": -29.1250,
            "dest_lon": 26.2200,
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        # Ensure rerouting detour was computed
        self.assertGreater(data["detours_count"], 0)
        self.assertGreater(len(data["route_waypoints"]), 2)

    def test_panic_trigger_and_stand_down_countdown(self):
        self.client.login(username="lindam", password="StrongPassword2026!")

        # Trigger SOS
        response = self.client.post(
            reverse("emergency:trigger"),
            data={"trigger_source": "VOICE", "latitude": -29.1200, "longitude": 26.2200},
        )
        self.assertEqual(response.status_code, 302)

        alert = PanicAlert.objects.filter(user=self.user).first()
        self.assertIsNotNone(alert)
        self.assertEqual(alert.status, PanicAlert.STATUS_STAND_DOWN_PENDING)
        self.assertEqual(alert.trigger_source, "VOICE")
        self.assertEqual(alert.standdown_seconds_total, 60)

    def test_stand_down_safe_pin_cancellation(self):
        self.client.login(username="lindam", password="StrongPassword2026!")
        alert = PanicAlert.objects.create(
            user=self.user,
            trigger_source=PanicAlert.TRIGGER_FALL,
            status=PanicAlert.STATUS_STAND_DOWN_PENDING,
            latitude=-29.1200,
            longitude=26.2200,
        )

        # Submit wrong PIN
        res_wrong = self.client.post(reverse("emergency:cancel", args=[alert.id]), {"pin": "0000"})
        alert.refresh_from_db()
        self.assertEqual(alert.status, PanicAlert.STATUS_STAND_DOWN_PENDING)

        # Submit correct PIN (9876)
        res_correct = self.client.post(reverse("emergency:cancel", args=[alert.id]), {"pin": "9876"})
        alert.refresh_from_db()
        self.assertEqual(alert.status, PanicAlert.STATUS_FALSE_ALARM)
        self.assertIsNotNone(alert.stood_down_at)

    def test_emergency_dispatch_notifications(self):
        alert = PanicAlert.objects.create(
            user=self.user,
            trigger_source=PanicAlert.TRIGGER_TRIPLE_PRESS,
            status=PanicAlert.STATUS_STAND_DOWN_PENDING,
            latitude=-29.1200,
            longitude=26.2200,
        )

        # Dispatch alert
        dispatch_emergency(alert)
        alert.refresh_from_db()

        self.assertEqual(alert.status, PanicAlert.STATUS_ACTIVE)
        self.assertIsNotNone(alert.escalated_at)

        # Check notifications generated for mother ONLY (NOK only). 
        # For 1 contact, there are 2 logs: Primary channel + WhatsApp fallback.
        notifications = ContactNotificationLog.objects.filter(panic_alert=alert)
        self.assertEqual(notifications.count(), 2)

        mother_notif = notifications.filter(recipient_phone=self.contact.phone_number, channel=ContactNotificationLog.CHANNEL_CALL).first()
        self.assertIsNotNone(mother_notif)
        self.assertIn("EMERGENCY ALERT", mother_notif.message_body)
        self.assertIn(str(alert.latitude), mother_notif.message_body)
