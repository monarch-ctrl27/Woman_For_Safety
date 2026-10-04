import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings
from django.utils import timezone
from .models import PanicAlert, ContactNotificationLog
from .services import dispatch_emergency
from accounts.models import EmergencyContact
from hotspots.models import Hotspot
from core.ratelimit import is_rate_limited


@login_required
def trigger_panic(request):
    """
    Unified entrypoint for the SafeHer Panic Pipeline (FR-PANIC).
    Supports: Manual button, Voice 'Help', Fall detection, Triple-press, Geofence timeout.
    """
    if request.method == "POST":
        if request.content_type == "application/json":
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                data = {}
        else:
            data = request.POST

        trigger_source = data.get("trigger_source", PanicAlert.TRIGGER_MANUAL)
        immediate = str(data.get("immediate", "false")).lower() in ("1", "true", "yes")

        # Bloemfontein reference coords default
        try:
            lat = float(data.get("latitude", -29.1181))
            lon = float(data.get("longitude", 26.2249))
        except (TypeError, ValueError):
            lat, lon = -29.1181, 26.2249

        battery = None
        try:
            if "battery_level" in data and data["battery_level"] is not None:
                battery = int(float(data["battery_level"]))
        except (ValueError, TypeError):
            battery = None

        hotspot_id = data.get("hotspot_id")
        hotspot = Hotspot.objects.filter(id=hotspot_id).first() if hotspot_id else None

        # Check Next of Kin warning (FR-PANIC-9: surface to user if no NOK configured)
        nok_exists = EmergencyContact.objects.filter(user=request.user, notify_on_panic=True).exists()

        standdown_total = getattr(settings, "SAFEHER_STANDDOWN_SECONDS", 60)

        # Create alert record
        alert = PanicAlert.objects.create(
            user=request.user,
            trigger_source=trigger_source,
            status=PanicAlert.STATUS_STAND_DOWN_PENDING,
            latitude=lat,
            longitude=lon,
            battery_level=battery,
            standdown_seconds_total=standdown_total,
            hotspot_approached=hotspot,
        )

        if immediate:
            dispatch_emergency(alert)
            if request.content_type == "application/json":
                return JsonResponse({
                    "status": "escalated",
                    "alert_id": alert.id,
                    "nok_configured": nok_exists,
                    "redirect_url": f"/emergency/stand-down/{alert.id}/"
                })
            return redirect("emergency:stand_down", alert_id=alert.id)

        if request.content_type == "application/json":
            return JsonResponse({
                "status": "stand_down_started",
                "alert_id": alert.id,
                "seconds_remaining": standdown_total,
                "nok_configured": nok_exists,
                "redirect_url": f"/emergency/stand-down/{alert.id}/"
            })

        return redirect("emergency:stand_down", alert_id=alert.id)

    # GET redirect
    active = PanicAlert.objects.filter(
        user=request.user,
        status__in=[PanicAlert.STATUS_STAND_DOWN_PENDING, PanicAlert.STATUS_ACTIVE]
    ).first()
    if active:
        return redirect("emergency:stand_down", alert_id=active.id)

    return redirect("core:dashboard")


@login_required
def stand_down_view(request, alert_id):
    """
    Renders 60-second Stand-Down countdown window (FR-GEO-2, FR-GEO-3).
    Displays prominent 'False Alarm' cancel button.
    """
    alert = get_object_or_404(PanicAlert, id=alert_id, user=request.user)

    if alert.is_stand_down_expired and alert.status == PanicAlert.STATUS_STAND_DOWN_PENDING:
        dispatch_emergency(alert)

    notifications = alert.notifications.all()
    nok_count = EmergencyContact.objects.filter(user=request.user, notify_on_panic=True).count()

    context = {
        "alert": alert,
        "seconds_remaining": alert.seconds_remaining,
        "notifications": notifications,
        "nok_count": nok_count,
        "is_demo": getattr(settings, "SAFEHER_DEMO_MODE", True),
    }
    return render(request, "emergency/stand_down.html", context)


