"""
Database Models
"""

import uuid
import os
from PIL import Image  # noqa

from django_cleanup import cleanup
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone
from django.core.exceptions import ValidationError


def recipe_image_file_path(instance, filename):
    """Generate file path for new post image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'post', filename)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, first_name, last_name, username, password=None, **extra_fields):
        """Create, save and return a new user."""

        if not first_name:
            raise ValueError("User must provide full name.")
        if not last_name:
            raise ValueError("User must provide a username.")
        if not email:
            raise ValueError("User must have an email address.")
        if not username:
            raise ValueError("User must have an email address.")

        user = self.model(email=self.normalize_email(email), first_name=first_name,
                          last_name=last_name, username=username.lower(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, username, password):
        """Create, save and return a new superuser."""
        user = self.create_user(email, first_name, last_name, username, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=128, verbose_name='password')
    username = models.CharField(max_length=50, unique=True, verbose_name='username')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    date_joined = models.DateTimeField(default=timezone.now, verbose_name='date joined')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['email', "first_name", "last_name"]
    USERNAME_FIELD = "username"

    objects = UserManager()

    def __str__(self):
        return self.username

    @property
    def fullname(self):
        return f"{self.first_name} {self.last_name}"


@cleanup.select
class Post(models.Model):
    """Post object."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=100)
    body = models.TextField(max_length=500)
    img = models.ImageField(null=True, upload_to=recipe_image_file_path)
    likes_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    hashtags = models.ManyToManyField('HashTag', blank=True)
    tags = models.ManyToManyField('Tag', blank=True)

    def __str__(self):
        return self.title

    @property
    def username(self):
        return self.user.username  # noqa

    def save(self, *args, **kwargs):
        """Save method"""

        super().save()

        if self.img:
            try:
                saved_img = Image.open(self.img.path)
            except FileNotFoundError:
                pass
            else:
                if saved_img.height > 300 or saved_img.width > 300:
                    new_img = (300, 300)
                    saved_img.thumbnail(new_img)
                    saved_img.save(self.img.path)


class HashTag(models.Model):
    """Hashtag model."""
    name = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """@Tags for Post."""
    somebody = models.CharField(max_length=30)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.somebody


class Follower(models.Model):
    """Followers model."""
    leader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name="followers")
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name="following")

    created_at = models.DateTimeField(default=timezone.now)


class Comment(models.Model):
    """Model for comments."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="comments")
    body = models.CharField(max_length=255)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return self.body


class Like(models.Model):
    """Model for likes."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey("Post", on_delete=models.CASCADE, blank=True, null=True,
                             related_name="likes")
    comment = models.ForeignKey("Comment", on_delete=models.CASCADE, blank=True, null=True,
                                related_name="likes")

    def clean(self):
        if not self.post and not self.comment:
            raise ValidationError('You must provide either comment_id or post_id.')
        if self.post and self.comment:
            raise ValidationError('You cannot provide comment_id and post_id.')
