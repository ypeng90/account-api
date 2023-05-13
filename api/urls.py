"""
URL configuration for account project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from .views import CustomizedUserViewSet


user_list = CustomizedUserViewSet.as_view({"get": "list", "post": "create"})
# Get User object from db -> meaningful id, username and password
user_detail = CustomizedUserViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)
# Get User object from token -> meaningful id and empty username and password
user_me = CustomizedUserViewSet.as_view(
    {"get": "me", "put": "me", "patch": "me", "delete": "me"}
)
user_activation = CustomizedUserViewSet.as_view({"post": "activation"})
user_resend_activation = CustomizedUserViewSet.as_view({"post": "resend_activation"})
user_reset_password = CustomizedUserViewSet.as_view({"post": "reset_password"})
user_reset_password_confirm = CustomizedUserViewSet.as_view(
    {"post": "reset_password_confirm"}
)
user_set_password = CustomizedUserViewSet.as_view({"post": "set_password"})

urlpatterns = [
    path("users/", user_list, name="user-list"),
    path("users/activation/", user_activation, name="user-activation"),
    path("users/me/", user_me, name="user-me"),
    path(
        "users/resend_activation/",
        user_resend_activation,
        name="user-resend-activation",
    ),
    path(
        "users/reset_password/",
        user_reset_password,
        name="user-reset-password",
    ),
    path(
        "users/reset_password_confirm/",
        user_reset_password_confirm,
        name="user-reset-password-confirm",
    ),
    path(
        "users/set_password/",
        user_set_password,
        name="user-set-password",
    ),
    re_path(
        r"^users/(?P<id>[^/.]+)/$",
        user_detail,
        name="user-detail",
    ),
]
