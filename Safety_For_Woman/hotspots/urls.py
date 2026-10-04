from django.urls import path
from . import views

app_name = "hotspots"

urlpatterns = [
    path("", views.map_view, name="map"),
    path("report/", views.report_hotspot, name="report"),
    path("api/all/", views.api_all_hotspots, name="api_all"),
    path("api/check-geofence/", views.api_check_geofence, name="api_check_geofence"),
    path("api/safe-route/", views.api_safe_route, name="api_safe_route"),
    path("api/confirm/<int:hotspot_id>/", views.confirm_hotspot, name="confirm"),
]
