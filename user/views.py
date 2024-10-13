from django.contrib.auth import get_user_model
from django.db.models import Count

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response

from user import serializers


class CreateUserView(generics.CreateAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = (AllowAny,)


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.UserRetrieveMyselfSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    serializer_class = serializers.UserListSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get_queryset(self):
        queryset = get_user_model().objects.all()

        username = self.request.query_params.get("username")
        if username:
            queryset = queryset.filter(username__icontains=username)

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


class RetrieveUserFollowersView(generics.GenericAPIView):
    serializer_class = serializers.UserFollowersListSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    queryset = get_user_model().objects.prefetch_related("followers__user")

    def get(self, request, *args, **kwargs):
        instance = self.get_object().followers.all()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)


class RetrieveUserFollowingsView(generics.GenericAPIView):
    serializer_class = serializers.UserFollowingListSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    queryset = get_user_model().objects.prefetch_related(
        "following__following_user"
    )

    def get(self, request, *args, **kwargs):
        instance = self.get_object().following.all()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)
