from rest_framework.permissions import BasePermission
from matches.models import MatchOfficial


class IsMatchOfficialOrAdmin(BasePermission):
    """
    Allows access only if:
    - User is ADMIN
    - OR user is assigned to the match
    """

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        # Admin always allowed
        if request.user.role == "ADMIN":
            return True

        match_id = view.kwargs.get("match_id")

        if not match_id:
            return False

        return MatchOfficial.objects.filter(
            match_id=match_id,
            user=request.user
        ).exists()


class IsMatchOfficialWithRole(BasePermission):
    """
    Allows access only if:
    - User is ADMIN
    - OR user is assigned with specific role
    """

    allowed_roles = []

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.role == "ADMIN":
            return True

        match_id = view.kwargs.get("match_id")

        if not match_id:
            return False

        return MatchOfficial.objects.filter(
            match_id=match_id,
            user=request.user,
            role__in=self.allowed_roles
        ).exists()
