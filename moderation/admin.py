from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "reporter", "target_user", "target_job", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("reporter__username", "target_user__username", "target_job__title", "reason")
    date_hierarchy = "created_at"
