from django.conf import settings
from django.db import models

from jobs.models import Job


class Application(models.Model):
    """A job seeker's application to a Job. US-3/US-4/US-13."""

    class Status(models.TextChoices):
        APPLIED = "APPLIED", "Applied"
        REVIEW = "REVIEW", "Review"
        INTERVIEW = "INTERVIEW", "Interview"
        OFFER = "OFFER", "Offer"
        CLOSED = "CLOSED", "Closed"

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications"
    )
    tailored_note = models.TextField(
        blank=True, help_text="A short note the applicant tailors to this specific job."
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPLIED)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["job", "applicant"], name="unique_application_per_job_applicant"
            )
        ]

    def __str__(self):
        return f"{self.applicant} -> {self.job} ({self.get_status_display()})"