@login_required
@require_POST
def stand_down_cancel(request, alert_id):
    """
    Resolves alert via False Alarm cancellation (FR-GEO-3, §12.1).
    """
    alert = get_object_or_404(PanicAlert, id=alert_id, user=request.user)
    pin = request.POST.get("pin", "").strip()
    profile = request.user.profile
    expected_pin = profile.safe_pin or "1234"

    # Allow cancellation if PIN matches or in demo mode with PIN provided
    if pin == expected_pin or (not pin and getattr(settings, "SAFEHER_DEMO_MODE", True)):
        alert.status = PanicAlert.STATUS_FALSE_ALARM
        alert.stood_down_at = timezone.now()
        alert.save()
        messages.success(request, "Alert resolved: Recorded as False Alarm. You are safe.")
        return redirect("core:dashboard")
    else:
        messages.error(request, "Incorrect Safe PIN! Stand-down rejected.")
        return redirect("emergency:stand_down", alert_id=alert.id)


@login_required
@require_POST
def escalate_now(request, alert_id):
    """
    Manual override: immediately skip countdown and dispatch to Next of Kin.
    """
    alert = get_object_or_404(PanicAlert, id=alert_id, user=request.user)
    if alert.status == PanicAlert.STATUS_STAND_DOWN_PENDING:
        dispatch_emergency(alert)
        messages.warning(request, "Alert escalated to your Next of Kin contacts.")

    return redirect("emergency:stand_down", alert_id=alert.id)


@login_required
@require_GET
def api_alert_status(request, alert_id):
    """
    Polled by simulator and stand-down countdown page.
    Automatically escalates to Next of Kin when timer reaches 0.
    """
    alert = get_object_or_404(PanicAlert, id=alert_id, user=request.user)

    if alert.is_stand_down_expired and alert.status == PanicAlert.STATUS_STAND_DOWN_PENDING:
        dispatch_emergency(alert)

    notifications_data = [
        {
            "recipient": n.recipient_name,
            "channel": n.get_channel_display(),
            "status": n.get_status_display(),
            "time": n.sent_at.strftime("%H:%M:%S"),
            "body": n.message_body,
        }
        for n in alert.notifications.all()
    ]

    return JsonResponse({
        "status": alert.status,
        "seconds_remaining": alert.seconds_remaining,
        "is_expired": alert.is_stand_down_expired,
        "notifications": notifications_data,
        "coords": {"lat": alert.latitude, "lon": alert.longitude},
    })


@login_required
def emergency_history(request):
    alerts = PanicAlert.objects.filter(user=request.user).order_by("-started_at")
    return render(request, "emergency/history.html", {"alerts": alerts})


@login_required
def simulation_center(request):
    """
    Simulation & Pipeline Testing Cockpit (FR-PREV-1, FR-PREV-2, FR-PANIC).
    Allows administrators, moderators, and evaluators to trigger and inspect
    the full emergency pipeline in a safe preview environment:
    - Hands-free Voice Distress ('Help!')
    - Accelerometer Fall Detection
    - Triple-Press Power/Hardware Key
    - Geofence Proximity & 60-Second Stand-Down
    - Next-of-Kin Dual-Channel Dispatch (Voice/SMS + WhatsApp Backup)
    - Safe PIN Cancellation ('False Alarm')
    """
    user = request.user
    contacts = EmergencyContact.objects.filter(user=user).order_by("priority")
    hotspots = Hotspot.objects.filter(active=True).order_by("title")
    recent_simulations = PanicAlert.objects.filter(user=user).order_by("-started_at")[:8]
    active_alert = PanicAlert.objects.filter(
        user=user,
        status__in=[PanicAlert.STATUS_STAND_DOWN_PENDING, PanicAlert.STATUS_ACTIVE]
    ).order_by("-started_at").first()

    context = {
        "contacts": contacts,
        "contacts_count": contacts.count(),
        "hotspots": hotspots,
        "recent_simulations": recent_simulations,
        "active_alert": active_alert,
        "safe_pin": getattr(user.profile, "safe_pin", "2468"),
        "is_demo": getattr(settings, "SAFEHER_DEMO_MODE", True),
    }
    return render(request, "emergency/simulation.html", context)

