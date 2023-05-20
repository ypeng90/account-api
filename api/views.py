from django.conf import settings
from django.contrib.auth import get_user_model
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from djoser.views import UserViewSet
from django.utils.decorators import method_decorator


# Create your views here.

User = get_user_model()

CACHE_TTL = settings.CACHE_TTL


class CustomizedUserViewSet(UserViewSet):
    # Set default ordering to ensure consistent paginated results.
    # It will be overrided by passed in fields.
    # UnorderedObjectListWarning is raised without default ordering.
    ordering = ["id"]

    def get_queryset(self):
        if self.action == "list" or self.action == "retrieve":
            self.queryset = User.objects.using("querydb")
        # self.queryset = User.objects.using("querydb")

        # Can not override db for create because of hardcoded behaviour
        # in UserCreateMixin:
        #   user = User.objects.create_user(**validated_data)

        return super().get_queryset()

    @method_decorator(cache_page(CACHE_TTL))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(CACHE_TTL))
    @method_decorator(vary_on_headers("Authorization"))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
