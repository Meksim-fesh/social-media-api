from django.urls import path

from post import views

urlpatterns = [
    path("posts/", views.PostListView.as_view(), name="post-list"),
    path(
        "posts/<int:pk>/",
        views.PostRetrieveView.as_view(),
        name="post-detail"
    ),
]

app_name = "post"
