from django.conf import settings
from django.db import models


class SavedSearch(models.Model):
    """US-16: a recruiter's saved candidate-search filters, used to notify
    them of new matches."""

    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_searches"
    )
    name = models.CharField(max_length=150)
    filters = models.JSONField(
        default=dict, help_text="Stored filter params, e.g. {'skills': ['Python'], 'location': 'Atlanta'}"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.recruiter})"


class Notification(models.Model):
    """A notification for a user, e.g. new candidate matches for a
    SavedSearch (US-16)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    saved_search = models.ForeignKey(
        SavedSearch, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications"
    )
    message = models.CharField(max_length=255)
    link_url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification for {self.user}: {self.message[:40]}"
