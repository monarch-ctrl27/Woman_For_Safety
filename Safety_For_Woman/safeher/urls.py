from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("map/", include("hotspots.urls")),
    path("facilities/", include("facilities.urls")),
    path("emergency/", include("emergency.urls")),
    path("moderation/", include("moderation.urls")),
]