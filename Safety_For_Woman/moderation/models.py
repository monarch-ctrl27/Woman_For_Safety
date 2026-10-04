from django.db import models
from django.contrib.auth.models import User
from hotspots.models import Hotspot


class ModerationLog(models.Model):
    """
    ModerationAction audit trail (SRS §6.1 & FR-MOD-3).
    Tracks every post-publication moderation decision:
    who reviewed, what decision, when, and reason.
    """
    ACTION_KEPT = "kept"
    ACTION_REMOVED = "removed"
    ACTION_FLAGGED = "flagged"
    ACTION_RADIUS_ADJUSTED = "radius_adjusted"

    ACTION_CHOICES = [
        (ACTION_KEPT, "Kept / Approved as Genuine Hazard"),
        (ACTION_REMOVED, "Removed from Live Map"),
        (ACTION_FLAGGED, "Flagged / Disputed by Community"),
        (ACTION_RADIUS_ADJUSTED, "Danger Radius Modified"),
    ]

    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    hotspot = models.ForeignKey(Hotspot, on_delete=models.CASCADE, related_name="moderation_logs")
    action = models.CharField(max_length=30, choices=ACTION_CHOICES, default=ACTION_KEPT)
    reason = models.TextField(help_text="Audit explanation for this moderation decision.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} on '{self.hotspot.title}' by {self.moderator or 'System'}"
