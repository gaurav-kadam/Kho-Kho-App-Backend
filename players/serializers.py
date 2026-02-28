# players/serializers.py
from rest_framework import serializers
from .models import Player
from teams.models import Team

class PlayerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    team_name = serializers.CharField(source='team.name', read_only=True)
    full_name = serializers.CharField(source='full_name', read_only=True)
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = Player
        fields = [
            'id', 'full_name', 'jersey_number', 'role', 
            'team_name', 'is_active', 'age'
        ]
    
    def get_age(self, obj):
        from datetime import date
        today = date.today()
        age = today.year - obj.date_of_birth.year
        if today.month < obj.date_of_birth.month or \
           (today.month == obj.date_of_birth.month and today.day < obj.date_of_birth.day):
            age -= 1
        return age

class PlayerDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single player view"""
    team_name = serializers.CharField(source='team.name', read_only=True)
    tournament_name = serializers.CharField(source='team.tournament.name', read_only=True)
    full_name = serializers.CharField(source='full_name', read_only=True)
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = Player
        fields = '__all__'
        read_only_fields = ['created_at']
    
    def get_age(self, obj):
        from datetime import date
        today = date.today()
        age = today.year - obj.date_of_birth.year
        if today.month < obj.date_of_birth.month or \
           (today.month == obj.date_of_birth.month and today.day < obj.date_of_birth.day):
            age -= 1
        return age

class PlayerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating players with validation"""
    
    class Meta:
        model = Player
        fields = [
            'team', 'first_name', 'last_name', 'jersey_number',
            'role', 'date_of_birth', 'is_active'
        ]
    
    def validate_team(self, value):
        """Check if team has space for more players"""
        if value.players.count() >= 15:
            raise serializers.ValidationError(
                f"Team {value.name} already has maximum 15 players."
            )
        return value
    
    def validate_jersey_number(self, value):
        """Jersey number must be positive"""
        if value <= 0:
            raise serializers.ValidationError("Jersey number must be positive.")
        if value > 99:
            raise serializers.ValidationError("Jersey number cannot exceed 99.")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        team = data.get('team')
        jersey = data.get('jersey_number')
        
        # Check if jersey number is unique in team
        if Player.objects.filter(team=team, jersey_number=jersey).exists():
            raise serializers.ValidationError(
                f"Jersey number {jersey} already exists in team {team.name}."
            )
        
        # Age validation based on tournament
        from datetime import date
        today = date.today()
        dob = data.get('date_of_birth')
        age = today.year - dob.year
        if today.month < dob.month or \
           (today.month == dob.month and today.day < dob.day):
            age -= 1
        
        age_group = team.tournament.age_group
        
        if age_group == "U14" and age > 14:
            raise serializers.ValidationError(
                f"Player age {age} exceeds U14 limit."
            )
        if age_group == "U17" and age > 17:
            raise serializers.ValidationError(
                f"Player age {age} exceeds U17 limit."
            )
        if age_group == "U19" and age > 19:
            raise serializers.ValidationError(
                f"Player age {age} exceeds U19 limit."
            )
        
        return data