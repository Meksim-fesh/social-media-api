from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)

from user import views


urlpatterns = [
    path("register/", views.CreateUserView.as_view(), name="create"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("me/", views.ManageUserView.as_view(), name="manage"),
    path("all/", views.UserListView.as_view(), name="user-list"),
    path(
        "profile/<int:pk>/",
        views.UserRetrieveView.as_view(),
        name="user-detail"
    ),
    path(
        "profile/<int:pk>/followers/",
        views.RetrieveUserFollowersView.as_view(),
        name="followers-list"
    ),
    path(
        "profile/<int:pk>/following/",
        views.RetrieveUserFollowingsView.as_view(),
        name="following-list"
    ),
    path(
        "profile/<int:pk>/toggle-follow/",
        views.ToggleUserFollowView.as_view(),
        name="toggle-follow"
    ),
    path(
        "me/followers/",
        views.RetrieveMyFollowers.as_view(),
        name="my-followers"
    ),
    path(
        "me/following/",
        views.RetrieveMyFollowing.as_view(),
        name="my-followings"
    ),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
]

app_name = "user"
