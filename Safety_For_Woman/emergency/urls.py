from django.urls import path
from . import views

app_name = "emergency"

urlpatterns = [
    path("trigger/", views.trigger_panic, name="trigger"),
    path("stand-down/<int:alert_id>/", views.stand_down_view, name="stand_down"),
    path("stand-down/<int:alert_id>/cancel/", views.stand_down_cancel, name="cancel"),
    path("stand-down/<int:alert_id>/escalate/", views.escalate_now, name="escalate"),
    path("api/status/<int:alert_id>/", views.api_alert_status, name="api_status"),
    path("history/", views.emergency_history, name="history"),
    path("simulation/", views.simulation_center, name="simulation"),
]
