from djoser.views import UserViewSet


# Create your views here.
class CustomizedUserViewSet(UserViewSet):
    # Set default ordering to ensure consistent paginated results.
    # It will be overrided by passed in fields.
    # UnorderedObjectListWarning is raised without default ordering.
    ordering = ["id"]
