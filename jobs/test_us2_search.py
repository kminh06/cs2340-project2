from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from profiles.models import Skill

from .models import Job


class JobSearchUS2Tests(TestCase):
    """US-2: search jobs by title, skills, location, salary, work type, visa."""

    @classmethod
    def setUpTestData(cls):
        rec = User.objects.create_user("rec", password="pw", role=User.Role.RECRUITER)
        py, sql, react = (Skill.objects.create(name=n) for n in ("Python", "SQL", "React"))

        def job(title, **kw):
            skills = kw.pop("skills", [])
            j = Job.objects.create(title=title, description="d", company="Co", posted_by=rec, **kw)
            j.skills.set(skills)
            return j

        cls.backend = job("Backend Engineer", office_address="Atlanta, GA", salary_min=90000,
                          salary_max=120000, work_type=Job.WorkType.REMOTE,
                          visa_sponsorship=True, skills=[py, sql])
        cls.frontend = job("Frontend Engineer", office_address="New York, NY", salary_min=60000,
                           salary_max=80000, work_type=Job.WorkType.ONSITE, skills=[react])
        cls.exact = job("Engineer", office_address="Atlanta, GA", work_type=Job.WorkType.HYBRID)
        cls.inactive = job("Backend Engineer Old", is_active=False, skills=[py])
        cls.open_ended = job("Staff Engineer", salary_min=150000)  # "$150,000+"

    def search(self, **params):
        resp = self.client.get(reverse("jobs:job_search"), params)
        self.assertEqual(resp.status_code, 200)
        return list(resp.context["jobs"])

    def test_title_filter(self):
        self.assertEqual(set(self.search(title="backend")), {self.backend})

    def test_title_relevance_puts_exact_match_first(self):
        self.assertEqual(self.search(title="Engineer")[0], self.exact)

    def test_skills_filter_single_and_multiple(self):
        self.assertEqual(self.search(skills="python"), [self.backend])
        self.assertEqual(self.search(skills="Python, SQL"), [self.backend])
        self.assertEqual(self.search(skills="Python, React"), [])

    def test_location_filter(self):
        self.assertEqual(set(self.search(location="atlanta")), {self.backend, self.exact})

    def test_salary_range_filter(self):
        self.assertEqual(self.search(salary_min=100000, salary_max=200000)[0:1], [self.backend])
        self.assertEqual(self.search(salary_max=70000), [self.frontend])

    def test_work_type_filter(self):
        self.assertEqual(self.search(work_type="REMOTE"), [self.backend])
        self.assertIn(self.frontend, self.search(work_type="ONSITE"))
        self.assertNotIn(self.backend, self.search(work_type="ONSITE"))

    def test_visa_filter(self):
        self.assertEqual(self.search(visa_sponsorship="on"), [self.backend])

    def test_combined_filters(self):
        self.assertEqual(
            self.search(title="engineer", skills="SQL", location="Atlanta",
                        work_type="REMOTE", visa_sponsorship="on"),
            [self.backend],
        )

    def test_inactive_jobs_hidden(self):
        self.assertNotIn(self.inactive, self.search(title="backend"))

    def test_no_match_message(self):
        resp = self.client.get(reverse("jobs:job_search"), {"title": "zzz"})
        self.assertContains(resp, "No jobs match")

    def test_pagination_keeps_filters(self):
        rec = User.objects.get(username="rec")
        for i in range(12):
            Job.objects.create(title=f"Remote role {i}", description="d", company="Co",
                               posted_by=rec, work_type=Job.WorkType.REMOTE)
        resp = self.client.get(reverse("jobs:job_search"), {"work_type": "REMOTE"})
        self.assertEqual(len(resp.context["jobs"]), 10)
        self.assertContains(resp, 'href="?work_type=REMOTE&page=2"')
        page2 = self.client.get(reverse("jobs:job_search"), {"work_type": "REMOTE", "page": 2})
        self.assertEqual(len(page2.context["jobs"]), 3)
