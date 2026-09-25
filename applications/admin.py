from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("job", "applicant", "status", "created_at", "updated_at")
    list_filter = ("status",)
    search_fields = ("job__title", "applicant__username")
    date_hierarchy = "created_at"
