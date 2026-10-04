from django.urls import path
from . import views

app_name = "moderation"

urlpatterns = [
    path("", views.moderation_dashboard, name="dashboard"),
    path("review/<int:hotspot_id>/", views.review_hotspot, name="review"),
    path("log/", views.moderation_log_view, name="log"),
]
