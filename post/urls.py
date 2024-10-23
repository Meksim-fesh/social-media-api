from django.urls import path

from post import views

urlpatterns = [
    path("posts/", views.PostListView.as_view(), name="post-list"),
    path(
        "posts/<int:pk>/",
        views.PostRetrieveView.as_view(),
        name="post-detail"
    ),
    path(
        "posts/<int:pk>/likes/",
        views.LikeListView.as_view(),
        name="post-likes"
    ),
]

app_name = "post"
