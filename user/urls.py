from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
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
]

app_name = "user"
