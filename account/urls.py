"""
URL configuration for account project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, re_path
from djoser.views import UserViewSet
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

user_list = UserViewSet.as_view({"get": "list", "post": "create"})
user_detail = UserViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)
user_me = UserViewSet.as_view({"get": "me", "put": "me", "patch": "me", "delete": "me"})
user_activation = UserViewSet.as_view({"post": "activation"})
user_resend_activation = UserViewSet.as_view({"post": "resend_activation"})
user_reset_password = UserViewSet.as_view({"post": "reset_password"})
user_reset_password_confirm = UserViewSet.as_view({"post": "reset_password_confirm"})
user_set_password = UserViewSet.as_view({"post": "set_password"})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/users/", user_list, name="user-list"),
    path("api/users/activation/", user_activation, name="user-activation"),
    path("api/users/me/", user_me, name="user-me"),
    path(
        "api/users/resend_activation/",
        user_resend_activation,
        name="user-resend-activation",
    ),
    path(
        "api/users/reset_password/",
        user_reset_password,
        name="user-reset-password",
    ),
    path(
        "api/users/reset_password_confirm/",
        user_reset_password_confirm,
        name="user-reset-password-confirm",
    ),
    path(
        "api/users/set_password/",
        user_set_password,
        name="user-set-password",
    ),
    re_path(
        r"^api/users/(?P<id>[^/.]+)/$",
        user_detail,
        name="user-detail",
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=["json"])
