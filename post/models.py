import os
import uuid

from django.db import models
from django.utils.text import slugify

from social_media_api.settings import AUTH_USER_MODEL


def post_file_path(instance, filename) -> os.path:
    name, extension = os.path.splitext(filename)
    name = f"{slugify(name)}-{slugify(instance.hashtag)}"
    filename = f"{name}-{uuid.uuid4()}{extension}"
    return os.path.join("uploads/posts/", filename)


class Post(models.Model):
    file = models.FileField(upload_to=post_file_path)
    text = models.TextField()
    hashtag = models.CharField(max_length=255)
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name="posts",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.user}"


class Like(models.Model):
    post = models.ForeignKey(
        Post,
        related_name="likes",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name="likes",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"Like to {self.post}"


class Comment(models.Model):
    content = models.TextField()
    post = models.ForeignKey(
        Post,
        related_name="comments",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name="comments",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"Comment to {self.post}"
