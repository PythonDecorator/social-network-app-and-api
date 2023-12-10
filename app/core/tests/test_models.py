"""
Test Models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models  # noqa


def create_user(email='user@example.com', password='testpass123', fullname="test test"):
    """Create a return a new user."""
    return get_user_model().objects.create_user(email, password, fullname)


def create_post(user, **params):
    """Create and return a sample post."""
    defaults = {
        'title': 'Sample post title',
        'body': 'Sample description',
    }
    defaults.update(params)

    post = models.Post.objects.create(user=user, **defaults)
    return post


class ModelTests(TestCase):
    """ Test models."""

    def test_create_user_with_email_successful(self):
        """ Test creating a user with an email is successful."""
        email = "test@example.com"
        password = "testpass123"
        fullname = "Test User",
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            fullname=fullname,
        )

        self.assertEqual(user.email, email)
        self.assertEqual(user.fullname, fullname)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "sample123", "test name")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Tests that creating a new user without an email
        raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123", "test name")

    def test_new_user_without_fullname_raises_value_error(self):
        """Tests that creating a new user without an username
        raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("test@example.com", "", "test123")

    def test_create_superuser(self):
        """ Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            "admin@example.com",
            "testpass123",
            "test name",
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_post(self):
        """Test creating a post is successful."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'Test Name',
            'testpass123',
        )
        post = models.Post.objects.create(
            user=user,
            title='Sample post title',
            body='Test post body.',
            img="app/core/static/Amos.png"
        )

        self.assertEqual(str(post), post.title)
