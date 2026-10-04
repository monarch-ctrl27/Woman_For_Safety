from django.urls import path
from . import views

app_name = "facilities"

urlpatterns = [
    path("", views.facility_list, name="list"),
    path("api/nearest/", views.api_nearest_facilities, name="api_nearest"),
]
