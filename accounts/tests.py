from django.test import TestCase
from django.urls import reverse

from .models import User


class ManageUsersUS21Tests(TestCase):
    """US-21: Administrators manage users and roles."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user("admin", email="a@x.com", password="pw", role=User.Role.ADMIN)
        cls.seeker = User.objects.create_user("seeker", email="s@x.com", password="pw", role=User.Role.JOB_SEEKER)
        cls.rec = User.objects.create_user("rec", email="r@x.com", password="pw", role=User.Role.RECRUITER)
        cls.gone = User.objects.create_user("gone", email="g@x.com", password="pw", is_active=False)

    def setUp(self):
        self.client.login(username="admin", password="pw")

    def listing(self, **params):
        resp = self.client.get(reverse("accounts:manage_users"), params)
        self.assertEqual(resp.status_code, 200)
        return set(resp.context["users"])

    def update(self, user, **data):
        return self.client.post(reverse("accounts:update_user", args=[user.id]), data)

    def test_non_admins_are_forbidden(self):
        self.client.login(username="rec", password="pw")
        self.assertEqual(self.client.get(reverse("accounts:manage_users")).status_code, 403)
        self.assertEqual(self.update(self.seeker, role=User.Role.ADMIN, is_active="on").status_code, 403)
        self.seeker.refresh_from_db()
        self.assertEqual(self.seeker.role, User.Role.JOB_SEEKER)

    def test_filters(self):
        self.assertEqual(self.listing(q="S@X"), {self.seeker})
        self.assertEqual(self.listing(role=User.Role.RECRUITER), {self.rec})
        self.assertEqual(self.listing(status="inactive"), {self.gone})
        self.assertNotIn(self.gone, self.listing(status="active"))

    def test_change_role(self):
        self.update(self.seeker, role=User.Role.RECRUITER, is_active="on")
        self.seeker.refresh_from_db()
        self.assertEqual(self.seeker.role, User.Role.RECRUITER)
        self.assertTrue(self.seeker.is_active)

    def test_deactivate_and_reactivate(self):
        self.update(self.rec, role=User.Role.RECRUITER)  # unchecked box omits is_active
        self.rec.refresh_from_db()
        self.assertFalse(self.rec.is_active)
        self.update(self.rec, role=User.Role.RECRUITER, is_active="on")
        self.rec.refresh_from_db()
        self.assertTrue(self.rec.is_active)

    def test_deactivated_user_cannot_log_in(self):
        self.update(self.rec, role=User.Role.RECRUITER)
        self.client.logout()
        self.assertFalse(self.client.login(username="rec", password="pw"))

    def test_admin_cannot_change_self(self):
        self.update(self.admin, role=User.Role.JOB_SEEKER)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.role, User.Role.ADMIN)
        self.assertTrue(self.admin.is_active)

    def test_invalid_role_rejected(self):
        self.update(self.seeker, role="SUPERUSER", is_active="on")
        self.seeker.refresh_from_db()
        self.assertEqual(self.seeker.role, User.Role.JOB_SEEKER)

    def test_get_not_allowed_and_external_next_ignored(self):
        self.assertEqual(self.client.get(reverse("accounts:update_user", args=[self.seeker.id])).status_code, 405)
        resp = self.update(self.seeker, role=User.Role.JOB_SEEKER, is_active="on", next="https://evil.com/")
        self.assertRedirects(resp, reverse("accounts:manage_users"))
