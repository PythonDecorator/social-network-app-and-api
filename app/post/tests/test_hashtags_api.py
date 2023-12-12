"""
Tests for the hashtags API.
"""
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import HashTag, Post  # noqa
from post.serializers import HashTagSerializer  # noqa
from core.tests.test_admin import create_user  # noqa

HASHTAGS_URL = reverse('post:hashtag-list')


def detail_url(hashtag_id):
    """Create and return an HashTag detail URL."""
    return reverse('post:hashtag-detail', args=[hashtag_id])


class PublicHashtagsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving hashtags."""
        res = self.client.get(HASHTAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateHashTagsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_hashtags(self):
        """Test retrieving a list of hashtags."""
        HashTag.objects.create(user=self.user, name='#Kale')
        HashTag.objects.create(user=self.user, name='#Vanilla')

        res = self.client.get(HASHTAGS_URL)

        hashtags = HashTag.objects.all().order_by('-name')
        serializer = HashTagSerializer(hashtags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_hashtags_limited_to_user(self):
        """Test list of hashtags is limited to authenticated user."""
        user2 = create_user(email='user2@example.com', username="user2")
        HashTag.objects.create(user=user2, name='Salt')
        hashtag = HashTag.objects.create(user=self.user, name='#hello')

        res = self.client.get(HASHTAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], hashtag.name)
        self.assertEqual(res.data[0]['id'], hashtag.id)

    def test_update_hashtag(self):
        """Test updating a hashtag."""
        hashtag = HashTag.objects.create(user=self.user, name='#Cilantro')

        payload = {'name': '#Coriander'}
        url = detail_url(hashtag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        hashtag.refresh_from_db()
        self.assertEqual(hashtag.name, payload['name'])

    def test_delete_HashTag(self):
        """Test deleting an HashTag."""
        hashtag = HashTag.objects.create(user=self.user, name='#Lettuce')

        url = detail_url(hashtag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        hashtags = HashTag.objects.filter(user=self.user)
        self.assertFalse(hashtags.exists())

    def test_filter_hashtags_assigned_to_posts(self):
        """Test listing hashtags to those assigned to posts."""
        htag1 = HashTag.objects.create(user=self.user, name='#Apples')
        htag2 = HashTag.objects.create(user=self.user, name='#Turkey')
        post = Post.objects.create(
            title='Title 1',
            body="body",
            user=self.user,
        )
        post.hashtags.add(htag1)

        res = self.client.get(HASHTAGS_URL, {'assigned_only': 1})

        s1 = HashTagSerializer(htag1)
        s2 = HashTagSerializer(htag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_hashtags_unique(self):
        """Test filtered hashtags returns a unique list."""
        htag = HashTag.objects.create(user=self.user, name='#New')
        HashTag.objects.create(user=self.user, name='#GoFast')
        post1 = Post.objects.create(
            title='Test Post',
            body="Test Boby",
            user=self.user,
        )
        post2 = Post.objects.create(
            title='Test Post 2',
            body="Test Boby 2",
            user=self.user,
        )
        post1.hashtags.add(htag)
        post2.hashtags.add(htag)

        res = self.client.get(HASHTAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
