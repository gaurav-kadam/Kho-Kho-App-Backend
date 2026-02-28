from django.shortcuts import render

# Create your views here.
# tournaments/views.py

from django.db.models import Q, Sum, Count, Case, When, IntegerField
from teams.models import Team
from matches.models import MatchResult

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Tournament
from .serializers import TournamentSerializer
from .utils import create_matches_for_tournament
from matches.serializers import MatchSerializer  # we'll create this next

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

    @action(detail=True, methods=['post'])
    def generate_matches(self, request, pk=None):
        tournament = self.get_object()
        # Get all teams belonging to this tournament
        teams = tournament.teams.all()
        if teams.count() < 2:
            return Response(
                {'error': 'At least 2 teams are required to generate matches'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Check if matches already exist
        if tournament.matches.exists():
            return Response(
                {'error': 'Matches have already been generated for this tournament'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Create matches
        matches = create_matches_for_tournament(
            tournament,
            [team.id for team in teams],
            venue=request.data.get('venue', 'TBD')
        )
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def tournament_standings(request, tournament_id):
    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return Response({'error': 'Tournament not found'}, status=404)

    teams = Team.objects.filter(tournament=tournament)
    # Initialize stats
    standings = []
    for team in teams:
        # Get all match results involving this team
        results = MatchResult.objects.filter(
            Q(match__team_a=team) | Q(match__team_b=team)
        ).select_related('match')

        played = 0
        won = 0
        drawn = 0
        lost = 0
        points = 0
        score_for = 0
        score_against = 0

        for res in results:
            match = res.match
            # Determine if team is team_a or team_b
            is_team_a = (match.team_a == team)
            team_score = res.team_a_score if is_team_a else res.team_b_score
            opponent_score = res.team_b_score if is_team_a else res.team_a_score

            played += 1
            score_for += team_score
            score_against += opponent_score

            if res.is_draw:
                drawn += 1
                points += 1
            else:
                if res.winner == team:
                    won += 1
                    points += 2   # 2 points for win
                else:
                    lost += 1

        standings.append({
            'team_id': team.id,
            'team_name': team.name,
            'played': played,
            'won': won,
            'drawn': drawn,
            'lost': lost,
            'points': points,
            'score_for': score_for,
            'score_against': score_against,
            'net_score': score_for - score_against,
        })

    # Sort by points, then net score
    standings.sort(key=lambda x: (-x['points'], -x['net_score']))
    return Response(standings)