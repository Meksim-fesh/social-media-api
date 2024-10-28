from django.test import TestCase
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from user import serializers


REGISTER_PAGE_URL = reverse_lazy("user:create")
PROFILES_PAGE_URL = reverse_lazy("user:user-list")
ME_PAGE_URL = reverse_lazy("user:manage")

RETRIEVE_PROFILE_PAGE_URL_STR = "user:user-detail"


def create_profiles() -> None:
    users_data = [
        {
            "email": "user_1@test.com",
            "username": "user_1",
            "first_name": "user_first",
            "last_name": "first_user",
            "password": "password",
        },
        {
            "email": "user_2@test.com",
            "username": "user_2",
            "first_name": "user_second",
            "last_name": "second_user",
            "password": "password",
        },
        {
            "email": "user_3@test.com",
            "username": "user_3",
            "first_name": "user_third",
            "last_name": "third_user",
            "password": "password",
        },
    ]

    for user_data in users_data:
        get_user_model().objects.create_user(**user_data)


class UnauthenticatedUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_authentication_required(self):
        response = self.client.get(PROFILES_PAGE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_user(self):
        response = self.client.post(
            REGISTER_PAGE_URL,
            data={
                "email": "user@test.com",
                "password": "password",
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AuthenticatedUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="password"
        )
        self.client.force_authenticate(user=self.user)

    def test_list_user_profiles_page(self):
        create_profiles()

        response = self.client.get(PROFILES_PAGE_URL)

        user_profiles = get_user_model().objects.all()
        serializer = serializers.UserListSerializer(user_profiles, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_user_profiles_by_username(self):
        filter_username = "user"
        create_profiles()

        response = self.client.get(
            PROFILES_PAGE_URL,
            {
                "username": filter_username,
            }
        )

        users = get_user_model().objects.filter(
            username__icontains=filter_username
        )
        serializer = serializers.UserListSerializer(users, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_user_profiles_by_first_name(self):
        filter_first_name = "er_"
        create_profiles()

        response = self.client.get(
            PROFILES_PAGE_URL,
            {
                "first_name": filter_first_name,
            }
        )

        users = get_user_model().objects.filter(
            first_name__icontains=filter_first_name
        )
        serializer = serializers.UserListSerializer(users, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_user_profiles_by_last_name(self):
        filter_last_name = "d_use"
        create_profiles()

        response = self.client.get(
            PROFILES_PAGE_URL,
            {
                "last_name": filter_last_name,
            }
        )

        users = get_user_model().objects.filter(
            last_name__icontains=filter_last_name
        )
        serializer = serializers.UserListSerializer(users, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_profile_page(self):
        user_id = 2
        create_profiles()

        response = self.client.get(
            reverse_lazy(
                RETRIEVE_PROFILE_PAGE_URL_STR,
                args=[user_id]
            )
        )

        response.data.pop("i_follow")
        response.data.pop("my_followers")

        user = get_user_model().objects.get(id=user_id)
        serializer = serializers.UserRetrieveSerializer(user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_own_profile_page(self):
        response = self.client.get(ME_PAGE_URL)

        user = self.user
        serializer = serializers.UserRetrieveMyselfSerializer(user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_put_own_profile_page(self):
        username = "new_username"
        first_name = "test_first"
        last_name = "test_last"

        response = self.client.put(
            ME_PAGE_URL,
            data={
                "picture": "",
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "bio": "",
                "email": "user@test.com",
            }
        )

        user = self.user

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.username, username)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)

    def test_patch_own_profile_page(self):
        username = "new_test_username"
        first_name = "new_test_first_name"
        last_name = "new_test_last_name"

        response = self.client.patch(
            ME_PAGE_URL,
            data={
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
            }
        )

        user = self.user

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.username, username)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
