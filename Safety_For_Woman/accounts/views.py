import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Profile, EmergencyContact
from .forms import UserRegisterForm, ProfileUpdateForm, EmergencyContactForm
from core.ratelimit import is_rate_limited


def register_view(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            # Profile is auto-created by signal, update extra fields
            profile = user.profile
            profile.phone_number = form.cleaned_data.get("phone_number", "")
            profile.safe_pin = form.cleaned_data.get("safe_pin", "1234")
            profile.save()

            login(request, user)
            messages.success(request, f"Welcome to SafeHer, {user.first_name or user.username}! Please add your trusted emergency contacts.")
            return redirect("accounts:contacts")
    else:
        form = UserRegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}. SafeHer hands-free triggers are armed.")
            next_url = request.GET.get("next") or "core:dashboard"
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out safely.")
    return redirect("core:home")


@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your safety settings have been updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, "accounts/profile.html", {"form": form, "profile": profile})


@login_required
def contacts_view(request):
    contacts = EmergencyContact.objects.filter(user=request.user)

    if request.method == "POST":
        # Check contact edit rate limit (10 / hr)
        if is_rate_limited(f"contact_edit:{request.user.id}", limit=10, window_seconds=3600):
            messages.error(request, "Too many contact edits. Please wait a moment before trying again.")
            return redirect("accounts:contacts")

        form = EmergencyContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            messages.success(request, f"Added {contact.name} to your emergency alert network.")
            return redirect("accounts:contacts")
    else:
        form = EmergencyContactForm()

    return render(request, "accounts/contacts.html", {"contacts": contacts, "form": form})


@login_required
@require_POST
def contact_delete(request, contact_id):
    contact = get_object_or_404(EmergencyContact, id=contact_id, user=request.user)
    name = contact.name
    contact.delete()
    messages.info(request, f"Removed {name} from your emergency contacts.")
    return redirect("accounts:contacts")


@login_required
@require_POST
def api_toggle_handsfree(request):
    """
    AJAX endpoint for toggling hands-free sensors (voice trigger, triple-press, fall detection).
    """
    try:
        data = json.loads(request.body)
        profile = request.user.profile

        if "voice" in data:
            profile.voice_trigger_enabled = bool(data["voice"])
        if "triple_press" in data:
            profile.triple_press_enabled = bool(data["triple_press"])
        if "fall" in data:
            profile.fall_detection_enabled = bool(data["fall"])
        if "geofence" in data:
            profile.geofence_vibration_enabled = bool(data["geofence"])

        profile.save()
        return JsonResponse({
            "status": "ok",
            "voice": profile.voice_trigger_enabled,
            "triple_press": profile.triple_press_enabled,
            "fall": profile.fall_detection_enabled,
            "geofence": profile.geofence_vibration_enabled,
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
