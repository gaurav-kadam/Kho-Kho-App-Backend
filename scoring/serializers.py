from rest_framework import serializers
from .models import ScoreEvent

class ScoreEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScoreEvent
        fields = [
            'id',
            'match',
            'attacking_team',
            'defending_team',
            'player',
            'event_type',
            'points',
            'timestamp',
        ]
