from django.contrib import admin
from .models import ModerationLog


@admin.register(ModerationLog)
class ModerationLogAdmin(admin.ModelAdmin):
    list_display = ("action", "hotspot", "moderator", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("hotspot__title", "reason")
