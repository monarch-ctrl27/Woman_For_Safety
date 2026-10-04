from django.contrib import admin
from .models import PanicAlert, ContactNotificationLog


class ContactNotificationLogInline(admin.TabularInline):
    model = ContactNotificationLog
    extra = 0
    readonly_fields = ("recipient_name", "recipient_phone", "channel", "status", "message_body", "sent_at")


@admin.register(PanicAlert)
class PanicAlertAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "trigger_source", "status", "latitude", "longitude", "started_at", "escalated_at")
    list_filter = ("status", "trigger_source", "started_at")
    search_fields = ("user__username", "user__email")
    inlines = [ContactNotificationLogInline]


@admin.register(ContactNotificationLog)
class ContactNotificationLogAdmin(admin.ModelAdmin):
    list_display = ("panic_alert", "recipient_name", "channel", "status", "sent_at")
    list_filter = ("channel", "status", "sent_at")
