from django.contrib import admin

from .models import Education, Experience, JobSeekerProfile, Link, RecruiterProfile, Skill


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0


class LinkInline(admin.TabularInline):
    model = Link
    extra = 0


@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "headline", "location_text", "is_public_to_recruiters", "updated_at")
    list_filter = ("is_public_to_recruiters", "show_contact_info")
    search_fields = ("user__username", "headline", "location_text")
    filter_horizontal = ("skills",)
    inlines = [EducationInline, ExperienceInline, LinkInline]


@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name", "company_location", "updated_at")
    search_fields = ("user__username", "company_name")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
