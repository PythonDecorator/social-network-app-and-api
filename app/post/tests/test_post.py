"""
Test for Index Page
"""
import tempfile
import os

from PIL import Image  # noqa

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from core.models import Post  # noqa
from core.tests.test_admin import create_user  # noqa

PAYLOAD = {
    'title': 'Sample post title',
    'body': 'Sample description',
}

INDEX_URL = reverse('post:index')
CREATE_POST_URL = reverse('post:create')


def update_url(pk):
    """Return User profile url."""
    return reverse('post:update', kwargs={'pk': pk})


def delete_url(pk):
    """Return User profile url."""
    return reverse('post:delete', kwargs={'pk': pk})


class PublicPostIndexTests(TestCase):
    """Test unauthenticated."""

    def setUp(self):
        self.client = Client()

    def test_auth_required(self):
        """Test auth is required for the index page."""
        res = self.client.get(INDEX_URL, follow=True)

        self.assertRedirects(res, "/login/?next=%2F")
        self.assertContains(res, "Login")


class PrivatePostIndexTests(TestCase):
    """Test authenticated Arequests."""

    def setUp(self):
        self.client = Client()
        self.user = create_user()
        self.client.force_login(self.user)

        self.other_user = create_user(email="other1@example.com", username="other_user1")
        create_user(email="other2@example.com", username="other_user2")
        create_user(email="other3@example.com", username="other_user3")

        # Create Post
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {
                'title': "post title @other_user1, @other_user3 @invalid, @user3",
                "body": "post body @other_user2 and @other_user3, @other_user3",
                'img': image_file
            }
            self.res = self.client.post(CREATE_POST_URL, payload, format='multipart')
        self.post = Post.objects.get(user=self.user)

    def tearDown(self) -> None:
        self.post.img.delete()

    def test_getting_post_index_page(self):
        """Test getting the index page is successful."""
        res = self.client.get(INDEX_URL)
        self.assertEqual(res.status_code, 200)

    def test_create_post(self):
        """Test creating a post is successful."""
        self.assertEqual(self.res.status_code, 302)
        self.assertEqual(self.post.user, self.user)
        self.assertTrue(os.path.exists(self.post.img.path))

    def test_update_post(self):
        """Test that updating a post is successful."""
        self.assertEqual(self.res.status_code, 302)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {
                'title': "New title",
                "body": "New body",
                'img': image_file
            }
            res = self.client.post(update_url(self.post.pk), payload, format='multipart')
        post = Post.objects.filter(user=self.user, pk=self.post.pk).first()
        self.assertEqual(res.status_code, 302)
        self.assertEqual(post.user, self.user)
        self.assertEqual(post.body, payload["body"])
        self.assertEqual(post.title, payload["title"])

    def test_creating_post_with_tags(self):
        """Test that saving tags from post title and body is successful."""
        self.assertEqual(self.res.status_code, 302)

        self.assertEqual(self.post.tags.count(), 3)
        for tag in [word[1:] for word in self.post.title.split(" ")
                    if word[0] == "@" and get_user_model().objects.filter(username=word[1:]).exists()]:
            exists = self.post.tags.filter(somebody=tag, user=self.user).exists()
            self.assertTrue(exists)

    def test_duplicated_post_tags_are_not_created(self):
        """Test that tags are saved only once even if the same user is tagged multiple times
        in the same post."""
        self.assertEqual(self.res.status_code, 302)
        self.assertEqual(self.post.tags.count(), 3)

    def test_tags_for_non_valid_users_are_not_created(self):
        """Test that tags for none valid usernames are not saved"""
        self.assertEqual(self.res.status_code, 302)

        self.assertEqual(self.post.tags.count(), 3)
        for tag in [word[1:] for word in self.post.title.split(" ")
                    if word[0] == "@" and get_user_model().objects.filter(username=word[1:]).exists()]:
            exists = self.post.tags.filter(somebody=tag, user=self.user).exists()
            self.assertTrue(exists)

    def test_delete_post_successful(self):
        """Test that deleting a post is successful."""
        self.assertEqual(self.res.status_code, 302)

        res = self.client.post(delete_url(self.post.pk))
        self.assertEqual(res.status_code, 302)
        post = Post.objects.filter(user=self.user, pk=self.post.pk).first()
        self.assertIsNone(post)

    def test_liking_a_post_successful(self):
        """Test that liking a post is successful."""
        initial_likes = self.post.likes_count

        like_post_url = reverse('post:like-post')
        res = self.client.post(like_post_url, {"post_id": self.post.id})

        self.assertEqual(res.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes.count(), initial_likes + 1)

        self.assertTrue(self.post.likes.filter(user=self.user, post=self.post))

    def test_disliking_a_post_successful(self):
        """Test that disliking a post is successful."""
        initial_likes = self.post.likes_count

        like_post_url = reverse('post:like-post')
        res = self.client.post(like_post_url, {"post_id": self.post.id})
        self.assertEqual(res.status_code, 200)
        self.post.refresh_from_db()

        self.assertEqual(self.post.likes.count(), initial_likes + 1)
        self.assertEqual(self.post.likes.count(), 1)

        res = self.client.post(like_post_url, {"post_id": self.post.id})
        self.assertEqual(res.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes.count(), 0)

    def test_commenting_on_post_successful(self):
        """Test that commenting on a post is successful."""
        initial_comments_count = self.post.comments.count()
        self.comment_on_post()
        self.assertEqual(self.post.comments.count(), initial_comments_count + 1)

        self.assertTrue(self.post.comments.filter(user=self.user, post=self.post))

    def test_updating_comment_on_post_success(self):
        """Test that updating a comment on a post is successful."""
        self.comment_on_post()

        post_comment_update_url = reverse('post:comment-post-update')

        comment = self.post.comments.filter(user=self.user, post=self.post).first()
        update_payload = {
            'body': 'Updated comment.',
            "comment_id": comment.id
        }
        res = self.client.post(post_comment_update_url, update_payload)
        self.assertEqual(res.status_code, 200)
        comment.refresh_from_db()

        self.assertEqual(self.post, comment.post)
        self.assertEqual(comment.body, update_payload['body'])
        self.assertEqual(res.json()['comment_body'], update_payload['body'], res)

    def comment_on_post(self):
        """Add a comment to a post"""
        post_comment_url = reverse('post:comment-post')
        payload = {
            'body': 'Sample comment on a post.',
            "post_id": self.post.id

        }
        res = self.client.post(post_comment_url, payload)
        self.assertEqual(res.status_code, 200)
        self.post.refresh_from_db()

    def test_deleting_comment_on_post_success(self):
        """Test that deleting a comment from a post is successful."""
        self.comment_on_post()

        post_comment_delete_url = reverse('post:comment-post-delete')

        comment = self.post.comments.filter(user=self.user, post=self.post).first()
        delete_payload = {
            "comment_id": comment.id
        }
        res = self.client.post(post_comment_delete_url, delete_payload)
        self.assertEqual(res.status_code, 200)

        self.assertFalse(self.post.comments.filter(user=self.user, post=self.post))
