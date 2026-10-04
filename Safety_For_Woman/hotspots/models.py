import math
from django.db import models
from django.contrib.auth.models import User


def haversine_distance_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class Hotspot(models.Model):
    """
    Crowd-sourced danger zone pinned by women based on personal knowledge,
    past incidents, lighting conditions, harassment, or robbery.
    """
    SEVERITY_LOW = "LOW"
    SEVERITY_MEDIUM = "MEDIUM"
    SEVERITY_HIGH = "HIGH"
    SEVERITY_CRITICAL = "CRITICAL"

    SEVERITY_CHOICES = [
        (SEVERITY_LOW, "Caution (Poor lighting, deserted)"),
        (SEVERITY_MEDIUM, "Moderate Risk (Frequent catcalling / verbal harassment)"),
        (SEVERITY_HIGH, "High Danger (Mugging, robbery, groping reported)"),
        (SEVERITY_CRITICAL, "Critical Hotspot (Severe violent assault / weapon sighted)"),
    ]

    CATEGORY_CHOICES = [
        ("LIGHTING", "Dark / Broken Streetlights"),
        ("HARASSMENT", "Catcalling & Stalking Area"),
        ("MUGGING", "Robbery / Mugging Hotspot"),
        ("ASSAULT", "Physical Assault / GBV Incident"),
        ("ISOLATED", "Isolated Alley / Abandoned Building"),
        ("TRANSPORT", "Unsafe Taxi Rank / Station Corner"),
    ]

    RISK_TIME_CHOICES = [
        ("ALL", "Dangerous Anytime"),
        ("NIGHT", "Dangerous After Dark (Night)"),
        ("RUSH", "Dangerous During Commute / Rush Hour"),
    ]

    CORRIDOR_CHOICES = [
        ("WESTDENE", "Westdene Corridor"),
        ("WILLOWS", "Willows / CUT Student Belt"),
        ("UNIVERSITAS", "Universitas / UFS Campus Fringe"),
        ("BRANDWAG", "Brandwag Retail Corridor"),
        ("CBD", "Bloemfontein CBD / Station Fringe"),
        ("OTHER", "Other Metro Corridor"),
    ]

    STATUS_PUBLISHED = "published"
    STATUS_FLAGGED = "flagged"
    STATUS_DISPUTED = "disputed"
    STATUS_REMOVED = "removed"

    STATUS_CHOICES = [
        (STATUS_PUBLISHED, "Published on Live Map"),
        (STATUS_FLAGGED, "Flagged for Moderator Review"),
        (STATUS_DISPUTED, "Disputed by Community"),
        (STATUS_REMOVED, "Removed by Moderator"),
    ]

    title = models.CharField(max_length=150, help_text="e.g. Unlit alley behind taxi rank")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="MUGGING")
    corridor = models.CharField(max_length=30, choices=CORRIDOR_CHOICES, default="WESTDENE", db_index=True)
    description = models.TextField(help_text="Provide context to help other women avoid this spot safely.")
    latitude = models.FloatField()
    longitude = models.FloatField()
    danger_radius_meters = models.PositiveIntegerField(
        default=250,
        help_text="Radius in meters where rerouting occurs and warnings activate."
    )
    severity = models.CharField(max_length=15, choices=SEVERITY_CHOICES, default=SEVERITY_HIGH)
    risk_time = models.CharField(max_length=10, choices=RISK_TIME_CHOICES, default="NIGHT")
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PUBLISHED,
        db_index=True,
        help_text="Current state in the post-publication moderation workflow (SRS §3.7)."
    )
    flag_reason = models.TextField(blank=True, help_text="Reason provided when flagged by community or user.")
    confirmations_count = models.PositiveIntegerField(default=1)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} [{self.get_corridor_display()}] - {self.verification_status}"

    def distance_from(self, user_lat, user_lon):
        try:
            return haversine_distance_km(user_lat, user_lon, self.latitude, self.longitude)
        except Exception:
            return 9999.0

    def is_within_geofence(self, user_lat, user_lon, geofence_radius_km=0.6):
        dist = self.distance_from(user_lat, user_lon)
        return dist <= geofence_radius_km


class HotspotConfirmation(models.Model):
    hotspot = models.ForeignKey(Hotspot, on_delete=models.CASCADE, related_name="confirmations")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("hotspot", "user")

    def __str__(self):
        return f"{self.user.username} confirmed {self.hotspot.title}"
