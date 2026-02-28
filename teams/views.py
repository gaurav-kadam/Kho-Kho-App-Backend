# teams/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from .models import Team
from .serializers import TeamListSerializer, TeamDetailSerializer, TeamCreateSerializer

class TeamViewSet(viewsets.ModelViewSet):
    """
    Professional Team Management API
    """
    queryset = Team.objects.select_related('tournament').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tournament', 'gender', 'age_group', 'status', 'state']
    search_fields = ['name', 'short_name', 'city']
    ordering_fields = ['name', 'total_points', 'matches_won', 'created_at']
    ordering = ['-total_points', 'name']

    def get_serializer_class(self):
        """Different serializers for different actions"""
        if self.action == 'list':
            return TeamListSerializer
        elif self.action == 'create':
            return TeamCreateSerializer
        return TeamDetailSerializer

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

    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def update_stats(self, request, pk=None):
        """Manually update team statistics"""
        team = self.get_object()
        try:
            team.update_statistics()
            return Response({
                'status': 'success',
                'message': 'Team statistics updated',
                'data': TeamDetailSerializer(team).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def tournament_summary(self, request):
        """Get teams summary for a tournament"""
        tournament_id = request.query_params.get('tournament_id')
        if not tournament_id:
            return Response(
                {'error': 'tournament_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        teams = self.get_queryset().filter(tournament_id=tournament_id)
        serializer = TeamListSerializer(teams, many=True)
        
        # Add summary statistics
        summary = {
            'total_teams': teams.count(),
            'active_teams': teams.filter(status='ACTIVE').count(),
            'disqualified': teams.filter(status='DISQUALIFIED').count(),
            'teams': serializer.data
        }
        return Response(summary)

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Get top teams across all tournaments"""
        limit = int(request.query_params.get('limit', 10))
        teams = self.get_queryset().order_by('-total_points')[:limit]
        serializer = TeamListSerializer(teams, many=True)
        return Response(serializer.data)