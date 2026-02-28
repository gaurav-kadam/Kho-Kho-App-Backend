from re import match
from time import timezone

from django.db.models import Q, Sum, Count, Case, When, IntegerField
from teams.models import Team
from matches.models import MatchResult
from rest_framework import viewsets

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

from .models import Match, MatchResult
from .serializers import MatchResultSerializer

from .models import MatchOfficial
from users.models import User

from .models import MatchPlayer
from players.models import Player


from common.permissions import (
    IsMatchOfficialOrAdmin,
    IsMatchOfficialWithRole
)



class StartMatchAPI(APIView):
    permission_classes = [IsAuthenticated, IsMatchOfficialWithRole]
    IsMatchOfficialWithRole.allowed_roles = ["UMPIRE"]


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
    permission_classes = [IsAuthenticated, IsMatchOfficialWithRole]
    IsMatchOfficialWithRole.allowed_roles = ["UMPIRE"]


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
    permission_classes = [IsAuthenticated, IsMatchOfficialOrAdmin]

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
    permission_classes = [IsAuthenticated, IsMatchOfficialWithRole]
    IsMatchOfficialWithRole.allowed_roles = ["UMPIRE"]

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
    permission_classes = [IsAuthenticated, IsMatchOfficialWithRole]
    IsMatchOfficialWithRole.allowed_roles = ["UMPIRE"]

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
            
            result_data = None

            if hasattr(match, "result"):
                result_data = {
                "team_a_score": match.result.team_a_score,
                "team_b_score": match.result.team_b_score,
                "winner": match.result.winner.name if match.result.winner else None,
                "is_draw": match.result.is_draw
            }

            return Response({
                "match_id": match.id,
                "status": match.status,
                "team_a": match.team_a.name,
                "team_b": match.team_b.name,
                "team_a_score": scoreboard.get("team_a_score", 0),
                "team_b_score": scoreboard.get("team_b_score", 0),
                "events": scoreboard.get("events", []),
                "result": result_data,
            })

        except Match.DoesNotExist:
            return Response({"error": "Match not found"}, status=404)

class AssignOfficialAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        if request.user.role != "ADMIN":
            return Response(
                {"error": "Only ADMIN can assign officials"},
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

        allowed_roles = dict(MatchOfficial.OFFICIAL_ROLE_CHOICES).keys()

        if role not in allowed_roles:
            return Response(
                {"error": "Invalid role"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            match = Match.objects.get(id=match_id)
            user = User.objects.get(id=user_id)
        except Match.DoesNotExist:
            return Response({"error": "Match not found"}, status=404)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if MatchOfficial.objects.filter(match=match, user=user).exists():
            return Response(
                {"error": "Official already assigned"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if role == "UMPIRE":
            umpire_count = MatchOfficial.objects.filter(
                match=match,
                role="UMPIRE"
            ).count()

            if umpire_count >= 2:
                return Response(
                    {"error": "Maximum 2 umpires allowed"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        MatchOfficial.objects.create(
            match=match,
            user=user,
            role=role
        )

        return Response(
            {"message": "Official assigned successfully"},
            status=status.HTTP_201_CREATED
        )

class AssignMatchPlayerAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        if request.user.role != "ADMIN":
            return Response(
                {"error": "Only admin can assign match players"},
                status=403
            )

        match_id = request.data.get("match")
        player_id = request.data.get("player")
        status_value = request.data.get("status", "PLAYING")

        if not all([match_id, player_id]):
            return Response(
                {"error": "match and player are required"},
                status=400
            )

        try:
            match = Match.objects.get(id=match_id)
            player = Player.objects.get(id=player_id)

            MatchPlayer.objects.create(
                match=match,
                player=player,
                status=status_value
            )

            return Response(
                {"message": "Player assigned to match successfully"},
                status=201
            )

        except Match.DoesNotExist:
            return Response({"error": "Match not found"}, status=404)

        except Player.DoesNotExist:
            return Response({"error": "Player not found"}, status=404)

        except ValidationError as e:
            return Response({"error": str(e)}, status=400)
        
class TournamentStandingsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, tournament_id):

        from tournaments.models import Tournament
        from .services import get_tournament_standings

        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response({"error": "Tournament not found"}, status=404)

        table = get_tournament_standings(tournament)

        return Response({
            "tournament": tournament.name,
            "standings": table
        })
    
class MatchResultViewSet(viewsets.ModelViewSet):
    queryset = MatchResult.objects.all()
    serializer_class = MatchResultSerializer
    permission_classes = [IsAuthenticated]  # adjust as needed

    def create(self, request, *args, **kwargs):
        # Ensure match is not already completed
        match_id = request.data.get('match')
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return Response({'error': 'Match not found'}, status=status.HTTP_404_NOT_FOUND)

        if match.status == 'COMPLETED':
            return Response({'error': 'Match already completed'}, status=status.HTTP_400_BAD_REQUEST)

        # Save result
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Update match status and ended_at
        match.status = 'COMPLETED'
        match.ended_at = timezone.now()
        match.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)