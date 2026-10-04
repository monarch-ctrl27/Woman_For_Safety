from django import forms
from .models import Hotspot


class HotspotReportForm(forms.ModelForm):
    class Meta:
        model = Hotspot
        fields = [
            "title",
            "category",
            "severity",
            "risk_time",
            "danger_radius_meters",
            "description",
            "latitude",
            "longitude",
            "is_anonymous",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Broken lights alley near station"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "severity": forms.Select(attrs={"class": "form-control"}),
            "risk_time": forms.Select(attrs={"class": "form-control"}),
            "danger_radius_meters": forms.NumberInput(attrs={"class": "form-control", "min": 50, "max": 1000}),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "What happened or why is this spot unsafe? (e.g. Men loitering in unlit corridor, regular catcalling after 7pm)"
            }),
            "latitude": forms.HiddenInput(attrs={"id": "id_latitude"}),
            "longitude": forms.HiddenInput(attrs={"id": "id_longitude"}),
            "is_anonymous": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
