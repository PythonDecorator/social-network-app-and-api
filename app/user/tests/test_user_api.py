"""
Tests for the user API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

PAYLOAD = {'first_name': "Test",
           'last_name': "Name",
           'email': 'test@example.com',
           'password': "testpass123",
           'username': 'username',
           }


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""
        res = self.client.post(CREATE_USER_URL, PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=PAYLOAD['email'])
        self.assertTrue(user.check_password(PAYLOAD['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exist_error(self):
        """Test error returned if user with email exists."""
        create_user(**PAYLOAD)
        res = self.client.post(CREATE_USER_URL, PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    #
    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""
        PAYLOAD["password"] = "ph"
        res = self.client.post(CREATE_USER_URL, PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=PAYLOAD['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        create_user(**PAYLOAD)
        res = self.client.post(TOKEN_URL, PAYLOAD)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_email_not_found(self):
        """Test error returned if user not found for given email."""
        res = self.client.post(TOKEN_URL, PAYLOAD)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""
        create_user(**PAYLOAD)
        PAYLOAD["email"] = "wrong"

        res = self.client.post(TOKEN_URL, PAYLOAD)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        PAYLOAD["email"] = 'test@example.com'

    def test_create_token_blank_password(self):
        """Test posting a blank password returns error"""
        PAYLOAD["password"] = ''
        res = self.client.post(TOKEN_URL, PAYLOAD)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        PAYLOAD["password"] = "testpass123"

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API request that require authentication."""

    def setUp(self):
        self.user = create_user(**PAYLOAD)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn("password", res.data)
        self.assertEqual(res.data, {'first_name': self.user.first_name,
                                    'last_name': self.user.last_name,
                                    'email': self.user.email,
                                    'username': self.user.username,
                                    })

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the ME endpoint."""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""
        PAYLOAD["first_name"] = "New"

        res = self.client.patch(ME_URL, PAYLOAD)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "New")
        self.assertEqual(self.user.username, PAYLOAD['username'])
        self.assertTrue(self.user.check_password(PAYLOAD['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
