from django import forms
from django.contrib.auth.models import User
from .models import Profile, EmergencyContact


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Create a strong password (min 10 chars)"}),
        label="Password",
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm your password"}),
        label="Confirm Password",
    )
    phone_number = forms.CharField(
        max_length=25,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+27 82 000 0000"}),
        label="Mobile Number",
    )
    safe_pin = forms.CharField(
        max_length=4,
        min_length=4,
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control text-center", "placeholder": "4-digit Safe PIN", "maxlength": "4"}),
        help_text="Secret 4-digit PIN used to stand down countdowns or disarm alerts.",
        label="Safe Stand-Down PIN",
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Choose a username"}),
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "name@example.com"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("confirm_password")
        if p1 and p2 and p1 != p2:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "phone_number",
            "safe_pin",
            "voice_trigger_enabled",
            "triple_press_enabled",
            "fall_detection_enabled",
            "geofence_vibration_enabled",
            "medical_notes",
        ]
        widgets = {
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "safe_pin": forms.TextInput(attrs={"class": "form-control", "maxlength": "6"}),
            "medical_notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = [
            "name",
            "relationship",
            "phone_number",
            "email",
            "priority",
            "notify_on_panic",
            "notify_on_standdown_expire",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Contact Full Name"}),
            "relationship": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Sister, Mom, Friend"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "+27 82 123 4567"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "contact@example.com"}),
            "priority": forms.Select(attrs={"class": "form-control"}),
        }
