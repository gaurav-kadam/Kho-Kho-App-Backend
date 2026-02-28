# teams/serializers.py
from rest_framework import serializers
from .models import Team

class TeamListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    player_count = serializers.IntegerField(source='players.count', read_only=True)
    
    class Meta:
        model = Team
        fields = [
            'id', 'name', 'short_name', 'color', 'logo',
            'tournament_name', 'status', 'player_count',
            'matches_played', 'matches_won', 'total_points'
        ]

class TeamDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single team view"""
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    win_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = [
            'matches_played', 'matches_won', 'matches_lost',
            'matches_drawn', 'total_points', 'created_at', 'updated_at'
        ]

    def get_win_percentage(self, obj):
        if obj.matches_played == 0:
            return 0
        return round((obj.matches_won / obj.matches_played) * 100, 2)

class TeamCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating teams with validation"""
    
    class Meta:
        model = Team
        fields = [
            'tournament', 'name', 'short_name', 'color', 'logo',
            'state', 'city', 'gender', 'age_group',
            'captain_name', 'coach_name', 'coach_contact'
        ]

    def validate_tournament(self, value):
        """Check if tournament allows more teams"""
        if value.teams.count() >= value.max_teams:
            raise serializers.ValidationError(
                f"Tournament already has maximum {value.max_teams} teams."
            )
        return value

    def validate_name(self, value):
        """Validate team name format"""
        if len(value) < 3:
            raise serializers.ValidationError("Team name must be at least 3 characters.")
        return value

    def validate_short_name(self, value):
        """Validate short name format"""
        if len(value) < 2:
            raise serializers.ValidationError("Short name must be at least 2 characters.")
        return value.upper()