from rest_framework import generics
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from post.models import Like, Post
from post.serializers import (
    LikeListSerializer,
    PostListSerializer,
    PostRetrieveSerializer,
    PostSerializer,
    ToggleLikeSerializer
)


class PostViewSet(ModelViewSet):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated,)
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

    def get_serializer_class(self):

        if self.action == "list":
            return PostListSerializer

        if self.action == "retrieve":
            return PostRetrieveSerializer

        return PostSerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
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

        if self.action == "retrieve":
            queryset = self.queryset.prefetch_related("comments__user")
            queryset = queryset.annotate(
                amount_of_likes=(
                    Count("likes")
                ),
            )
            return queryset

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LikeListView(generics.ListAPIView):
    serializer_class = LikeListSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Like.objects.select_related("user")


class ToggleLikeView(generics.GenericAPIView):
    serializer_class = ToggleLikeSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Post.objects.all()

    def post(self, request, *args, **kwargs):

        user = self.request.user
        post = self.get_object()

        try:
            like = Like.objects.get(
                post=post,
                user=user,
            )
            like.delete()
        except Like.DoesNotExist:
            Like.objects.create(
                user=user,
                post=post,
            )

        return HttpResponseRedirect(
            reverse_lazy("post:post-detail", args=[post.id])
        )
