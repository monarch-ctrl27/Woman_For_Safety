from django.shortcuts import render
from django.http import JsonResponse
from .models import Facility


def facility_list(request):
    """
    Directory of safe facilities with filtering by type.
    """
    facility_type = request.GET.get("type", "").upper()
    queryset = Facility.objects.all()

    if facility_type in [Facility.FACILITY_POLICE, Facility.FACILITY_HOSPITAL, Facility.FACILITY_CLINIC, Facility.FACILITY_SHELTER]:
        queryset = queryset.filter(facility_type=facility_type)

    context = {
        "facilities": queryset,
        "selected_type": facility_type,
    }
    return render(request, "facilities/list.html", context)


def api_nearest_facilities(request):
    """
    API endpoint accepting lat & lon query params.
    Returns the nearest Police Station, Hospital/Clinic, and Shelter
    with computed distance in km, direct phone links, and navigation coords.
    """
    try:
        lat = float(request.GET.get("lat"))
        lon = float(request.GET.get("lon"))
    except (TypeError, ValueError):
        # Default to Bloemfontein central if no coords provided
        lat, lon = -29.1181, 26.2249

    facilities = Facility.objects.all()
    facility_data = []

    for fac in facilities:
        dist_km = fac.distance_from(lat, lon)
        facility_data.append({
            "id": fac.id,
            "name": fac.name,
            "type": fac.facility_type,
            "type_label": fac.get_facility_type_display(),
            "address": fac.address,
            "phone": fac.phone_number,
            "hotline": fac.emergency_hotline or fac.phone_number,
            "lat": fac.latitude,
            "lon": fac.longitude,
            "is_24_hours": fac.is_24_hours,
            "distance_km": round(dist_km, 2),
            "distance_meters": int(dist_km * 1000),
            "has_victim_room": fac.has_victim_support_room,
            "notes": fac.services_notes,
        })

    # Sort all by distance
    facility_data.sort(key=lambda x: x["distance_km"])

    # Extract nearest of each category
    nearest_by_type = {}
    for item in facility_data:
        ftype = item["type"]
        if ftype not in nearest_by_type:
            nearest_by_type[ftype] = item

    return JsonResponse({
        "status": "ok",
        "user_coords": {"lat": lat, "lon": lon},
        "nearest_summary": nearest_by_type,
        "all_nearby": facility_data[:10],
    })
