"""Business logic for the jobs app, kept out of views per project convention."""
from .models import Job


def search_jobs(cleaned_data):
    """US-2: filter active jobs by the fields in a validated ``JobSearchForm``.

    TODO(US-2): This currently only handles title/location text match, salary
    range overlap, work type, and visa sponsorship. Extend the skills filter
    to match against the Skill M2M (currently a naive icontains on skill
    name) and consider ranking/sorting by relevance.
    """
    qs = Job.objects.filter(is_active=True)

    title = cleaned_data.get("title")
    if title:
        qs = qs.filter(title__icontains=title)

    location = cleaned_data.get("location")
    if location:
        qs = qs.filter(office_address__icontains=location)

    skills = cleaned_data.get("skills")
    if skills:
        names = [s.strip() for s in skills.split(",") if s.strip()]
        for name in names:
            qs = qs.filter(skills__name__icontains=name)

    salary_min = cleaned_data.get("salary_min")
    if salary_min:
        qs = qs.filter(salary_max__gte=salary_min)

    salary_max = cleaned_data.get("salary_max")
    if salary_max:
        qs = qs.filter(salary_min__lte=salary_max)

    work_type = cleaned_data.get("work_type")
    if work_type:
        qs = qs.filter(work_type=work_type)

    if cleaned_data.get("visa_sponsorship"):
        qs = qs.filter(visa_sponsorship=True)

    return qs.distinct()
