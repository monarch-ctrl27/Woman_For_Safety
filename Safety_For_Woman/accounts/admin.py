from django.contrib import admin
from .models import Profile, EmergencyContact, InstitutionalAccount


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "phone_number", "voice_trigger_enabled", "triple_press_enabled", "fall_detection_enabled", "geofence_vibration_enabled")
    list_filter = ("role", "voice_trigger_enabled", "triple_press_enabled", "fall_detection_enabled")
    search_fields = ("user__username", "user__email", "phone_number")


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "relationship", "phone_number", "priority", "notify_on_panic")
    list_filter = ("priority", "notify_on_panic")
    search_fields = ("name", "phone_number", "user__username")


@admin.register(InstitutionalAccount)
class InstitutionalAccountAdmin(admin.ModelAdmin):
    list_display = ("name", "institution_type", "plan", "status", "covered_corridor", "active_students_protected", "monthly_subscription_zar")
    list_filter = ("institution_type", "plan", "status")
    search_fields = ("name", "contact_person", "contact_email", "covered_corridor")
