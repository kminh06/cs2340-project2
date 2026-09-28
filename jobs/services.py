"""Business logic for the jobs app, kept out of views per project convention."""
from django.db.models import Case, IntegerField, Q, Value, When
from .models import Job


def search_jobs(cleaned_data):
    """US-2: filter active jobs by the fields in a validated ``JobSearchForm``."""
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
            qs = qs.filter(skills__name__iexact=name)

    # A job's pay range matches when it overlaps the searched range. A job
    # with only a minimum ("$150,000+") has no upper limit, so it matches any
    # "at least" search. A job with only a maximum has no lower limit.
    # Jobs with no salary at all are left out once a salary filter is used.
    salary_min = cleaned_data.get("salary_min")
    if salary_min:
        qs = qs.filter(
            Q(salary_max__gte=salary_min)
            | Q(salary_max__isnull=True, salary_min__isnull=False)
        )

    salary_max = cleaned_data.get("salary_max")
    if salary_max:
        qs = qs.filter(
            Q(salary_min__lte=salary_max)
            | Q(salary_min__isnull=True, salary_max__isnull=False)
        )

    work_type = cleaned_data.get("work_type")
    if work_type:
        qs = qs.filter(work_type=work_type)

    if cleaned_data.get("visa_sponsorship"):
        qs = qs.filter(visa_sponsorship=True)

    if title:
        qs=qs.annotate(
            relevance=Case(
                When(title__iexact=title, then=Value(2)),
                When(title__icontains=title, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
            ).order_by("-relevance","-created_at")
    else:
        qs=qs.order_by("-created_at")     
    return qs.distinct()
