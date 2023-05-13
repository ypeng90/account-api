from rest_framework import permissions


class CurrentUserOrAdmin(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        # UUID('5f9e398f-22dc-4517-b325-e81a4c2ec220') vs '5f9e398f-22dc-4517-b325-e81a4c2ec220'
        return user.is_staff or obj.pk == user.pk or str(obj.pk) == user.pk
