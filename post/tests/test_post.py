from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from rest_framework.test import APIClient
from rest_framework import status

from post import serializers
from post.models import Comment, Like, Post


POST_URL = reverse_lazy("post:post-list")
LIKED_POST_URL = reverse_lazy("post:post-liked")

RETRIEVE_POST_URL_STR = "post:post-detail"
ADD_COMMENT_URL_STR = "post:comment-create"
LIKE_POST_URL_STR = "post:like-toggle"
LIST_LIKE_TO_POST_URL_STR = "post:post-likes"


def sample_post(user, **kwargs):
    payload = {
        "text": "Test Post Text",
        "hashtag": "testing",
        "user": user,
    }
    payload.update(kwargs)

    return Post.objects.create(**payload)


def create_posts(user) -> None:
    posts_data = [
        {
            "file": "",
            "text": "Test Post 1",
            "hashtag": "Testing1",
            "user": user,
        },
        {
            "file": "",
            "text": "Test Post 2",
            "hashtag": "Testing2",
            "user": user,
        },
        {
            "file": "",
            "text": "Test Post 3",
            "hashtag": "Testing3",
            "user": user,
        },
    ]

    for post_data in posts_data:
        post = Post.objects.create(**post_data)
        post.publish()


def pop_likes_and_comments(response):
    if isinstance(response.data, list):
        for post in response.data:
            post.pop("amount_of_likes", None)
            post.pop("amount_of_comments", None)
    else:
        response.data.pop("amount_of_likes", None)
        response.data.pop("amount_of_comments", None)

    return response


class UnauthenticatedUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_authentication_required(self):
        response = self.client.get(POST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="password",
        )
        self.client.force_authenticate(self.user)

    def test_list_post(self):
        user = self.user
        create_posts(user)

        response = self.client.get(POST_URL)
        response = pop_likes_and_comments(response)

        posts = Post.objects.all()
        serializer = serializers.PostListSerializer(posts, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_list_post_filter_by_hashtag(self):
        hashtag_filter = "testing2"
        user = self.user
        create_posts(user)

        response = self.client.get(
            POST_URL,
            {
                "hashtag": hashtag_filter,
            }
        )
        response = pop_likes_and_comments(response)

        posts = Post.objects.filter(hashtag__icontains=hashtag_filter)
        serializer = serializers.PostListSerializer(posts, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_post(self):
        post_text = "Test Post"
        payload = {
            "text": post_text,
            "hashtag": "testing",
        }

        response = self.client.post(
            POST_URL,
            payload,
        )

        post = Post.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(post.text, post_text)

    def test_retrieve_post(self):
        user = self.user
        # text = "Test Post Text"
        # hashtag = "testing"

        post = sample_post(user)
        post.publish()
        serializer = serializers.PostRetrieveSerializer(post)

        response = self.client.get(
            reverse_lazy(
                RETRIEVE_POST_URL_STR,
                args=[post.id],
            )
        )
        response = pop_likes_and_comments(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_put_own_post(self):
        user = self.user
        old_text = "Test Post Text"
        old_hashtag = "testing"
        new_text = "New Test Post Text"
        new_hashtag = "newtesting"

        payload = {
            "file": "",
            "text": new_text,
            "hashtag": new_hashtag,
            "user": user,
        }

        post = sample_post(user=user, text=old_text, hashtag=old_hashtag)
        post.publish()

        response = self.client.put(
            reverse_lazy(
                RETRIEVE_POST_URL_STR,
                args=[post.id],
            ),
            payload
        )
        post.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(post.text, new_text)
        self.assertEqual(post.hashtag, new_hashtag)

    def test_patch_own_post(self):
        user = self.user
        old_text = "Test Post Text"
        old_hashtag = "testing"
        new_text = "New Test Post Text"
        new_hashtag = "newtesting"

        payload = {
            "text": new_text,
            "hashtag": new_hashtag,
        }

        post = sample_post(user=user, text=old_text, hashtag=old_hashtag)
        post.publish()

        response = self.client.patch(
            reverse_lazy(
                RETRIEVE_POST_URL_STR,
                args=[post.id],
            ),
            payload
        )
        post.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(post.text, new_text)
        self.assertEqual(post.hashtag, new_hashtag)

    def test_delete_own_post(self):
        user = self.user

        post = sample_post(user)
        post.publish()

        self.assertEqual(Post.objects.count(), 1)

        response = self.client.delete(
            reverse_lazy(
                RETRIEVE_POST_URL_STR,
                args=[post.id]
            )
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)

    def test_cant_modify_or_delete_not_own_post(self):
        second_user = get_user_model().objects.create_user(
            email="second_user@test.com",
            password="password",
        )
        text = "Post Belongs To Second User",
        hashtag = "seconduser",

        post = sample_post(user=second_user, text=text, hashtag=hashtag)
        post.publish()

        payload = {
            "text": "New test text"
        }

        response = self.client.patch(
            reverse_lazy(
                RETRIEVE_POST_URL_STR,
                args=[post.id],
            ),
            payload
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(
            reverse_lazy(
                RETRIEVE_POST_URL_STR,
                args=[post.id],
            )
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_comment_to_post(self):
        user = self.user
        comment_content = "Test Comment"

        post = sample_post(user)
        post.publish()

        payload = {
            "content": comment_content,
        }

        response = self.client.post(
            reverse_lazy(
                ADD_COMMENT_URL_STR,
                args=[post.id]
            ),
            payload
        )

        comment = Comment.objects.first()

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(comment.content, comment_content)

    def test_like_post(self):
        user = self.user

        post = sample_post(user)
        post.publish()

        response = self.client.post(
            reverse_lazy(
                LIKE_POST_URL_STR,
                args=[post.id],
            )
        )

        like = Like.objects.first()

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Like.objects.count(), 1)
        self.assertEqual(like.post, post)

    def test_unlike_post(self):
        user = self.user

        post = sample_post(user)
        post.publish()

        Like.objects.create(
            post=post,
            user=user,
        )

        self.assertEqual(Like.objects.count(), 1)

        response = self.client.post(
            reverse_lazy(
                LIKE_POST_URL_STR,
                args=[post.id],
            )
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Like.objects.count(), 0)

    def test_list_likes_to_post(self):
        user = self.user
        second_user = get_user_model().objects.create_user(
            email="second_user@test.com",
            password="password",
        )

        post = sample_post(user)

        Like.objects.create(
            post=post,
            user=user,
        )
        Like.objects.create(
            post=post,
            user=second_user,
        )

        response = self.client.get(
            reverse_lazy(
                LIST_LIKE_TO_POST_URL_STR,
                args=[post.id]
            )
        )

        likes = Like.objects.filter(post=post)
        serializer = serializers.LikeListSerializer(likes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(likes), 2)
        self.assertEqual(response.data, serializer.data)

    def test_list_liked_posts(self):
        user = self.user
        create_posts(user)

        posts = Post.objects.all()

        for post in posts:
            Like.objects.create(
                post=post,
                user=user,
            )

        response = self.client.get(LIKED_POST_URL)
        response = pop_likes_and_comments(response)

        serializer = serializers.PostListSerializer(posts, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
