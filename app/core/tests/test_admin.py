"""
Tests for Django admin modifications.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

from core import models  # noqa


EMAIL = "test@example.com"
PASSWORD = "testpass123"
FIRST_NAME = "Test",
LAST_NAME = "User"
USERNAME = "username"


def create_user(email=EMAIL, first_name=FIRST_NAME, last_name=LAST_NAME,
                username=USERNAME, password=PASSWORD):
    """Create a return a new user."""
    return get_user_model().objects.create_user(email, first_name, last_name, username, password)


class AdminSiteTests(TestCase):
    """Tests for Django Admin."""

    def setUp(self):
        """Create user and client."""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            EMAIL, FIRST_NAME, LAST_NAME, USERNAME, PASSWORD)
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            email="user@example.com", first_name=FIRST_NAME,
            last_name=LAST_NAME, username="TestUser", password=PASSWORD
        )

    def test_users_lists(self):
        """Test that users are listed on page."""
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_edit_user_page(self):
        """Test that edit user page works."""
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that adding or creating a user works."""
        url = reverse("admin:core_user_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
