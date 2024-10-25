from rest_framework import serializers

from post.models import Comment, Like, Post


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "user", "content", "post")


class CommentCreateSerializer(CommentSerializer):
    class Meta:
        model = Comment
        fields = ("content", )

    def create(self, validated_data):

        post = self.context["post"]
        user = self.context["user"]

        validated_data["user"] = user
        validated_data["post"] = post

        data = super().create(validated_data)
        return data


class CommentListSerializer(CommentSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ("id", "user", "content",)


class CommentRetrieveUpdateDeleteSerializer(CommentSerializer):
    class Meta:
        model = Comment
        fields = ("content", )


class PostSerializer(serializers.ModelSerializer):
    scheduled_time = serializers.DateTimeField(required=False)

    class Meta:
        model = Post
        fields = (
            "id",
            "file",
            "text",
            "hashtag",
            "created_at",
            "scheduled_time",
        )


class PostListSerializer(PostSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )
    amount_of_comments = serializers.IntegerField(
        read_only=True,
    )
    amount_of_likes = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "file",
            "text",
            "hashtag",
            "user",
            "created_at",
            "amount_of_likes",
            "amount_of_comments",
        )


class PostRetrieveSerializer(PostSerializer):
    comments = CommentListSerializer(many=True, read_only=True)
    user = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )
    amount_of_likes = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = Post
        fields = (
            "file",
            "text",
            "hashtag",
            "user",
            "created_at",
            "amount_of_likes",
            "comments",
        )


class LikeListSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username", read_only=True
    )

    class Meta:
        model = Like
        fields = ("user",)


class ToggleLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = []
