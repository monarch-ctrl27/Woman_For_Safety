from django.contrib import admin
from .models import Hotspot, HotspotConfirmation


@admin.register(Hotspot)
class HotspotAdmin(admin.ModelAdmin):
    list_display = ("title", "corridor", "category", "severity", "verification_status", "danger_radius_meters", "confirmations_count", "created_at")
    list_filter = ("verification_status", "corridor", "severity", "category", "risk_time", "active")
    search_fields = ("title", "description", "flag_reason")


@admin.register(HotspotConfirmation)
class HotspotConfirmationAdmin(admin.ModelAdmin):
    list_display = ("hotspot", "user", "created_at")
