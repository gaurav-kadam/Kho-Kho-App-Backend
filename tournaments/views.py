from django.shortcuts import render

# Create your views here.
# tournaments/views.py
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