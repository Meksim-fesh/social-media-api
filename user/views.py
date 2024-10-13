from django.contrib.auth import get_user_model

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

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
    queryset = get_user_model().objects.all()
