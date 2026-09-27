from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Job


class JobFormPageTests(TestCase):
    """US-11 job form: no lat/long, Yes/No dropdowns, chip skills with a + button."""

    def setUp(self):
        self.user = User.objects.create_user("rec", password="pw", role=User.Role.RECRUITER)
        self.client.login(username="rec", password="pw")
        self.url = reverse("jobs:job_create")

    def _data(self, **overrides):
        data = {
            "title": "Backend Engineer",
            "description": "Build APIs.",
            "company": "Acme",
            "office_address": "",
            "salary_min": "",
            "salary_max": "",
            "work_type": Job.WorkType.REMOTE,
            "visa_sponsorship": "True",
            "is_active": "False",
            "skills": "Python, SQL",
        }
        data.update(overrides)
        return data

    def test_page_has_no_latlong_and_has_dropdowns_and_skill_button(self):
        html = self.client.get(self.url).content.decode()
        self.assertNotIn('name="latitude"', html)
        self.assertNotIn('name="longitude"', html)
        self.assertIn('<select name="visa_sponsorship"', html)
        self.assertIn('<select name="is_active"', html)
        self.assertIn('id="skill-add"', html)
        self.assertIn('type="hidden" name="skills"', html)

    def test_new_job_defaults(self):
        form = self.client.get(self.url).context["form"]
        self.assertEqual(form["is_active"].value(), "True")
        self.assertEqual(form["visa_sponsorship"].value(), "False")

    def test_create_saves_yes_no_and_skills(self):
        resp = self.client.post(self.url, self._data())
        job = Job.objects.get()
        self.assertRedirects(resp, reverse("jobs:job_detail", args=[job.pk]))
        self.assertTrue(job.visa_sponsorship)
        self.assertFalse(job.is_active)
        self.assertEqual(sorted(job.skills.values_list("name", flat=True)), ["Python", "SQL"])

    def test_edit_prefills_current_values(self):
        job = Job.objects.create(
            title="T", description="D", company="C", posted_by=self.user,
            visa_sponsorship=True, is_active=False,
        )
        form = self.client.get(reverse("jobs:job_edit", args=[job.pk])).context["form"]
        self.assertEqual(form["visa_sponsorship"].value(), "True")
        self.assertEqual(form["is_active"].value(), "False")
