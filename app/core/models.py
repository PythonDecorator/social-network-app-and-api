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

    def create_user(self, email, fullname, password=None, **extra_fields):
        """Create, save and return a new user."""

        if not email:
            raise ValueError("User must have an email address.")
        if not fullname:
            raise ValueError("User must provide full name.")

        user = self.model(email=self.normalize_email(email), fullname=fullname,
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, fullname):
        """Create, save and return a new superuser."""
        user = self.create_user(email, password, fullname)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=128, verbose_name='password')
    fullname = models.CharField(max_length=255)

    date_joined = models.DateTimeField(default=timezone.now, verbose_name='date joined')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"


class Post(models.Model):
    """Post object."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField(max_length=2000)
    img = models.ImageField(null=True, upload_to=recipe_image_file_path)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
