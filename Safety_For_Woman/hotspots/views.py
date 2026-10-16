import json
import math
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings
from .models import Hotspot, HotspotConfirmation
from .forms import HotspotReportForm
from facilities.models import Facility
from core.ratelimit import is_rate_limited


def map_view(request):
    """
    Main interactive safety map:
    - Pins danger hotspots with live danger rings
    - Displays all safe havens (Police, Clinics, Shelters)
    - Real-time geofence proximity detection
    - Automated safe rerouting avoiding flagged hotspots
    """
    bounds = getattr(settings, "WFS_MAP_BOUNDS", {
        "lat_min": -29.16,
        "lat_max": -29.02,
        "lon_min": 26.05,
        "lon_max": 26.32,
    })
    geofence_km = getattr(settings, "WFS_GEOFENCE_RADIUS_KM", 0.6)

    context = {
        "map_bounds": bounds,
        "geofence_km": geofence_km,
        "standdown_seconds": getattr(settings, "WFS_STANDDOWN_SECONDS", 60),
    }
    return render(request, "hotspots/map.html", context)


@login_required
def report_hotspot(request):
    """
    Allows a woman to pin a dangerous area to warn the community.
    Rate limited to prevent false report flooding.
    """
    # Rate limit check (3 reports per hour)
    limit, window = getattr(settings, "WFS_REPORT_RATE_LIMIT", (3, 3600))
    if is_rate_limited(f"report:{request.user.id}", limit=limit, window_seconds=window):
        messages.error(request, "You have reached the reporting limit for this hour. Please try again later.")
        return redirect("hotspots:map")

    if request.method == "POST":
        form = HotspotReportForm(request.POST)
        if form.is_valid():
            hotspot = form.save(commit=False)
            if not hotspot.is_anonymous:
                hotspot.reported_by = request.user
            hotspot.save()

            # Record reporter's own confirmation
            HotspotConfirmation.objects.create(hotspot=hotspot, user=request.user)

            messages.success(request, f"Danger area '{hotspot.title}' pinned. Thank you for protecting other women.")
            return redirect("hotspots:map")
    else:
        # Prepopulate with optional lat/lon if passed in query string
        initial = {}
        if "lat" in request.GET and "lon" in request.GET:
            try:
                initial["latitude"] = float(request.GET["lat"])
                initial["longitude"] = float(request.GET["lon"])
            except ValueError:
                pass
        form = HotspotReportForm(initial=initial)

    return render(request, "hotspots/report.html", {"form": form})


@require_GET
def api_all_hotspots(request):
    """
    Returns all active danger zones for map rendering.
    """
    hotspots = Hotspot.objects.filter(active=True).select_related("reported_by")
    features = []

    for h in hotspots:
        features.append({
            "id": h.id,
            "title": h.title,
            "category": h.get_category_display(),
            "category_code": h.category,
            "description": h.description,
            "severity": h.severity,
            "severity_label": h.get_severity_display(),
            "lat": h.latitude,
            "lon": h.longitude,
            "radius_meters": h.danger_radius_meters,
            "risk_time": h.get_risk_time_display(),
            "confirmations": h.confirmations_count,
            "created_at": h.created_at.strftime("%Y-%m-%d %H:%M"),
            "corridor_code": h.corridor,
            "corridor_label": h.get_corridor_display(),
            "verification_status": h.verification_status,
            "reporter": h.reported_by.username if h.reported_by and not h.is_anonymous else "Anonymous",
        })

    return JsonResponse({"status": "ok", "hotspots": features})


