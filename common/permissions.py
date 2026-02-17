from rest_framework.permissions import BasePermission
from matches.models import MatchOfficial

class IsMatchUmpireOrAdmin(BasePermission):

    def has_permission(self, request, view):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin always allowed
        if request.user.role == "ADMIN":
            return True

        # Must have match_id in URL
        match_id = view.kwargs.get("match_id")

        if not match_id:
            return False

        # Check if user is assigned as UMPIRE for this match
        return MatchOfficial.objects.filter(
            match_id=match_id,
            user=request.user,
            role="UMPIRE"
        ).exists()
