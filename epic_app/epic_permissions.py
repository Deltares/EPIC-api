from django.http import HttpRequest
from rest_framework import permissions


def _is_admin(request: HttpRequest) -> bool:
    return bool(request.user and request.user.is_staff) or bool(
        request.user and request.user.is_superuser
    )


def _is_epicuser_advisor(request: HttpRequest) -> bool:
    try:
        return request.user.epicuser and request.user.epicuser.is_advisor
    except:
        return None


class IsEpicAdvisor(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(request.user and _is_epicuser_advisor(request))


class IsAdminOrEpicAdvisor(permissions.IsAdminUser):
    def has_permission(self, request, view) -> bool:
        return super(IsAdminOrEpicAdvisor, self).has_permission(request, view) or bool(
            request.user and _is_epicuser_advisor(request)
        )


class IsAdminOrSelfUser(permissions.BasePermission):
    """
    Allows access only to admin users and the user itself.
    """

    def has_permission(self, request: HttpRequest, view):
        return _is_admin(request) or (
            request.user.pk != None and str(request.user.pk) == view.kwargs["pk"]
        )


class IsInstanceOwner(permissions.BasePermission):
    """
    Allows access to admin users and users in the field `user` of an entity.
    """

    def has_permission(self, request: HttpRequest, view) -> bool:
        try:
            return request.user.pk == view.get_object().user.pk
        except:
            return False
