from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.utils.decorators import method_decorator
from djoser import signals
from djoser.conf import settings as djoser_settings
from djoser.compat import get_user_email
from djoser.views import UserViewSet
import json
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from .events import ESClient


# Create your views here.

User = get_user_model()

CACHE_TTL = settings.CACHE_TTL


class CustomizedUserViewSet(UserViewSet):
    # Set default ordering to ensure consistent paginated results.
    # It will be overrided by passed in fields.
    # UnorderedObjectListWarning is raised without default ordering.
    ordering = ["id"]

    # Not needed since we are using database routers.
    # def get_queryset(self):
    #     if self.action == "list" or self.action == "retrieve":
    #         self.queryset = User.objects.using("querydb")
    #     # self.queryset = User.objects.using("querydb")

    #     # Can not override db for create because of hardcoded behaviour
    #     # in UserCreateMixin:
    #     #   user = User.objects.create_user(**validated_data)

    #     return super().get_queryset()

    @method_decorator(cache_page(CACHE_TTL))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(CACHE_TTL))
    @method_decorator(vary_on_headers("Authorization"))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(["post"], detail=False)
    def activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        # Use transaction to ensure atomicity of user activation and event sending.
        with transaction.atomic():
            user.is_active = True
            user.save()
            data = json.dumps(
                {
                    "id": str(user.id),
                }
            )
            client = ESClient(
                "user",
                "UserActivated",
                data,
            )
            client.send()
            client.close()

        signals.user_activated.send(
            sender=self.__class__, user=user, request=self.request
        )

        if djoser_settings.SEND_CONFIRMATION_EMAIL:
            context = {"user": user}
            to = [get_user_email(user)]
            djoser_settings.EMAIL.confirmation(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)
