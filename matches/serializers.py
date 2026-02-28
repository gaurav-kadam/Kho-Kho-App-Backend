# matches/serializers.py
from .models import Match, MatchResult

from rest_framework import serializers
from .models import Match, MatchResult  # Make sure MatchResult is imported

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'

class MatchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchResult
        fields = '__all__'

    def validate(self, data):
        match = data['match']
        team_a_score = data['team_a_score']
        team_b_score = data['team_b_score']
        is_draw = data.get('is_draw', False)
        winner = data.get('winner')

        # Basic score validation
        if team_a_score < 0 or team_b_score < 0:
            raise serializers.ValidationError("Scores cannot be negative")

        if is_draw:
            if team_a_score != team_b_score:
                raise serializers.ValidationError("Draw must have equal scores")
            if winner is not None:
                raise serializers.ValidationError("Draw cannot have a winner")
        else:
            if winner is None:
                raise serializers.ValidationError("Winner must be specified for non-draw match")
            if winner not in [match.team_a, match.team_b]:
                raise serializers.ValidationError("Winner must be one of the two teams")
            if (winner == match.team_a and team_a_score <= team_b_score) or \
               (winner == match.team_b and team_b_score <= team_a_score):
                raise serializers.ValidationError("Winner must have higher score")
        return data