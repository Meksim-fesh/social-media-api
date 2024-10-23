from rest_framework import serializers

from post.models import Comment, Post


class CommentListSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ("user", "content",)


class PostSerializer(serializers.ModelSerializer):
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
            "id",
            "file",
            "text",
            "hashtag",
            "user",
            "created_at",
            "amount_of_likes",
        )


class PostListSerializer(PostSerializer):
    amount_of_comments = serializers.IntegerField(
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
