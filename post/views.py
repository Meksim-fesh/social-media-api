from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone

from post.models import Comment, Like, Post
from post.serializers import (
    CommentCreateSerializer,
    CommentRetrieveUpdateDeleteSerializer,
    LikeListSerializer,
    PostListSerializer,
    PostRetrieveSerializer,
    PostSerializer,
    ToggleLikeSerializer
)
from post.permissions import IsOwnerOrReadOnly

from post.tasks import create_scheduled_post


class PostViewSet(ModelViewSet):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsOwnerOrReadOnly, )
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
        queryset = queryset.filter(is_published=True)

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
                    Count("comments", distinct=True)
                ),
                amount_of_likes=(
                    Count("likes", distinct=True)
                ),
            )
            return queryset

        if self.action == "retrieve":
            queryset = self.queryset.prefetch_related("comments__user")
            queryset = queryset.annotate(
                amount_of_likes=(
                    Count("likes", distinct=True)
                ),
            )
            return queryset

        return queryset

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        scheduled_time = serializer.validated_data.pop("scheduled_time", None)

        post = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        if scheduled_time and scheduled_time > timezone.now():
            create_scheduled_post.apply_async(
                args=[post.id],
                eta=scheduled_time,
            )
            return Response(status=status.HTTP_200_OK)

        else:
            post.publish()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class LikedPostView(generics.ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )
    queryset = Post.objects.select_related("user")

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user

        queryset = queryset.annotate(
            amount_of_comments=(
                Count("comments", distinct=True)
            ),
            amount_of_likes=(
                Count("likes", distinct=True)
            ),
        )
        queryset = queryset.filter(likes__user=user)

        return queryset


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


class CommentCreateView(generics.GenericAPIView):
    serializer_class = CommentCreateSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsOwnerOrReadOnly, )
    queryset = Post.objects.all()

    def post(self, request, *args, **kwargs):

        post = self.get_object()
        user = self.request.user

        serializer = CommentCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "user": user,
                "post": post,
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return HttpResponseRedirect(
            reverse_lazy("post:post-detail", args=[post.id])
        )


class CommentViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    serializer_class = CommentRetrieveUpdateDeleteSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsOwnerOrReadOnly, )
    queryset = Comment.objects.all()
