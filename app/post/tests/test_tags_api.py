"""
Tests for the tags API.
"""
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Post  # noqa
from post.serializers import TagSerializer  # noqa
from core.tests.test_admin import create_user  # noqa

TAGS_URL = reverse('post:tag-list')

PAYLOAD = {
    'title': 'Sample post title',
    'body': 'Sample description',
}


def create_post(user, **params):
    """Create and return a sample post."""
    PAYLOAD.update(params)
    post = Post.objects.create(user=user, **PAYLOAD)

    return post


def detail_url(tag_id):
    """Create and return a tag detail url."""
    return reverse('post:tag-detail', args=[tag_id])


class PublicTagsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.other_user = create_user(email="other@example.com", username="other")

    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""
        Tag.objects.create(user=self.user, somebody="@other")
        Tag.objects.create(user=self.user, somebody='@other')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-somebody')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        Tag.objects.create(user=self.other_user, somebody='@other')
        tag = Tag.objects.create(user=self.user, somebody='@other')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['somebody'], tag.somebody)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user, somebody='@username')

        payload = {'somebody': '@other'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.somebody, payload['somebody'])

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = Tag.objects.create(user=self.user, somebody='@other')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_posts(self):
        """Test listing tags to those assigned to posts."""
        tag1 = Tag.objects.create(user=self.user, somebody='@other')
        tag2 = Tag.objects.create(user=self.user, somebody='@other')

        post = create_post(user=self.user)
        post.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags returns a unique list."""
        tag = Tag.objects.create(user=self.user, somebody='@other')
        Tag.objects.create(user=self.user, somebody='@other')

        post1 = create_post(user=self.user)
        post2 = Post.objects.create(user=self.user)
        post1.tags.add(tag)
        post2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
