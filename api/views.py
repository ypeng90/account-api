from django.contrib.auth import get_user_model
from djoser.views import UserViewSet


# Create your views here.

User = get_user_model()


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
