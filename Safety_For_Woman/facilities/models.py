import math
from django.db import models


def haversine_distance_km(lat1, lon1, lat2, lon2):
    """
    Computes great-circle distance between two points in kilometers.
    """
    R = 6371.0  # Earth's radius in km
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


class Facility(models.Model):
    """
    Safe sanctuaries for women in distress: Police stations, 24h clinics,
    trauma centers, and accredited women's shelters.
    """
    FACILITY_POLICE = "POLICE"
    FACILITY_HOSPITAL = "HOSPITAL"
    FACILITY_CLINIC = "CLINIC"
    FACILITY_SHELTER = "SHELTER"

    TYPE_CHOICES = [
        (FACILITY_POLICE, "Police Station (SAPS)"),
        (FACILITY_HOSPITAL, "Hospital / Trauma Center"),
        (FACILITY_CLINIC, "24h Healthcare Clinic"),
        (FACILITY_SHELTER, "Women's Safe Haven Shelter"),
    ]

    name = models.CharField(max_length=150)
    facility_type = models.CharField(max_length=20, choices=TYPE_CHOICES, db_index=True)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=30, help_text="Direct landline or mobile")
    emergency_hotline = models.CharField(max_length=30, blank=True, help_text="e.g. 10111 or direct dispatch")
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_24_hours = models.BooleanField(default=True)
    has_victim_support_room = models.BooleanField(
        default=True,
        help_text="Equipped with private victim empowerment / trauma counseling room."
    )
    services_notes = models.TextField(blank=True, help_text="Specializations, transport assistance, security detail.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Facilities"
        ordering = ["facility_type", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_facility_type_display()})"

    def distance_from(self, user_lat, user_lon):
        """Calculates distance in kilometers from given coordinate."""
        try:
            return haversine_distance_km(user_lat, user_lon, self.latitude, self.longitude)
        except Exception:
            return 9999.0
