from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from post.models import Post
from post.serializers import PostListSerializer, PostRetrieveSerializer


class PostListView(generics.ListAPIView):
    serializer_class = PostListSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Post.objects.all()


class PostRetrieveView(generics.RetrieveAPIView):
    serializer_class = PostRetrieveSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Post.objects.all()
