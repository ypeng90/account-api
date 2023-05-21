from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.conf import settings
from djoser.serializers import UserCreateSerializer
import json

from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
    TokenBlacklistSerializer,
)
from .events import ESClient
from .tokens import MyRefreshToken

# Workaround to serialize UUIDs
# from json import JSONEncoder
# from uuid import UUID
# old_default = JSONEncoder.default
# def new_default(self, obj):
#     if isinstance(obj, UUID):
#         return str(obj)
#     return old_default(self, obj)
# JSONEncoder.default = new_default

User = get_user_model()


class MyStatelessTokenObtainPairSerializer(TokenObtainPairSerializer):
    token_class = MyRefreshToken

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["is_superuser"] = user.is_superuser
        token["is_staff"] = user.is_staff

        return token


class MyTokenRefreshSerializer(TokenRefreshSerializer):
    token_class = MyRefreshToken


class MyTokenBlacklistSerializer(TokenBlacklistSerializer):
    token_class = MyRefreshToken


class MyUserCreateSerializer(UserCreateSerializer):
    def perform_create(self, validated_data):
        # Use transaction to ensure atomicity of user creation and event sending.
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            if settings.SEND_ACTIVATION_EMAIL:
                user.is_active = False
                user.save(update_fields=["is_active"])
            data = json.dumps(
                {
                    "id": str(user.id),
                    "username": user.username,
                    "password": user.password,
                    "email": user.email,
                    "is_active": user.is_active,
                    "is_superuser": user.is_superuser,
                    "is_staff": user.is_staff,
                }
            )
            client = ESClient(
                "user",
                "UserCreated",
                data,
            )
            client.send()
            client.close()

        return user
