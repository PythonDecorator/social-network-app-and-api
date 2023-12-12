"""
Test Models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

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

    def setUp(self) -> None:
        self.user = create_user()
        self.post = create_post(user=self.user)

    def test_create_user_with_email_successful(self):
        """ Test creating a user with an email is successful."""

        self.assertEqual(self.user.email, EMAIL)
        self.assertEqual(self.user.first_name, FIRST_NAME)
        self.assertEqual(self.user.last_name, LAST_NAME)
        self.assertEqual(self.user.username, USERNAME)
        self.assertEqual(self.user.fullname, f"{FIRST_NAME} {LAST_NAME}")
        self.assertTrue(self.user.check_password(PASSWORD))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            [1, "test1@EXAMPLE.com", "test1@example.com"],
            [2, "Test2@Example.com", "Test2@example.com"],
            [3, "TEST3@EXAMPLE.COM", "TEST3@example.com"],
            [4, "test4@example.COM", "test4@example.com"],
        ]

        for n, email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, FIRST_NAME, LAST_NAME,
                                                        f"{USERNAME}{n}", PASSWORD)
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Tests that creating a new user without an email
        raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123", "test name", "test name", "username4")

    def test_new_user_without_first_name_raises_value_error(self):
        """Tests that creating a new user without fullname
        raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("test@example.com", "",  "test name",
                                                 "test123", "username5")

    def test_new_user_without_username_raises_value_error(self):
        """Tests that creating a new user without a username
        raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("test@example.com", "firstname", "last_name", "", "test123")

    def test_create_superuser(self):
        """ Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            "admin@example.com",
            FIRST_NAME,
            LAST_NAME,
            "admin",
            PASSWORD,
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_post(self):
        """Test creating a post is successful."""
        self.assertEqual(str(self.post), self.post.title)

    def test_create_hashtag(self):
        """Test creating a hashtag is successful."""
        hashtag = models.HashTag.objects.create(user=self.user, name='#tag')

        self.assertEqual(str(hashtag), hashtag.name)

    def test_create_tag(self):
        """Test creating a @tag is successful."""
        tag = models.Tag.objects.create(user=self.user, somebody='@amos12')

        self.assertEqual(str(tag), tag.somebody)