@require_GET
def api_check_geofence(request):
    """
    Proximity check: receives user's GPS coords.
    If within geofence radius (0.6 km = 600m) of an active danger zone:
    notifies client to vibrate phone and trigger stand-down protocol.
    """
    try:
        lat = float(request.GET.get("lat"))
        lon = float(request.GET.get("lon"))
    except (TypeError, ValueError):
        return JsonResponse({"status": "error", "message": "Invalid coordinates"}, status=400)

    geofence_km = getattr(settings, "WFS_GEOFENCE_RADIUS_KM", 0.6)
    active_hotspots = Hotspot.objects.filter(active=True)

    nearest_danger = None
    min_dist_km = 9999.0

    for h in active_hotspots:
        dist_km = h.distance_from(lat, lon)
        if dist_km <= geofence_km and dist_km < min_dist_km:
            min_dist_km = dist_km
            nearest_danger = h

    if nearest_danger:
        dist_m = int(min_dist_km * 1000)
        return JsonResponse({
            "status": "warning",
            "approaching_danger": True,
            "distance_meters": dist_m,
            "vibrate": True,
            "standdown_window_seconds": getattr(settings, "WFS_STANDDOWN_SECONDS", 60),
            "hotspot": {
                "id": nearest_danger.id,
                "title": nearest_danger.title,
                "category": nearest_danger.get_category_display(),
                "severity": nearest_danger.severity,
                "severity_label": nearest_danger.get_severity_display(),
                "description": nearest_danger.description,
                "lat": nearest_danger.latitude,
                "lon": nearest_danger.longitude,
                "radius_meters": nearest_danger.danger_radius_meters,
            }
        })

    return JsonResponse({
        "status": "ok",
        "approaching_danger": False,
        "distance_meters": None,
        "vibrate": False,
    })


@require_GET
def api_safe_route(request):
    """
    Calculates safe walking route from start to destination, automatically
    diverting around any active danger hotspots.
    Takes `start_lat`, `start_lon`, `dest_lat`, `dest_lon`.
    """
    try:
        s_lat = float(request.GET.get("start_lat"))
        s_lon = float(request.GET.get("start_lon"))
        d_lat = float(request.GET.get("dest_lat"))
        d_lon = float(request.GET.get("dest_lon"))
    except (TypeError, ValueError):
        return JsonResponse({"status": "error", "message": "Invalid origin or destination coordinates"}, status=400)

    # Find hotspots along or near the direct vector
    active_hotspots = Hotspot.objects.filter(active=True)
    waypoints = [[s_lat, s_lon]]
    detours_taken = []

    # Check each hotspot if it intersects or is too close to line segment
    for h in active_hotspots:
        # Distance from hotspot to start and dest
        d_start = h.distance_from(s_lat, s_lon)
        d_dest = h.distance_from(d_lat, d_lon)
        total_trip_dist = math.hypot(d_lat - s_lat, d_lon - s_lon) * 111.0

        # Simplified projection distance to segment
        # If hotspot is between origin and destination:
        if d_start < total_trip_dist and d_dest < total_trip_dist:
            buffer_km = (h.danger_radius_meters / 1000.0) + 0.15  # buffer clearance
            # Detour around the circle perpendicularly
            dx = d_lon - s_lon
            dy = d_lat - s_lat
            seg_len = math.hypot(dx, dy)
            if seg_len > 0.0001:
                # Perpendicular unit vector
                perp_lat = -dx / seg_len
                perp_lon = dy / seg_len

                detour_lat = h.latitude + perp_lat * (buffer_km / 111.0)
                detour_lon = h.longitude + perp_lon * (buffer_km / (111.0 * math.cos(math.radians(h.latitude))))

                waypoints.append([round(detour_lat, 6), round(detour_lon, 6)])
                detours_taken.append({
                    "bypassed_hotspot_id": h.id,
                    "title": h.title,
                    "severity": h.severity,
                })

    waypoints.append([d_lat, d_lon])

    return JsonResponse({
        "status": "ok",
        "route_waypoints": waypoints,
        "detours_count": len(detours_taken),
        "bypassed_hotspots": detours_taken,
        "direct_route": [[s_lat, s_lon], [d_lat, d_lon]],
    })


@login_required
@require_POST
def confirm_hotspot(request, hotspot_id):
    """
    Allows a woman to upvote / peer-confirm a danger area.
    """
    hotspot = get_object_or_404(Hotspot, id=hotspot_id)
    confirmation, created = HotspotConfirmation.objects.get_or_create(hotspot=hotspot, user=request.user)

    if created:
        hotspot.confirmations_count = hotspot.confirmations.count()
        hotspot.save()
        return JsonResponse({"status": "ok", "confirmations": hotspot.confirmations_count, "action": "confirmed"})
    else:
        return JsonResponse({"status": "already_confirmed", "confirmations": hotspot.confirmations_count})
