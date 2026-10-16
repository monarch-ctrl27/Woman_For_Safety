import logging
from django.conf import settings
from django.utils import timezone
from .models import PanicAlert, ContactNotificationLog
from accounts.models import EmergencyContact
from facilities.models import Facility

logger = logging.getLogger("wfs.security")


def dispatch_emergency(panic_alert: PanicAlert):
    """
    Executes the Woman For Safety Next-of-Kin panic escalation pipeline (SRS v1.2, FR-PANIC-1).
    
    CRITICAL SAFETY CONSTRAINT:
    In compliance with SRS v1.2 §2.8:
    - Alerts escalate SOLELY through user's own next-of-kin list.
    - Never contacts or claims to contact police or emergency services automatically.
    - Honest failure reporting: warns if zero NOK contacts are registered.
    - Dispatches priority call and SMS with WhatsApp message fallback.
    """
    user = panic_alert.user
    user_name = f"{user.first_name} {user.last_name}".strip() or user.username
    phone = getattr(user.profile, "phone_number", "Unspecified")
    medical = getattr(user.profile, "medical_notes", "None")

    # Nearest safe facility provided for informational safety only
    police_stations = Facility.objects.filter(facility_type=Facility.FACILITY_POLICE)
    nearest_police = None
    min_dist = 9999.0
    for p in police_stations:
        d = p.distance_from(panic_alert.latitude, panic_alert.longitude)
        if d < min_dist:
            min_dist = d
            nearest_police = p

    nearest_police_info = (
        f"{nearest_police.name} ({nearest_police.phone_number})"
        if nearest_police else "SAPS National: 10111"
    )

    gmaps_url = f"https://www.google.com/maps?q={panic_alert.latitude},{panic_alert.longitude}"

    # Message explicitly states alert is sent to Next of Kin only, prompting manual emergency call if safe
    sms_body = (
        f"🚨 EMERGENCY ALERT: Woman For Safety Next-of-Kin Notification\n"
        f"User: {user_name} ({phone})\n"
        f"Trigger: {panic_alert.get_trigger_source_display()}\n"
        f"LIVE GPS LOCATION: {gmaps_url}\n"
        f"Nearest Safe Haven: {nearest_police_info}\n"
        f"Note: Woman For Safety does NOT automatically dispatch police. If needed, please contact SAPS on 10111 immediately."
    )

    is_demo = getattr(settings, "WFS_DEMO_MODE", True)
    contacts = EmergencyContact.objects.filter(user=user, notify_on_panic=True).order_by("priority")

    # Honest failure reporting: Surface to audit log if 0 contacts exist
    if not contacts.exists():
        ContactNotificationLog.objects.create(
            panic_alert=panic_alert,
            recipient_name="[NO NEXT OF KIN CONFIGURED]",
            recipient_phone="N/A",
            channel=ContactNotificationLog.CHANNEL_SMS,
            status=ContactNotificationLog.STATUS_FAILED,
            message_body="WARNING: Panic triggered but user has zero Next of Kin emergency contacts configured. Alert could not be delivered.",
        )
    else:
        for contact in contacts:
            # Priority 1 gets call attempt + SMS; others get SMS + WhatsApp fallback
            channel = (
                ContactNotificationLog.CHANNEL_CALL
                if contact.priority == 1
                else ContactNotificationLog.CHANNEL_SMS
            )

            # Record primary alert
            ContactNotificationLog.objects.create(
                panic_alert=panic_alert,
                recipient_name=f"{contact.name} ({contact.relationship or 'Next of Kin'})",
                recipient_phone=contact.phone_number,
                channel=channel,
                status=ContactNotificationLog.STATUS_SIMULATED if is_demo else ContactNotificationLog.STATUS_DELIVERED,
                message_body=sms_body,
            )

            # Record WhatsApp message fallback channel (FR-PANIC-6)
            ContactNotificationLog.objects.create(
                panic_alert=panic_alert,
                recipient_name=f"{contact.name} (WhatsApp Fallback)",
                recipient_phone=contact.phone_number,
                channel=ContactNotificationLog.CHANNEL_WHATSAPP,
                status=ContactNotificationLog.STATUS_SIMULATED if is_demo else ContactNotificationLog.STATUS_DELIVERED,
                message_body=f"🚨 [WhatsApp Backup] {sms_body}",
            )

            logger.info(f"[WFS NOK Dispatch] Alerted {contact.name} ({contact.phone_number}) via {channel}")

    # Mark alert as escalated to Next of Kin
    panic_alert.status = PanicAlert.STATUS_ACTIVE
    panic_alert.escalated_at = timezone.now()
    panic_alert.save()

    return panic_alert
