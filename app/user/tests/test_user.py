"""
Test for User web app.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from core.tests.test_admin import create_user  # noqa
from user.forms import SignUpForm, LoginForm, EditProfileForm  # noqa

SIGNUP_URL = reverse('user:signup')
LOGIN_URL = reverse('user:login')

PAYLOAD = {
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "password1": "testpass123",
    "password2": "testpass123",
    "username": "username"
}


def profile_url(username, profile="profile"):
    """Return User profile url."""
    return reverse(f'user:{profile}', kwargs={'username': username})


class PublicIndexTests(TestCase):
    """Test unauthenticated."""

    def setUp(self):
        self.client = Client()

    def tearDown(self) -> None:
        PAYLOAD["password1"] = "testpass123"
        PAYLOAD["password2"] = "testpass123"
        PAYLOAD["email"] = "test@example.com"

    def test_user_signup(self):
        """Test that a user can register."""
        res = self.client.post(SIGNUP_URL, PAYLOAD, follow=True)

        self.assertEqual(res.status_code, 200)

        user = get_user_model().objects.get(email=PAYLOAD['email'])
        self.assertTrue(user.check_password(PAYLOAD['password1']))

        self.assertRedirects(res, reverse("user:login"))
        self.assertContains(res, "Login")

    def test_user_with_email_exist_error(self):
        """Test error returned if user with email exists."""
        create_user()
        res = self.client.post(SIGNUP_URL, PAYLOAD)

        with self.assertRaises(AssertionError):
            self.assertRedirects(res, reverse("user:login"))
        self.assertNotIn("Login", res)
        self.assertContains(res, "User with this Email already exists.")

    def test_user_with_username_exist_error(self):
        """Test error returned if user with username exists."""
        create_user()
        res = self.client.post(SIGNUP_URL, PAYLOAD)

        with self.assertRaises(AssertionError):
            self.assertRedirects(res, reverse("user:login"))
        self.assertNotIn("Login", res)
        self.assertContains(res, "User with this Username already exists.")

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""
        PAYLOAD["password1"] = "ph"
        PAYLOAD["password2"] = "ph"

        res = self.client.post(SIGNUP_URL, PAYLOAD)
        self.assertEqual(res.status_code, 200)

        with self.assertRaises(AssertionError):
            self.assertRedirects(res, reverse("user:login"))
        self.assertNotIn("Login", res)
        self.assertContains(res, "This password is too short.")

    def test_invalid_email_error(self):
        """Test an error is returned if user provide invalid email."""
        PAYLOAD["email"] = "invalid@"

        res = self.client.post(SIGNUP_URL, PAYLOAD)

        with self.assertRaises(AssertionError):
            self.assertRedirects(res, reverse("user:login"))
        self.assertNotIn("Login", res)

    def test_user_can_login(self):
        """Test that a user login is successful."""
        create_user()

        res1 = self.client.post(SIGNUP_URL, PAYLOAD, follow=True)
        self.assertEqual(res1.status_code, 200)

        payload = {
            "email": "test@example.com",
            "password": "testpass123",
        }

        res2 = self.client.post(LOGIN_URL, payload, follow=True)
        self.assertEqual(res2.status_code, 200)

        self.assertRedirects(res2, reverse("post:index"))

    def test_login_with_wrong_email_error(self):
        """Test that logging-in with ta wrong email returns error."""
        create_user()

        res1 = self.client.post(SIGNUP_URL, PAYLOAD, follow=True)
        self.assertEqual(res1.status_code, 200)

        payload = {
            "email": "wrong@example.com",
            "password": "testpass123",
        }

        res2 = self.client.post(LOGIN_URL, payload, follow=True)

        with self.assertRaises(AssertionError):
            self.assertRedirects(res2, reverse("post:index"))

        self.assertContains(res2, 'That email does not exist. Please signup instead.')

    def test_login_with_wrong_password_error(self):
        """Test that logging-in with ta wrong password returns error."""
        create_user()

        res1 = self.client.post(SIGNUP_URL, PAYLOAD, follow=True)
        self.assertEqual(res1.status_code, 200)

        payload = {
            "email": "test@example.com",
            "password": "wrong-pass123",
        }

        res2 = self.client.post(LOGIN_URL, payload, follow=True)

        with self.assertRaises(AssertionError):
            self.assertRedirects(res2, reverse("post:index"))

        self.assertContains(res2, 'Please check your password and try again.')


class PrivateUserTests(TestCase):
    """Test authenticated requests."""

    def setUp(self):
        self.client = Client()
        self.user = create_user()
        self.client.force_login(self.user)

    def tearDown(self) -> None:
        PAYLOAD["username"] = "username"
        PAYLOAD["last_name"] = "User"
        PAYLOAD["first_name"] = "Test"

    def test_user_profile(self):
        """Test getting user profile is successful."""
        res = self.client.get(profile_url(self.user.username))

        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.user.username)

    def test_authenticated_user_can_not_access_other_users_profile(self):
        """Test that authenticated users can not access other users profile page."""
        create_user(email="test2@example.com", username="new")

        res = self.client.get(profile_url("new"), follow=True)

        self.assertEqual(res.status_code, 404)
        self.assertNotIn(self.user.username, res)
        self.assertNotIn("new", res)

    def test_following_user(self):
        """Test that a user following another user is successful."""

        user2 = create_user(username="leader", email="user2@example.com")

        follow_url = reverse("user:follow")
        initial_following_count_user1 = self.user.following.count()
        initial_followers_count_user1 = user2.followers.count()

        payload = {
            "leader_id": user2.id
        }
        res = self.client.post(follow_url, payload)

        self.assertEqual(res.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.following.count(), initial_following_count_user1 + 1)
        self.assertEqual(user2.followers.count(), initial_followers_count_user1 + 1)

        self.assertTrue(self.user.following.filter(leader=user2))
        self.assertTrue(user2.followers.filter(follower=self.user))
