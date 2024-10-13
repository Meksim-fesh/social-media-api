from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password",)
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 5,
                "style": {
                    "input_type": "password",
                },
            }
        }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class UserRetrieveMyselfSerializer(UserSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "picture",
            "username",
            "first_name",
            "last_name",
            "bio",
            "email",
            "is_staff",
            "date_joined",
        )
        read_only_fields = (
            "is_staff",
            "date_joined",
        )


class UserListSerializer(UserSerializer):
    class Meta:
        model = get_user_model()
        fields = ("username", "first_name", "last_name",)


class UserRetrieveSerializer(UserSerializer):
    i_follow = serializers.IntegerField(read_only=True)
    my_followers = serializers.IntegerField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "picture",
            "username",
            "first_name",
            "last_name",
            "bio",
            "i_follow",
            "my_followers",
        )
