from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField
from hotspots.models import Hotspot
from .models import ModerationLog


@login_required
def moderation_dashboard(request):
    """
    Moderator / Admin Hotspot Review Dashboard.
    Groups hotspots by verification status:
    Flagged (priority review) -> Disputed -> Published -> Removed.
    Supports corridor filtering via GET parameter `corridor`.
    """
    selected_corridor = request.GET.get("corridor", "").strip()

    qs = Hotspot.objects.all().select_related("reported_by")
    if selected_corridor:
        qs = qs.filter(corridor=selected_corridor)

    # Order by verification_status: flagged first, then disputed, published, removed
    hotspots = qs.annotate(
        status_priority=Case(
            When(verification_status=Hotspot.STATUS_FLAGGED, then=Value(1)),
            When(verification_status=Hotspot.STATUS_DISPUTED, then=Value(2)),
            When(verification_status=Hotspot.STATUS_PUBLISHED, then=Value(3)),
            When(verification_status=Hotspot.STATUS_REMOVED, then=Value(4)),
            default=Value(5),
            output_field=IntegerField(),
        )
    ).order_by("status_priority", "-created_at")

    flagged_count = qs.filter(verification_status=Hotspot.STATUS_FLAGGED).count()
    published_count = qs.filter(verification_status=Hotspot.STATUS_PUBLISHED).count()
    removed_count = qs.filter(verification_status=Hotspot.STATUS_REMOVED).count()
    total_count = qs.count()

    context = {
        "hotspots": hotspots,
        "flagged_count": flagged_count,
        "published_count": published_count,
        "removed_count": removed_count,
        "total_count": total_count,
        "selected_corridor": selected_corridor,
        "corridor_choices": Hotspot.CORRIDOR_CHOICES,
    }
    return render(request, "moderation/dashboard.html", context)


@login_required
def review_hotspot(request, hotspot_id):
    """
    GET: Displays hotspot details and moderation decision form.
    POST: Applies moderation action:
      - updates hotspot.verification_status
      - updates hotspot.active (removed=inactive)
      - creates ModerationLog entry
      - redirects back to dashboard with success message
    """
    hotspot = get_object_or_404(Hotspot, id=hotspot_id)

    if request.method == "POST":
        action = request.POST.get("action", "").strip()
        status_input = request.POST.get("verification_status", "").strip()
        reason = request.POST.get("reason", "").strip()
        radius_input = request.POST.get("danger_radius_meters", "").strip()

        # Handle either action or verification_status submitted
        chosen = action or status_input

        if chosen in ["removed", Hotspot.STATUS_REMOVED]:
            hotspot.verification_status = Hotspot.STATUS_REMOVED
            hotspot.active = False
            log_action = ModerationLog.ACTION_REMOVED
            action_desc = "removed from live map"
        elif chosen in ["kept", "published", Hotspot.STATUS_PUBLISHED, "approved"]:
            hotspot.verification_status = Hotspot.STATUS_PUBLISHED
            hotspot.active = True
            log_action = ModerationLog.ACTION_KEPT
            action_desc = "approved as genuine hazard and kept on live map"
        elif chosen in ["radius_adjusted", ModerationLog.ACTION_RADIUS_ADJUSTED]:
            hotspot.verification_status = Hotspot.STATUS_PUBLISHED
            hotspot.active = True
            log_action = ModerationLog.ACTION_RADIUS_ADJUSTED
            action_desc = "danger radius updated"
        elif chosen in ["flagged", Hotspot.STATUS_FLAGGED]:
            hotspot.verification_status = Hotspot.STATUS_FLAGGED
            hotspot.active = True
            log_action = ModerationLog.ACTION_FLAGGED
            action_desc = "flagged for review"
        elif chosen in ["disputed", Hotspot.STATUS_DISPUTED]:
            hotspot.verification_status = Hotspot.STATUS_DISPUTED
            hotspot.active = True
            log_action = ModerationLog.ACTION_FLAGGED
            action_desc = "marked as disputed"
        else:
            hotspot.verification_status = status_input or Hotspot.STATUS_PUBLISHED
            hotspot.active = (hotspot.verification_status != Hotspot.STATUS_REMOVED)
            log_action = ModerationLog.ACTION_KEPT
            action_desc = "updated"

        # Update danger radius if provided
        if radius_input:
            try:
                r_val = int(radius_input)
                if r_val > 0:
                    hotspot.danger_radius_meters = r_val
            except ValueError:
                pass

        if not reason:
            reason = f"Moderation action '{log_action}' applied by {request.user.username}."

        hotspot.save()

        # Create audit log entry
        ModerationLog.objects.create(
            moderator=request.user,
            hotspot=hotspot,
            action=log_action,
            reason=reason,
        )

        messages.success(request, f"Hotspot '{hotspot.title}' was successfully {action_desc}.")
        return redirect("moderation:dashboard")

    # GET
    recent_logs = hotspot.moderation_logs.all().order_by("-created_at")
    context = {
        "hotspot": hotspot,
        "moderation_logs": recent_logs,
        "action_choices": ModerationLog.ACTION_CHOICES,
        "status_choices": Hotspot.STATUS_CHOICES,
    }
    return render(request, "moderation/review.html", context)


@login_required
def moderation_log_view(request):
    """
    Shows all ModerationLog audit trail entries ordered by -created_at.
    """
    logs = ModerationLog.objects.all().select_related("moderator", "hotspot").order_by("-created_at")
    context = {
        "logs": logs,
        "moderation_logs": logs,
    }
    return render(request, "moderation/log.html", context)
