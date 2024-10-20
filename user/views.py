from django.contrib.auth import get_user_model
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from rest_framework import generics, views
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response

from user import serializers
from user.models import UserFollowing


class CreateUserView(generics.CreateAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = (AllowAny,)


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.UserRetrieveMyselfSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    serializer_class = serializers.UserListSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def _filter_by_username(self, queryset):
        username = self.request.query_params.get("username")

        if username:
            queryset = queryset.filter(username__icontains=username)

        return queryset

    def _filter_by_names(self, queryset):
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")

        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)

        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)

        return queryset

    def filter_by_query_params(self, queryset):

        queryset = self._filter_by_username(queryset)
        queryset = self._filter_by_names(queryset)

        return queryset.distinct()

    def get_queryset(self):
        queryset = get_user_model().objects.all()

        queryset = self.filter_by_query_params(queryset)

        return queryset


class UserRetrieveView(generics.RetrieveAPIView):
    serializer_class = serializers.UserRetrieveSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    queryset = get_user_model().objects.annotate(
        i_follow=(
            Count("following")
        ),
        my_followers=(
            Count("followers")
        ),
    )


class ToggleUserFollowView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserFollowingSerializer

    def post(self, request, *args, **kwargs):
        user = self.request.user
        following_user = self.get_object()

        try:
            follow = UserFollowing.objects.get(
                user=user,
                following_user=following_user
            )
            follow.delete()
        except UserFollowing.DoesNotExist:
            UserFollowing.objects.create(
                user=user,
                following_user=following_user
            )

        return HttpResponseRedirect(
            reverse_lazy("user:user-detail", args=[following_user.id])
        )


class FollowPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class RetrieveUserFollowersView(generics.GenericAPIView):
    serializer_class = serializers.UserFollowersListSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    queryset = get_user_model().objects.prefetch_related("followers__user")
    pagination_class = FollowPagination

    def get(self, request, *args, **kwargs):
        queryset = self.get_object().followers.all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RetrieveUserFollowingsView(generics.GenericAPIView):
    serializer_class = serializers.UserFollowingListSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    queryset = get_user_model().objects.prefetch_related(
        "following__following_user"
    )
    pagination_class = FollowPagination

    def get(self, request, *args, **kwargs):
        queryset = self.get_object().following.all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RetrieveMyFollowers(views.APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(
            reverse_lazy(
                "user:followers-list",
                args=[self.request.user.id]
            )
        )


class RetrieveMyFollowing(views.APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(
            reverse_lazy(
                "user:following-list",
                args=[self.request.user.id]
            )
        )
