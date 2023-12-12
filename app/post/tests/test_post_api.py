"""
Tests for post APIs.
"""
import tempfile
import os

from PIL import Image  # noqa

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import User, Post, HashTag  # noqa
from post.serializers import PostSerializer  # noqa
from core.tests.test_admin import create_user  # noqa

POST_URL = reverse('post:post-list')

PAYLOAD = {
    'title': 'Sample post title',
    'body': 'Sample description',
}

PAYLOAD_HASHTAGS = {
    'title': 'Sample post title',
    'body': 'Sample description',
    "hashtags": [{"name": "#new"}, {"name": "#hello"}]
}

PAYLOAD_TAGS = {
    'title': 'Sample post title',
    'body': 'Sample description',
    "tags": [{"somebody": "@user"}, {"somebody": "@user2"}]
}


def detail_url(post_id):
    """Create and return a post detail URL."""
    return reverse('post:post-detail', args=[post_id])


def image_upload_url(post_id):
    """Create and return an image upload URL."""
    return reverse('post:post-upload-image', args=[post_id])


def create_post(user, **params):
    """Create and return a sample post."""
    PAYLOAD.update(params)
    post = Post.objects.create(user=user, **PAYLOAD)

    return post


class PublicPostAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(POST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePostApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_posts(self):
        """Test retrieving a list of posts."""
        create_post(user=self.user)
        create_post(user=self.user)

        res = self.client.get(POST_URL)

        posts = Post.objects.all().order_by('-id')
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_post_list_limited_to_user(self):
        """Test list of posts is limited to authenticated user."""
        other_user = create_user(email='other@example.com', username="user2")
        create_post(user=other_user)
        create_post(user=self.user)

        res = self.client.get(POST_URL)

        posts = Post.objects.filter(user=self.user)
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_post_detail(self):
        """Test get post detail."""
        post = create_post(user=self.user)

        url = detail_url(post.id)
        res = self.client.get(url)

        serializer = PostSerializer(post)
        self.assertEqual(res.data, serializer.data)

    def test_create_post(self):
        """Test creating a post."""
        res = self.client.post(POST_URL, PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(id=res.data['id'])
        for k, v in PAYLOAD.items():
            self.assertEqual(getattr(post, k), v)

        self.assertEqual(post.user, self.user)

    def test_partial_update(self):
        """Test partial update of a post."""
        post = create_post(user=self.user)

        update = {'title': 'New title'}
        url = detail_url(post.id)
        res = self.client.patch(url, update)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, update['title'])
        self.assertEqual(post.user, self.user)

    def test_full_update(self):
        """Test full update of post."""
        post = create_post(user=self.user)

        url = detail_url(post.id)
        res = self.client.put(url, PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        for k, v in PAYLOAD.items():
            self.assertEqual(getattr(post, k), v)
        self.assertEqual(post.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the post user results in an error."""
        new_user = create_user(email='user3@example.com', username="user3")
        post = create_post(user=self.user)

        update = {'user': new_user.id}
        url = detail_url(post.id)
        self.client.patch(url, update)

        post.refresh_from_db()
        self.assertEqual(post.user, self.user)

    def test_delete_post(self):
        """Test deleting a post successful."""
        post = create_post(user=self.user)

        url = detail_url(post.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=post.id).exists())

    def test_post_other_users_post_error(self):
        """Test trying to delete another users post gives error."""
        new_user = create_user(email='user2@example.com', username="username3")
        post = create_post(user=new_user)

        url = detail_url(post.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Post.objects.filter(id=post.id).exists())

    def test_create_post_with_new_hashtags(self):
        """Test creating a post with new hashtags."""

        res = self.client.post(POST_URL, PAYLOAD_HASHTAGS, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        posts = Post.objects.filter(user=self.user)
        self.assertEqual(posts.count(), 1)
        post = posts[0]
        self.assertEqual(post.hashtags.count(), 2)
        for hashtag in PAYLOAD_HASHTAGS['hashtags']:
            exists = post.hashtags.filter(
                name=hashtag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_post_with_existing_hashtags(self):
        """Test creating a post with existing tag."""
        hashtag_indian = HashTag.objects.create(user=self.user, name='#Indian')
        PAYLOAD_HASHTAGS["hashtags"] = [{'name': '#Indian'}, {'name': '#Breakfast'}]

        res = self.client.post(POST_URL, PAYLOAD_HASHTAGS, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        posts = Post.objects.filter(user=self.user)

        self.assertEqual(posts.count(), 1)
        post = posts[0]
        self.assertEqual(post.hashtags.count(), 2)
        self.assertIn(hashtag_indian, post.hashtags.all())
        for hashtag in PAYLOAD_HASHTAGS['hashtags']:
            exists = post.hashtags.filter(

                name=hashtag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_hashtag_on_update(self):
        """Test create hashtag when updating a post."""
        post = create_post(user=self.user)

        PAYLOAD_HASHTAGS["hashtags"] = [{'name': '#Lunch'}]
        url = detail_url(post.id)
        res = self.client.patch(url, PAYLOAD_HASHTAGS, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_hashtag = HashTag.objects.get(user=self.user, name='#Lunch')
        self.assertIn(new_hashtag, post.hashtags.all())

    def test_update_post_assign_hashtag(self):
        """Test assigning an existing tag when updating a post."""
        hashtag_breakfast = HashTag.objects.create(user=self.user, name='#Breakfast')
        post = create_post(user=self.user)
        post.hashtags.add(hashtag_breakfast)

        hashtag_lunch = HashTag.objects.create(user=self.user, name='#Lunch')
        PAYLOAD_HASHTAGS["hashtags"] = [{'name': '#Lunch'}]
        url = detail_url(post.id)
        res = self.client.patch(url, PAYLOAD_HASHTAGS, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(hashtag_lunch, post.hashtags.all())
        self.assertNotIn(hashtag_breakfast, post.hashtags.all())

    def test_clear_post_hashtags(self):
        """Test clearing a post hashtags."""
        hashtag = HashTag.objects.create(user=self.user, name='#Dessert')
        post = create_post(user=self.user)
        post.hashtags.add(hashtag)

        PAYLOAD_HASHTAGS["hashtags"] = []
        url = detail_url(post.id)
        res = self.client.patch(url, PAYLOAD_HASHTAGS, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(post.hashtags.count(), 0)

    def test_create_post_with_new_tags(self):
        """Test creating a post with new tags."""
        create_user(email='user2@example.com', username="user2")
        PAYLOAD_TAGS["tags"] = [{'somebody': '@username'}, {'somebody': '@user2'}]

        res = self.client.post(POST_URL, PAYLOAD_TAGS, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        posts = Post.objects.filter(user=self.user)
        self.assertEqual(posts.count(), 1)
        post = posts[0]
        self.assertEqual(post.tags.count(), 2)
        for tag in PAYLOAD_TAGS['tags']:
            exists = post.tags.filter(
                somebody=tag['somebody'][1:],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_only_tags_with_valid_username_are_saved(self):
        """Test that only tags with valid usernames are saved."""
        create_user(email='user2@example.com', username="user2")
        create_user(email='user3@example.com', username="user3")

        PAYLOAD_TAGS["tags"] = [{'somebody': '@username'}, {'somebody': '@user2'},
                                {'somebody': '@user3'}, {'somebody': '@user4'}]

        res = self.client.post(POST_URL, PAYLOAD_TAGS, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        posts = Post.objects.filter(user=self.user)
        self.assertEqual(posts.count(), 1)
        post = posts[0]
        self.assertEqual(post.tags.count(), 3)

    def test_tags_from_post_body_with_valid_username_saved(self):
        """Test that tags from post body with valid usernames are saved."""
        create_user(email='user2@example.com', username="user2")
        create_user(email='user3@example.com', username="user3")

        PAYLOAD_TAGS["tags"] = [{'somebody': '@username'}, {'somebody': '@user3'}]
        PAYLOAD_TAGS["body"] = "The body @user2"

        res = self.client.post(POST_URL, PAYLOAD_TAGS, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        posts = Post.objects.filter(user=self.user)
        self.assertEqual(posts.count(), 1)
        post = posts[0]
        self.assertEqual(post.tags.count(), 3)


class ImageUploadTests(TestCase):
    """Tests for the image upload API."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

        self.post = create_post(user=self.user)

    def tearDown(self):
        self.post.img.delete()

    def test_upload_image(self):
        """Test uploading an image to a post."""
        url = image_upload_url(self.post.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'img': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.post.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('img', res.data)
        self.assertTrue(os.path.exists(self.post.img.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image."""
        url = image_upload_url(self.post.id)
        payload = {'img': 'not an image'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
