from django.contrib.auth import get_user_model, password_validation
from django.core import exceptions as django_exceptions
from django.db import transaction
from djoser.conf import settings
from djoser.serializers import UserCreateMixin
import json

from rest_framework import serializers
from rest_framework.settings import api_settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .events import ESClient

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


class StatelessTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["is_superuser"] = user.is_superuser
        token["is_staff"] = user.is_staff

        return token


class MyUserCreateMixin(UserCreateMixin):
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


class MyUserCreateSerializer(MyUserCreateMixin, serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    default_error_messages = {
        "cannot_create_user": settings.CONSTANTS.messages.CANNOT_CREATE_USER_ERROR
    }

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD,
            settings.USER_ID_FIELD,
            "password",
        )

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get("password")

        try:
            password_validation.validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error[api_settings.NON_FIELD_ERRORS_KEY]}
            )

        return attrs
