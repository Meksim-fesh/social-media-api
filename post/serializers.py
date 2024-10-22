from rest_framework import serializers

from post.models import Comment, Post


class CommentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("content", "user",)


class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "file",
            "text",
            "hashtag",
            "user",
            "created_at",
        )


class PostRetrieveSerializer(serializers.ModelSerializer):
    comments = CommentListSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "file",
            "text",
            "hashtag",
            "user",
            "created_at",
            "comments",
        )
