from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("contacts/", views.contacts_view, name="contacts"),
    path("contacts/<int:contact_id>/delete/", views.contact_delete, name="contact_delete"),
    path("api/toggle-handsfree/", views.api_toggle_handsfree, name="api_toggle_handsfree"),
]
