from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Education, Experience, JobSeekerProfile, Link


class SeekerProfileEditTests(TestCase):
    """US-1 profile page: chip skills, one education box, + rows for experience/links."""

    def setUp(self):
        self.user = User.objects.create_user("seeker", password="pw", role=User.Role.JOB_SEEKER)
        self.client.login(username="seeker", password="pw")
        self.url = reverse("profiles:seeker_profile_edit")

    def _post(self, **overrides):
        data = {
            "headline": "Dev",
            "summary": "",
            "location_text": "Atlanta, GA",
            "skills": "Python, SQL",
            "edu-TOTAL_FORMS": "1", "edu-INITIAL_FORMS": "0",
            "edu-MIN_NUM_FORMS": "0", "edu-MAX_NUM_FORMS": "1",
            "edu-0-school": "Georgia Tech",
            "exp-TOTAL_FORMS": "2", "exp-INITIAL_FORMS": "0",
            "exp-MIN_NUM_FORMS": "0", "exp-MAX_NUM_FORMS": "1000",
            "exp-0-company": "A", "exp-0-title": "Intern",
            "exp-1-company": "B", "exp-1-title": "Engineer",
            "link-TOTAL_FORMS": "1", "link-INITIAL_FORMS": "0",
            "link-MIN_NUM_FORMS": "0", "link-MAX_NUM_FORMS": "1000",
            "link-0-label": "GitHub", "link-0-url": "https://github.com/x",
        }
        data.update(overrides)
        return self.client.post(self.url, data)

    def test_page_has_no_privacy_or_latlong_fields(self):
        html = self.client.get(self.url).content.decode()
        for name in ("latitude", "longitude", "is_public_to_recruiters", "show_location"):
            self.assertNotIn(f'name="{name}"', html)
        self.assertIn('id="skill-add"', html)
        self.assertIn('id="exp-template"', html)

    def test_save_skills_education_and_multiple_experiences(self):
        resp = self._post()
        self.assertEqual(resp.status_code, 302)
        profile = JobSeekerProfile.objects.get(user=self.user)
        self.assertEqual(sorted(profile.skills.values_list("name", flat=True)), ["Python", "SQL"])
        self.assertEqual(Education.objects.filter(profile=profile).count(), 1)
        self.assertEqual(Experience.objects.filter(profile=profile).count(), 2)
        self.assertEqual(Link.objects.filter(profile=profile).count(), 1)

    def test_gap_from_removed_new_row_is_ignored(self):
        # User added three rows then clicked X on the middle one (index 1 missing).
        resp = self._post(**{
            "exp-TOTAL_FORMS": "3",
            "exp-1-company": "", "exp-1-title": "",
            "exp-2-company": "C", "exp-2-title": "Lead",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Experience.objects.count(), 2)

    def test_only_one_education_allowed(self):
        resp = self._post(**{"edu-TOTAL_FORMS": "2", "edu-1-school": "Other"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Education.objects.count(), 0)

    def test_education_box_not_duplicated_after_save(self):
        self._post()
        html = self.client.get(self.url).content.decode()
        self.assertIn('name="edu-0-school"', html)
        self.assertNotIn('name="edu-1-school"', html)
