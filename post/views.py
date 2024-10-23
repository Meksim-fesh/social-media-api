from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.db.models import Count, Q

from post.models import Post
from post.serializers import PostListSerializer, PostRetrieveSerializer


class PostListView(generics.ListAPIView):
    serializer_class = PostListSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Post.objects.all()

    def get_queryset(self):
        queryset = self.queryset

        user = self.request.user
        user_followings_objects = user.following.all().values("following_user")

        queryset = queryset.filter(
            Q(user__in=user_followings_objects) | Q(user=user)
        )

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
    queryset = Post.objects.all()

    def get_queryset(self):
        queryset = self.queryset

        queryset = queryset.annotate(
            amount_of_likes=(
                Count("likes")
            ),
        )

        return queryset
