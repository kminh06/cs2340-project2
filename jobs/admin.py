from django.contrib import admin

from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company",
        "work_type",
        "visa_sponsorship",
        "is_active",
        "posted_by",
        "created_at",
    )
    list_filter = ("work_type", "visa_sponsorship", "is_active")
    search_fields = ("title", "company", "office_address", "description")
    filter_horizontal = ("skills",)
    date_hierarchy = "created_at"
