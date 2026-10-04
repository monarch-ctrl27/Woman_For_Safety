from django.contrib import admin
from .models import Facility


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ("name", "facility_type", "phone_number", "is_24_hours", "has_victim_support_room")
    list_filter = ("facility_type", "is_24_hours", "has_victim_support_room")
    search_fields = ("name", "address", "phone_number")
