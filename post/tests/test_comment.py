from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from rest_framework import status
from rest_framework.test import APIClient

from post.serializers import CommentRetrieveUpdateDeleteSerializer
from post.models import Post, Comment


COMMENT_RETRIEVE_URL_STR = "post:comment-detail"


def sample_post(user, **kwargs):
    payload = {
        "text": "Test Post Text",
        "hashtag": "testing",
        "user": user,
    }
    payload.update(kwargs)

    return Post.objects.create(**payload)


def sample_comment(user, **kwargs):
    payload = {
        "content": "Test Comment",
        "user": user,
        "post": sample_post(user),
    }
    payload.update(**kwargs)

    return Comment.objects.create(**payload)


class AuthenticatedUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="password",
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_comment(self):
        user = self.user
        comment = sample_comment(user)
        serializer = CommentRetrieveUpdateDeleteSerializer(comment)

        response = self.client.get(
            reverse_lazy(
                COMMENT_RETRIEVE_URL_STR,
                args=[comment.id],
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_put_comment(self):
        user = self.user
        new_content = "New Comment Content"
        payload = {
            "content": new_content,
        }

        comment = sample_comment(user)

        response = self.client.put(
            reverse_lazy(
                COMMENT_RETRIEVE_URL_STR,
                args=[comment.id],
            ),
            payload
        )

        comment.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(comment.content, new_content)

    def test_patch_comment(self):
        user = self.user
        new_content = "New Comment Content"
        payload = {
            "content": new_content,
        }

        comment = sample_comment(user)

        response = self.client.patch(
            reverse_lazy(
                COMMENT_RETRIEVE_URL_STR,
                args=[comment.id],
            ),
            payload
        )

        comment.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(comment.content, new_content)

    def test_delete_comment(self):
        user = self.user
        comment = sample_comment(user)

        self.assertEqual(Comment.objects.count(), 1)

        response = self.client.delete(
            reverse_lazy(
                COMMENT_RETRIEVE_URL_STR,
                args=[comment.id],
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_cant_modify_or_delete_not_own_comment(self):
        second_user = get_user_model().objects.create_user(
            email="second_user@test.com",
            password="password",
        )
        comment = sample_comment(second_user)

        payload = {
            "content": "New Content",
        }

        response = self.client.patch(
            reverse_lazy(
                COMMENT_RETRIEVE_URL_STR,
                args=[comment.id],
            ),
            payload
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(
            reverse_lazy(
                COMMENT_RETRIEVE_URL_STR,
                args=[comment.id],
            )
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
