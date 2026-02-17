from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError

from .models import Match
from .services import start_match
from .services import end_match
from .services import get_match_state
from .services import pause_match, resume_match
from scoring.services import get_match_scoreboard

from .models import MatchOfficial
from users.models import User




from common.permissions import IsMatchUmpireOrAdmin


class StartMatchAPI(APIView):
    permission_classes = [IsAuthenticated, IsMatchUmpireOrAdmin]

    def post(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id)
            start_match(match)
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "Match started successfully"},
            status=status.HTTP_200_OK
        )



class EndMatchAPI(APIView):
    permission_classes = [IsAuthenticated, IsMatchUmpireOrAdmin]

    def post(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id)
            end_match(match)
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "Match completed successfully"},
            status=status.HTTP_200_OK
        )


class MatchStateAPI(APIView):
    permission_classes = [IsAuthenticated,IsMatchUmpireOrAdmin]

    def get(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id)
            state = get_match_state(match)
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(state, status=status.HTTP_200_OK)


class PauseMatchAPI(APIView):
    permission_classes = [IsAuthenticated, IsMatchUmpireOrAdmin]

    def post(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id)
            pause_match(match)
            return Response({"message": "Match paused"}, status=200)
        except Match.DoesNotExist:
            return Response({"error": "Match not found"}, status=404)
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)


class ResumeMatchAPI(APIView):
    permission_classes = [IsAuthenticated, IsMatchUmpireOrAdmin]

    def post(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id)
            resume_match(match)
            return Response({"message": "Match resumed"}, status=200)
        except Match.DoesNotExist:
            return Response({"error": "Match not found"}, status=404)
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)


class LiveMatchAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id)

            scoreboard = get_match_scoreboard(match)

            return Response({
                "match_id": match.id,
                "status": match.status,
                "team_a": match.team_a.name,
                "team_b": match.team_b.name,
                "team_a_score": scoreboard.get("team_a_score", 0),
                "team_b_score": scoreboard.get("team_b_score", 0),
                "events": scoreboard.get("events", []),
            })

        except Match.DoesNotExist:
            return Response({"error": "Match not found"}, status=404)

class AssignOfficialAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Only ADMIN can assign
        if request.user.role != "ADMIN":
            return Response(
                {"error": "Only admin can assign officials"},
                status=status.HTTP_403_FORBIDDEN
            )

        match_id = request.data.get("match")
        user_id = request.data.get("user")
        role = request.data.get("role")

        if not all([match_id, user_id, role]):
            return Response(
                {"error": "match, user and role are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate role
        allowed_roles = dict(MatchOfficial.OFFICIAL_ROLE_CHOICES).keys()
        if role not in allowed_roles:
            return Response(
                {"error": "Invalid role"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return Response({"error": "Match not found"}, status=404)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # Prevent duplicate assignment
        if MatchOfficial.objects.filter(match=match, user=user).exists():
            return Response(
                {"error": "Official already assigned to this match"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Allow maximum 2 umpires
        if role == "UMPIRE":
            umpire_count = MatchOfficial.objects.filter(
                match=match,
                role="UMPIRE"
            ).count()

            if umpire_count >= 2:
                return Response(
                    {"error": "Only 2 umpires allowed per match"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Create assignment
        MatchOfficial.objects.create(
            match=match,
            user=user,
            role=role
        )

        return Response(
            {"message": "Official assigned successfully"},
            status=status.HTTP_201_CREATED
        )
