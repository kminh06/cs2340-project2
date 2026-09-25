from django.conf import settings
from django.db import models

from jobs.models import Job


class Report(models.Model):
    """US-24: a report filed against a user OR a job posting, for an admin
    to review before taking action (US-22)."""

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
        RESOLVED = "RESOLVED", "Resolved"
        DISMISSED = "DISMISSED", "Dismissed"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="filed_reports",
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reports_against",
    )
    target_job = models.ForeignKey(
        Job, on_delete=models.CASCADE, null=True, blank=True, related_name="reports_against"
    )
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(target_user__isnull=False, target_job__isnull=True)
                    | models.Q(target_user__isnull=True, target_job__isnull=False)
                ),
                name="report_has_exactly_one_target",
            )
        ]

    def __str__(self):
        target = self.target_user or self.target_job
        return f"Report by {self.reporter} on {target} [{self.get_status_display()}]"
