from rest_framework import routers

from django.urls import path, include

from post import views


router = routers.DefaultRouter()
router.register("posts", views.PostViewSet)
router.register("comments", views.CommentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "posts/<int:pk>/likes/",
        views.LikeListView.as_view(),
        name="post-likes"
    ),
    path(
        "posts/<int:pk>/like/",
        views.ToggleLikeView.as_view(),
        name="like-toggle"
    ),
    path(
        "posts/<int:pk>/add-comment/",
        views.CommentCreateView.as_view(),
        name="comment-create"
    ),
]

app_name = "post"
