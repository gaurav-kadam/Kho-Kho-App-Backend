from django.core.exceptions import ValidationError

from matches.models import Match, MatchPlayer
from teams.models import Team
from players.models import Player
from .models import ScoreAuditLog, ScoreEvent


def create_score_event(
    *,
    match: Match,
    event_type: str,
    user,
    attacking_team: Team,
    defending_team: Team,
    player: Player | None = None
):
    
    # -------------------------
    # MATCH STATE VALIDATION
    # -------------------------
    if match.status != "LIVE":
        raise ValidationError("Score can be added only when match is LIVE")

    # -------------------------
    # TEAM VALIDATION
    # -------------------------
    if attacking_team not in [match.team_a, match.team_b]:
        raise ValidationError("Attacking team is not part of this match")

    if defending_team not in [match.team_a, match.team_b]:
        raise ValidationError("Defending team is not part of this match")

    if attacking_team == defending_team:
        raise ValidationError("Attacking and defending teams cannot be same")

    # -------------------------
    # PLAYER VALIDATION
    # -------------------------
    if player is not None:

        if player.team not in [match.team_a, match.team_b]:
            raise ValidationError("Player does not belong to this match")

        is_playing = MatchPlayer.objects.filter(
            match=match,
            player=player,
            status="PLAYING"
        ).exists()

        if not is_playing:
            raise ValidationError("Substitute player cannot score")

    # RULE 
   
    EVENT_POINTS = {
        "TOUCH": 1,
        "OUT": 1,
        "BONUS": 1,
        "ALL_OUT": 2,
        "FOUL": -1,
    }

    if event_type not in EVENT_POINTS:
        raise ValidationError("Invalid event type")

    # Assign points BEFORE creating event
    points = EVENT_POINTS[event_type]

    # -------------------------
    # CREATE SCORE EVENT
    # -------------------------
    score_event = ScoreEvent.objects.create(
        match=match,
        event_type=event_type,
        points=points, 
        attacking_team=attacking_team,
        defending_team=defending_team,
        player=player
    )

    # -------------------------
    # AUDIT LOG (HISTORY)
    # -------------------------
    ScoreAuditLog.objects.create(
        match=match,
        user=user,
        points=points
    )

    return score_event


def get_match_scoreboard(match):

    events = ScoreEvent.objects.filter(match=match).order_by("-timestamp")

    team_a_score = 0
    team_b_score = 0

    for event in events:
        if event.attacking_team == match.team_a:
            team_a_score += event.points
        elif event.attacking_team == match.team_b:
            team_b_score += event.points

    return {
        "team_a_score": team_a_score,
        "team_b_score": team_b_score,
        "events": [
            {
                "event_type": e.event_type,
                "points": e.points,
                "team": e.attacking_team.name,
                "player": e.player.name if e.player else None,
                "time": e.timestamp,
            }
            for e in events[:5]
        ]
    }
