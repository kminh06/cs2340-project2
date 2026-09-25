from django.conf import settings
from django.db import models

from jobs.models import Job


class Conversation(models.Model):
    """US-14: an in-platform chat thread between a recruiter and a candidate,
    optionally tied to a specific job posting."""

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="conversations"
    )
    job = models.ForeignKey(
        Job, on_delete=models.SET_NULL, null=True, blank=True, related_name="conversations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        names = ", ".join(self.participants.values_list("username", flat=True))
        return f"Conversation({names})"


class Message(models.Model):
    """A single message within a Conversation (US-14)."""

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["sent_at"]

    def __str__(self):
        return f"{self.sender}: {self.body[:40]}"
