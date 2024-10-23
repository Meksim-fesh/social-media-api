from rest_framework import routers

from django.urls import path, include

from post import views


router = routers.DefaultRouter()
router.register("posts", views.PostViewSet)

urlpatterns = [
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
    path("", include(router.urls)),
]

app_name = "post"
