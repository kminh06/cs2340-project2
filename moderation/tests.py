from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from jobs.models import Job

from .models import Report


class JobModerationUS22Tests(TestCase):
    """US-22: Administrators moderate or remove job posts."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user("admin", password="pw", role=User.Role.ADMIN)
        cls.rec = User.objects.create_user("rec", password="pw", role=User.Role.RECRUITER)
        cls.seeker = User.objects.create_user("seeker", password="pw", role=User.Role.JOB_SEEKER)

        def job(title, **kw):
            return Job.objects.create(title=title, description="d", company="Acme", posted_by=cls.rec, **kw)

        cls.good = job("Backend Engineer")
        cls.spam = job("Make $$$ fast")
        cls.old = job("Old Posting", is_active=False)
        Report.objects.create(reporter=cls.seeker, target_job=cls.spam, reason="spam")
        Report.objects.create(reporter=cls.seeker, target_job=cls.good, reason="meh",
                              status=Report.Status.DISMISSED)

    def setUp(self):
        self.client.login(username="admin", password="pw")

    def listing(self, **params):
        resp = self.client.get(reverse("moderation:job_moderation_list"), params)
        self.assertEqual(resp.status_code, 200)
        return set(resp.context["jobs"])

    def act(self, action, job, **data):
        return self.client.post(reverse(f"moderation:job_{action}", args=[job.id]), data)

    def test_non_admins_are_forbidden(self):
        self.client.login(username="rec", password="pw")
        self.assertEqual(self.client.get(reverse("moderation:job_moderation_list")).status_code, 403)
        self.assertEqual(self.act("deactivate", self.spam).status_code, 403)
        self.assertEqual(self.act("delete", self.spam).status_code, 403)
        self.spam.refresh_from_db()
        self.assertTrue(self.spam.is_active)

    def test_lists_active_and_inactive_jobs(self):
        self.assertEqual(self.listing(), {self.good, self.spam, self.old})

    def test_filters(self):
        self.assertEqual(self.listing(q="backend"), {self.good})
        self.assertEqual(self.listing(q="ACME"), {self.good, self.spam, self.old})
        self.assertEqual(self.listing(q="rec"), {self.good, self.spam, self.old})
        self.assertEqual(self.listing(status="inactive"), {self.old})
        self.assertEqual(self.listing(status="active"), {self.good, self.spam})

    def test_open_reports_counted_and_filterable(self):
        # Dismissed reports don't count as open.
        self.assertEqual(self.listing(reported="1"), {self.spam})
        counts = {j.pk: j.open_reports for j in self.listing()}
        self.assertEqual(counts[self.spam.pk], 1)
        self.assertEqual(counts[self.good.pk], 0)

    def test_deactivate_hides_job_from_search(self):
        self.act("deactivate", self.spam)
        self.spam.refresh_from_db()
        self.assertFalse(self.spam.is_active)
        resp = self.client.get(reverse("jobs:job_search"))
        self.assertNotIn(self.spam, list(resp.context["jobs"]))

    def test_reactivate(self):
        self.act("reactivate", self.old)
        self.old.refresh_from_db()
        self.assertTrue(self.old.is_active)

    def test_delete_removes_job(self):
        self.act("delete", self.spam)
        self.assertFalse(Job.objects.filter(pk=self.spam.pk).exists())

    def test_get_not_allowed(self):
        for action in ("deactivate", "reactivate", "delete"):
            resp = self.client.get(reverse(f"moderation:job_{action}", args=[self.spam.id]))
            self.assertEqual(resp.status_code, 405)
        self.assertTrue(Job.objects.filter(pk=self.spam.pk, is_active=True).exists())

    def test_redirects_to_next_but_ignores_external(self):
        back = reverse("moderation:job_moderation_list") + "?status=active"
        self.assertRedirects(self.act("deactivate", self.spam, next=back), back)
        resp = self.act("reactivate", self.spam, next="https://evil.com/")
        self.assertRedirects(resp, reverse("moderation:job_moderation_list"))

    def test_missing_job_404(self):
        self.assertEqual(self.client.post(reverse("moderation:job_delete", args=[9999])).status_code, 404)
