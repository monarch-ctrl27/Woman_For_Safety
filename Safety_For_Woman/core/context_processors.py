from django.conf import settings


def site_meta(request):
    """
    Supplies global SafeHer configuration, user state, and operational
    metrics to all rendered templates (admin/moderator platform).
    """
    active_alert = None
    flagged_count = 0
    total_panic_events = 0

    if request.user.is_authenticated:
        try:
            from emergency.models import PanicAlert
            active_alert = PanicAlert.objects.filter(
                user=request.user,
                status__in=[
                    PanicAlert.STATUS_STAND_DOWN_PENDING,
                    PanicAlert.STATUS_ACTIVE,
                ]
            ).order_by("-started_at").first()
            total_panic_events = PanicAlert.objects.count()
        except Exception:
            active_alert = None

        try:
            from hotspots.models import Hotspot
            flagged_count = Hotspot.objects.filter(
                verification_status=Hotspot.STATUS_FLAGGED
            ).count()
        except Exception:
            flagged_count = 0

    return {
        "SITE_NAME": "SafeHer",
        "SITE_TAGLINE": "Admin, Moderation & Simulation Hub",
        "DEMO_MODE": getattr(settings, "SAFEHER_DEMO_MODE", True),
        "STANDDOWN_SECONDS": getattr(settings, "SAFEHER_STANDDOWN_SECONDS", 60),
        "GEOFENCE_RADIUS_KM": getattr(settings, "SAFEHER_GEOFENCE_RADIUS_KM", 0.6),
        "MAP_BOUNDS": getattr(settings, "SAFEHER_MAP_BOUNDS", {}),
        "active_emergency_alert": active_alert,
        "flagged_hotspot_count": flagged_count,
        "total_panic_events": total_panic_events,
    }
