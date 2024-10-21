from django.contrib import admin

from post.models import Comment, Like, Post


admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)
