"""
Database Models
"""

import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone


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


class Post(models.Model):
    """Post object."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField(max_length=2000)
    img = models.ImageField(null=True, upload_to=recipe_image_file_path)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    hashtags = models.ManyToManyField('HashTag')
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.title


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
