from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from hotspots.models import Hotspot
from facilities.models import Facility
from emergency.models import PanicAlert
from accounts.models import EmergencyContact, InstitutionalAccount


def home(request):
    """
    Operations platform landing page.
    Redirects authenticated users to the ops dashboard.
    """
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    total_hotspots = Hotspot.objects.filter(active=True).count()
    total_facilities = Facility.objects.count()

    context = {
        "total_hotspots": total_hotspots,
        "total_facilities": total_facilities,
    }
    return render(request, "core/home.html", context)


@login_required
def dashboard(request):
    """
    Admin / Moderator Operations Dashboard.
    Provides at-a-glance metrics, flagged hotspot queue,
    recent panic simulations, institutional partner overview,
    and quick navigation to all operational views.
    """
    user = request.user
    contacts = EmergencyContact.objects.filter(user=user).order_by("priority", "created_at")

    # Hotspot stats
    active_hotspots = Hotspot.objects.filter(active=True)
    flagged_hotspots = active_hotspots.filter(verification_status=Hotspot.STATUS_FLAGGED)
    recent_flagged = flagged_hotspots.order_by("-created_at")[:5]
    recent_hotspots = active_hotspots.order_by("-created_at")[:5]

    # Panic simulation stats
    recent_panics = PanicAlert.objects.all()[:5]
    total_panics = PanicAlert.objects.count()

    # Facilities count
    total_facilities = Facility.objects.count()
    facilities_sample = Facility.objects.all()[:4]

    # Institutional partners
    institutional_accounts = InstitutionalAccount.objects.all()

    # Active alert (for simulation banner)
    active_alert = PanicAlert.objects.filter(
        user=user,
        status__in=[PanicAlert.STATUS_STAND_DOWN_PENDING, PanicAlert.STATUS_ACTIVE]
    ).order_by("-started_at").first()

    context = {
        "contacts": contacts,
        "contacts_count": contacts.count(),
        "recent_hotspots": recent_hotspots,
        "recent_flagged": recent_flagged,
        "flagged_count": flagged_hotspots.count(),
        "total_active_hotspots": active_hotspots.count(),
        "recent_panics": recent_panics,
        "total_panics": total_panics,
        "total_facilities": total_facilities,
        "facilities_sample": facilities_sample,
        "institutional_accounts": institutional_accounts,
        "active_alert": active_alert,
        "demo_mode": getattr(settings, "SAFEHER_DEMO_MODE", True),
    }
    return render(request, "core/dashboard.html", context)


def about(request):
    """
    Mission statement, emergency helpline directory, and technical safety details.
    """
    return render(request, "core/about.html")
