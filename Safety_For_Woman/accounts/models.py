from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """
    Extends standard Django user with role and safety configuration.
    Supports: Primary User, Community Moderator, Institutional Partner, Admin.
    """
    ROLE_USER = "user"
    ROLE_MODERATOR = "moderator"
    ROLE_ADMIN = "admin"
    ROLE_INSTITUTIONAL = "institutional"

    ROLE_CHOICES = [
        (ROLE_USER, "Mobile End User"),
        (ROLE_MODERATOR, "Community Safety Moderator"),
        (ROLE_ADMIN, "System Administrator"),
        (ROLE_INSTITUTIONAL, "Institutional Partner (Campus/BID)"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_USER, db_index=True)
    phone_number = models.CharField(max_length=25, blank=True, help_text="e.g. +27 82 123 4567")
    safe_pin = models.CharField(
        max_length=10,
        default="1234",
        help_text="4-digit PIN required to stand down an active countdown or cancel panic."
    )
    voice_trigger_enabled = models.BooleanField(default=True)
    triple_press_enabled = models.BooleanField(default=True)
    fall_detection_enabled = models.BooleanField(default=True)
    geofence_vibration_enabled = models.BooleanField(default=True)
    medical_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} [{self.get_role_display()}]"


class EmergencyContact(models.Model):
    PRIORITY_CHOICES = [
        (1, "Primary (Immediate Call & SMS)"),
        (2, "Secondary (SMS & WhatsApp Alert)"),
        (3, "Tertiary (SMS & WhatsApp Alert)"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emergency_contacts")
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=25)
    email = models.EmailField(blank=True)
    priority = models.PositiveSmallIntegerField(choices=PRIORITY_CHOICES, default=1)
    notify_on_panic = models.BooleanField(default=True)
    notify_on_standdown_expire = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["priority", "created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_priority_display()}) - {self.phone_number}"


class InstitutionalAccount(models.Model):
    """
    Supports FR-PAY-3, FR-PAY-8, and SRS §6.1 / §12.
    Enterprise / institutional licence holders: student residences, university safety,
    retailers/BIDs (Business Improvement Districts), and private security partners.
    """
    TYPE_CHOICES = [
        ("residence", "Student Residence / Housing Complex"),
        ("university", "University Campus Safety Directorate"),
        ("retailer_bid", "Retailer / Business Improvement District (BID)"),
        ("insurer", "Underwriter / Risk Partner"),
        ("ngo", "GBV / Women Safety NGO"),
    ]

    PLAN_CHOICES = [
        ("free_pilot", "Free Community Pilot"),
        ("institutional_standard", "Standard Institutional (R2,500/mo)"),
        ("institutional_campus", "Campus Enterprise (R8,500/mo)"),
        ("active_zone_sponsor", "Active Zone Retailer Sponsor (R1,200/mo)"),
    ]

    STATUS_CHOICES = [
        ("active", "Active (Paid via PayFast)"),
        ("trial", "Pilot Evaluation"),
        ("past_due", "Past Due / Pending Renewal"),
    ]

    name = models.CharField(max_length=150)
    institution_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default="residence")
    contact_person = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=25, blank=True)
    plan = models.CharField(max_length=30, choices=PLAN_CHOICES, default="institutional_standard")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    covered_corridor = models.CharField(max_length=100, default="Westdene & Willows Student Belt")
    active_students_protected = models.PositiveIntegerField(default=450)
    monthly_subscription_zar = models.DecimalField(max_digits=10, decimal_places=2, default=2500.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_institution_type_display()}) - {self.status}"
