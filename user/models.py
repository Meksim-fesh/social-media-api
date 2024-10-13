import os
import uuid

from django.db import models
from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.utils.translation import gettext as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.text import slugify

from social_media_api.settings import AUTH_USER_MODEL


def user_picture_file_path(instance, filename) -> os.path:
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.username)}-{uuid.uuid4()}{extension}"
    return os.path.join(f"uploads/users/{instance.id}/", filename)


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):

    username_validator = UnicodeUsernameValidator()

    picture = models.ImageField(
        blank=True,
        null=True,
        upload_to=user_picture_file_path
    )
    bio = models.TextField(blank=True)
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=False,
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
        default=f"user-{uuid.uuid1()}"
    )
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


class UserFollowing(models.Model):
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name="following",
        on_delete=models.CASCADE
    )
    following_user = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name="followers",
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return "{self.user} follows {self.following_user}"
