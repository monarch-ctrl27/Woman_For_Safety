from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from hotspots.models import Hotspot


class PanicAlert(models.Model):
    """
    Emergency incident trigger fired by:
    - In-app manual one-tap panic button
    - Hands-free voice trigger ("Help!") [Experimental]
    - Fall-detection accelerometer sensor [Experimental]
    - Geofence 60-second stand-down expiration
    - Power button triple-press simulation

    Per SRS v1.2 (§2.8 & FR-PANIC-1):
    Escalates SOLELY through user's own next-of-kin list.
    No build may claim or imply automated police dispatch.
    """
    TRIGGER_TRIPLE_PRESS = "TRIPLE_PRESS"
    TRIGGER_VOICE = "VOICE"
    TRIGGER_FALL = "FALL_DETECTION"
    TRIGGER_GEOFENCE = "GEOFENCE_APPROACH"
    TRIGGER_MANUAL = "MANUAL_SOS"

    TRIGGER_CHOICES = [
        (TRIGGER_MANUAL, "Manual SOS Button"),
        (TRIGGER_VOICE, "Hands-Free Voice ('Help!') [Experimental]"),
        (TRIGGER_FALL, "Automatic Fall Detection [Experimental]"),
        (TRIGGER_TRIPLE_PRESS, "Triple Power/Key Press Simulation"),
        (TRIGGER_GEOFENCE, "Geofence Stand-Down Expired"),
    ]

    STATUS_STAND_DOWN_PENDING = "STAND_DOWN_PENDING"
    STATUS_ACTIVE = "ACTIVE"
    STATUS_FALSE_ALARM = "FALSE_ALARM"
    STATUS_RESOLVED = "RESOLVED"

    STATUS_CHOICES = [
        (STATUS_STAND_DOWN_PENDING, "Stand-Down Window Active (60s)"),
        (STATUS_ACTIVE, "Escalated to Next of Kin"),
        (STATUS_FALSE_ALARM, "Resolved via False Alarm Cancel"),
        (STATUS_RESOLVED, "Resolved Safe"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="panic_alerts")
    trigger_source = models.CharField(max_length=25, choices=TRIGGER_CHOICES, default=TRIGGER_MANUAL)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default=STATUS_STAND_DOWN_PENDING)
    latitude = models.FloatField()
    longitude = models.FloatField()
    accuracy_meters = models.FloatField(default=10.0)
    battery_level = models.IntegerField(null=True, blank=True)
    standdown_seconds_total = models.IntegerField(default=60)
    hotspot_approached = models.ForeignKey(Hotspot, on_delete=models.SET_NULL, null=True, blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    escalated_at = models.DateTimeField(null=True, blank=True)
    stood_down_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"Incident #{self.id} ({self.get_trigger_source_display()}) - {self.status}"

    @property
    def seconds_remaining(self):
        if self.status != self.STATUS_STAND_DOWN_PENDING:
            return 0
        elapsed = (timezone.now() - self.started_at).total_seconds()
        remaining = self.standdown_seconds_total - elapsed
        return max(0, int(remaining))

    @property
    def is_stand_down_expired(self):
        return self.seconds_remaining <= 0 and self.status == self.STATUS_STAND_DOWN_PENDING

    @property
    def google_maps_url(self):
        return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"


class ContactNotificationLog(models.Model):
    """
    Audit log of Next-of-Kin notifications dispatched.
    Per SRS §3.5 (FR-PANIC-1 & FR-PANIC-6):
    Calls first; falls back to WhatsApp message with live GPS.
    """
    CHANNEL_CALL = "VOICE_CALL"
    CHANNEL_SMS = "SMS"
    CHANNEL_WHATSAPP = "WHATSAPP"

    CHANNEL_CHOICES = [
        (CHANNEL_CALL, "Priority Voice Call"),
        (CHANNEL_SMS, "SMS Coordinates Alert"),
        (CHANNEL_WHATSAPP, "WhatsApp Message Fallback"),
    ]

    STATUS_SIMULATED = "SIMULATED_DEMO"
    STATUS_DELIVERED = "DELIVERED"
    STATUS_FAILED = "FAILED"

    STATUS_CHOICES = [
        (STATUS_SIMULATED, "Simulated (Preview / Demo Mode)"),
        (STATUS_DELIVERED, "Delivered to Next of Kin"),
        (STATUS_FAILED, "Delivery Failed"),
    ]

    panic_alert = models.ForeignKey(PanicAlert, on_delete=models.CASCADE, related_name="notifications")
    recipient_name = models.CharField(max_length=100)
    recipient_phone = models.CharField(max_length=30)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default=CHANNEL_SMS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SIMULATED)
    message_body = models.TextField()
    external_sid = models.CharField(max_length=100, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sent_at"]

    def __str__(self):
        return f"{self.channel} to {self.recipient_name} ({self.status})"
