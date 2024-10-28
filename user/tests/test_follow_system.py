from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from rest_framework.test import APIClient
from rest_framework import status

from user import serializers
from user.models import UserFollowing


USER_PROFILE_FOLLOWERS_URL_STR = "user:followers-list"
USER_PROFILE_FOLLOWING_URL_STR = "user:following-list"
TOGGLE_FOLLOW_PAGE_URL_STR = "user:toggle-follow"

AUTHENTICATED_USER_FOLLOWERS_URL = reverse_lazy("user:my-followers")
AUTHENTICATED_USER_FOLLOWING_URL = reverse_lazy("user:my-followings")


def create_profiles() -> None:
    users_data = [
        {
            "email": "user_1@test.com",
            "password": "password",
        },
        {
            "email": "user_2@test.com",
            "password": "password",
        },
        {
            "email": "user_3@test.com",
            "password": "password",
        },
    ]

    for user_data in users_data:
        get_user_model().objects.create(**user_data)


def make_one_user_follow_everyone(user_id) -> None:
    user = get_user_model().objects.get(id=user_id)
    users = get_user_model().objects.all()

    for following_user in users:
        if following_user == user:
            continue

        UserFollowing.objects.create(
            user=user,
            following_user=following_user,
        )


def make_everyone_follow_one_user(user_id) -> None:
    followed_user = get_user_model().objects.get(id=user_id)
    users = get_user_model().objects.all()

    for user in users:
        if user == followed_user:
            continue

        UserFollowing.objects.create(
            user=user,
            following_user=followed_user,
        )


class AuthenticatedUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create(
            email="user@test.com",
            password="password",
        )
        self.client.force_authenticate(self.user)

    def test_toggle_follow_works(self):
        followed_user_id = 2
        create_profiles()

        response = self.client.post(
            reverse_lazy(
                TOGGLE_FOLLOW_PAGE_URL_STR,
                args=[followed_user_id],
            ),
        )

        user = self.user
        followed_user = get_user_model().objects.get(id=followed_user_id)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(user.following.count(), 1)
        self.assertEqual(followed_user.followers.count(), 1)
        self.assertEqual(UserFollowing.objects.count(), 1)

    def test_second_call_toggle_follow_make_unfollow(self):
        create_profiles()
        user = self.user
        followed_user_id = 2
        followed_user = get_user_model().objects.get(id=followed_user_id)

        UserFollowing.objects.create(
            user=user,
            following_user=followed_user,
        )

        response = self.client.post(
            reverse_lazy(
                TOGGLE_FOLLOW_PAGE_URL_STR,
                args=[followed_user_id],
            )
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(user.following.count(), 0)
        self.assertEqual(followed_user.followers.count(), 0)
        self.assertEqual(UserFollowing.objects.count(), 0)

    def test_list_user_followers(self):
        create_profiles()

        user = get_user_model().objects.last()
        make_everyone_follow_one_user(user.id)

        response = self.client.get(
            reverse_lazy(
                USER_PROFILE_FOLLOWERS_URL_STR,
                args=[user.id],
            )
        )

        followers = UserFollowing.objects.filter(
            following_user=user,
        )
        serializer = serializers.UserFollowersListSerializer(
            followers,
            many=True
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_list_user_followings(self):
        create_profiles()

        user = get_user_model().objects.last()
        make_one_user_follow_everyone(user.id)

        response = self.client.get(
            reverse_lazy(
                USER_PROFILE_FOLLOWING_URL_STR,
                args=[user.id],
            )
        )

        followings = UserFollowing.objects.filter(
            user=user,
        )
        serializer = serializers.UserFollowersListSerializer(
            followings,
            many=True
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_authenticated_user_followers_redirect(self):
        response = self.client.get(AUTHENTICATED_USER_FOLLOWERS_URL)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_authenticated_user_following_redirect(self):
        response = self.client.get(AUTHENTICATED_USER_FOLLOWING_URL)

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
