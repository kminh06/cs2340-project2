from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from jobs.models import Job

from .models import Application


class ApplyUS3Tests(TestCase):
    """US-3: one-click apply with a tailored note."""

    def setUp(self):
        self.rec = User.objects.create_user("rec", password="pw", role=User.Role.RECRUITER)
        self.seeker = User.objects.create_user("seek", password="pw", role=User.Role.JOB_SEEKER)
        self.job = Job.objects.create(title="Dev", description="d", company="Co", posted_by=self.rec)
        self.url = reverse("applications:apply_to_job", args=[self.job.pk])

    def test_job_detail_has_apply_button_for_seeker(self):
        self.client.login(username="seek", password="pw")
        resp = self.client.get(reverse("jobs:job_detail", args=[self.job.pk]))
        self.assertContains(resp, self.url)

    def test_apply_page_shows_note_box(self):
        self.client.login(username="seek", password="pw")
        resp = self.client.get(self.url)
        self.assertContains(resp, 'name="tailored_note"')

    def test_apply_with_note_creates_application(self):
        self.client.login(username="seek", password="pw")
        resp = self.client.post(self.url, {"tailored_note": "I love Django."}, follow=True)
        self.assertRedirects(resp, reverse("applications:my_applications"))
        app = Application.objects.get()
        self.assertEqual((app.job, app.applicant, app.tailored_note),
                         (self.job, self.seeker, "I love Django."))
        self.assertEqual(app.status, Application.Status.APPLIED)
        self.assertContains(resp, "successfully submitted")

    def test_apply_without_note_is_allowed(self):
        self.client.login(username="seek", password="pw")
        self.client.post(self.url, {"tailored_note": ""})
        self.assertEqual(Application.objects.count(), 1)

    def test_duplicate_apply_is_blocked_with_message(self):
        self.client.login(username="seek", password="pw")
        self.client.post(self.url, {"tailored_note": "first"})
        resp = self.client.post(self.url, {"tailored_note": "second"}, follow=True)
        self.assertEqual(Application.objects.count(), 1)
        self.assertEqual(Application.objects.get().tailored_note, "first")
        self.assertContains(resp, "already applied")

    def test_recruiter_cannot_apply(self):
        self.client.login(username="rec", password="pw")
        self.assertEqual(self.client.post(self.url, {"tailored_note": "x"}).status_code, 403)
        self.assertEqual(Application.objects.count(), 0)

    def test_anonymous_redirected_to_login(self):
        resp = self.client.post(self.url, {"tailored_note": "x"})
        self.assertEqual(resp.status_code, 302)
        self.assertIn("login", resp.url)
        self.assertEqual(Application.objects.count(), 0)

    def test_cannot_apply_to_inactive_job_even_with_direct_link(self):
        self.job.is_active = False
        self.job.save()
        self.client.login(username="seek", password="pw")
        detail = reverse("jobs:job_detail", args=[self.job.pk])
        for resp in (self.client.get(self.url), self.client.post(self.url, {"tailored_note": "x"})):
            self.assertRedirects(resp, detail)
        self.assertEqual(Application.objects.count(), 0)
        page = self.client.get(detail)
        self.assertNotContains(page, self.url)
        self.assertContains(page, "no longer accepting applications")
