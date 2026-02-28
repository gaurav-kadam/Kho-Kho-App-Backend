# players/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from .models import Player
from .serializers import (
    PlayerListSerializer, PlayerDetailSerializer, PlayerCreateSerializer
)

class PlayerViewSet(viewsets.ModelViewSet):
    """
    Professional Player Management API
    """
    queryset = Player.objects.select_related('team__tournament').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['team', 'team__tournament', 'role', 'is_active']
    search_fields = ['first_name', 'last_name', 'team__name']
    ordering_fields = ['first_name', 'last_name', 'jersey_number', 'created_at']
    ordering = ['team', 'jersey_number']

    def get_serializer_class(self):
        """Different serializers for different actions"""
        if self.action == 'list':
            return PlayerListSerializer
        elif self.action == 'create':
            return PlayerCreateSerializer
        return PlayerDetailSerializer

    def get_permissions(self):
        """Custom permissions based on action"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def by_team(self, request):
        """Get all players for a specific team"""
        team_id = request.query_params.get('team_id')
        if not team_id:
            return Response(
                {'error': 'team_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        players = self.get_queryset().filter(team_id=team_id)
        serializer = PlayerListSerializer(players, many=True)
        
        # Add team summary
        team = players.first().team if players.exists() else None
        summary = {
            'team_name': team.name if team else None,
            'total_players': players.count(),
            'active_players': players.filter(is_active=True).count(),
            'raiders': players.filter(role='RAIDER').count(),
            'defenders': players.filter(role='DEFENDER').count(),
            'all_rounders': players.filter(role='ALL_ROUNDER').count(),
            'players': serializer.data
        }
        return Response(summary)

    @action(detail=False, methods=['get'])
    def by_tournament(self, request):
        """Get all players for a specific tournament"""
        tournament_id = request.query_params.get('tournament_id')
        if not tournament_id:
            return Response(
                {'error': 'tournament_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        players = self.get_queryset().filter(team__tournament_id=tournament_id)
        serializer = PlayerListSerializer(players, many=True)
        return Response({
            'tournament_id': tournament_id,
            'total_players': players.count(),
            'players': serializer.data
        })

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle player active status"""
        player = self.get_object()
        player.is_active = not player.is_active
        player.save()
        return Response({
            'status': 'success',
            'is_active': player.is_active
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get player statistics across all teams"""
        stats = self.get_queryset().aggregate(
            total_players=Count('id'),
            active_players=Count('id', filter=Q(is_active=True)),
            raiders=Count('id', filter=Q(role='RAIDER')),
            defenders=Count('id', filter=Q(role='DEFENDER')),
            all_rounders=Count('id', filter=Q(role='ALL_ROUNDER')),
        )
        return Response(stats)