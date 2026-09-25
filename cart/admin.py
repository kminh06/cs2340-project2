from django.contrib import admin

from .models import SavedJob


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ("seeker", "job", "added_at")
    search_fields = ("seeker__username", "job__title")
    list_filter = ("added_at",)
