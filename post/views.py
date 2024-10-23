from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.db.models import Count, Q

from post.models import Like, Post
from post.serializers import (
    LikeListSerializer,
    PostListSerializer,
    PostRetrieveSerializer
)


class PostListView(generics.ListAPIView):
    serializer_class = PostListSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Post.objects.select_related("user")

    def _filter_queryset_by_hashtag(self, queryset):
        hashtag = self.request.query_params.get("hashtag")

        if hashtag:
            queryset = queryset.filter(hashtag__icontains=hashtag)

        return queryset

    def _filter_queryset_by_user(self, queryset):
        user = self.request.user
        user_followings_objects = user.following.all().values("following_user")

        queryset = queryset.filter(
            Q(user__in=user_followings_objects) | Q(user=user)
        )

        return queryset

    def filter_queryset_by_params(self, queryset):
        queryset = self._filter_queryset_by_user(queryset)
        queryset = self._filter_queryset_by_hashtag(queryset)

        return queryset.distinct()

    def get_queryset(self):
        queryset = self.queryset

        queryset = self.filter_queryset_by_params(queryset)

        queryset = queryset.annotate(
            amount_of_comments=(
                Count("comments")
            ),
            amount_of_likes=(
                Count("likes")
            ),
        )

        return queryset


class PostRetrieveView(generics.RetrieveAPIView):
    serializer_class = PostRetrieveSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Post.objects.select_related("user").prefetch_related(
        "comments__user"
    )

    def get_queryset(self):
        queryset = self.queryset

        queryset = queryset.annotate(
            amount_of_likes=(
                Count("likes")
            ),
        )

        return queryset


class LikeListView(generics.ListAPIView):
    serializer_class = LikeListSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Like.objects.select_related("user")
