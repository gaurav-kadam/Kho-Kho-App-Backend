from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.core.exceptions import ValidationError

from common.responses import error_response, success_response
from teams.models import Team
from players.models import Player
from matches.models import Match
from common.permissions import IsMatchOfficialWithRole
from .services import create_score_event, get_match_scoreboard


class CreateScoreEventAPI(APIView):
    permission_classes = [IsAuthenticated, IsMatchOfficialWithRole]

    IsMatchOfficialWithRole.allowed_roles = ["UMPIRE"]

    def post(self, request):
        try:
            match_id = request.data.get("match")
            event_type = request.data.get("event_type")
            attacking_team_id = request.data.get("attacking_team")
            defending_team_id = request.data.get("defending_team")
            player_id = request.data.get("player")

            if not all([match_id, attacking_team_id, defending_team_id]):
                return Response(
                    {"error": "match, points, event_type, attacking_team, defending_team are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            match = Match.objects.get(id=match_id)
            attacking_team = Team.objects.get(id=attacking_team_id)
            defending_team = Team.objects.get(id=defending_team_id)
            player = Player.objects.get(id=player_id) if player_id else None

            score_event = create_score_event(
                match=match,
                event_type=event_type,
                user=request.user,
                attacking_team=attacking_team,
                defending_team=defending_team,
                player=player
            )

            return Response(
                {"message": "Score added successfully", "score_id": score_event.id},
                status=status.HTTP_201_CREATED
            )

        except Match.DoesNotExist:
            return Response({"error": "Match not found"}, status=404)

        except Team.DoesNotExist:
            return Response({"error": "Invalid team"}, status=400)

        except Player.DoesNotExist:
            return Response({"error": "Invalid player"}, status=400)

        except ValidationError as e:
            return Response({"error": str(e)}, status=400)


class MatchScoreboardAPI(APIView):
    def get(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return error_response(
                "Match not found",
                status_code=404
            )

        data = get_match_scoreboard(match)
        return success_response(
            "Scoreboard fetched successfully",
            data=data,
            status_code=200
            )

