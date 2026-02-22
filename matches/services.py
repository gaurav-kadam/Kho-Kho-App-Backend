from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from scoring.services import get_match_scoreboard
from .models import MatchResult
from .models import Match
from .models import MatchOfficial
from teams.models import Team

def start_match(match):

    if match.status != "SCHEDULED":
        raise ValidationError("Only scheduled match can be started.")

    # Ensure at least 1 umpire assigned
    umpire_count = MatchOfficial.objects.filter(
        match=match,
        role="UMPIRE"
    ).count()

    if umpire_count < 1:
        raise ValidationError("Cannot start match without at least one umpire assigned.")

    match.status = "LIVE"
    match.started_at = timezone.now()
    match.save()

def end_match(match):

    if match.status != "LIVE":
        raise ValidationError("Only live match can be ended")

    if hasattr(match, "result"):
        raise ValidationError("Result already declared")

    from scoring.services import get_match_scoreboard
    from .models import MatchResult

    scoreboard = get_match_scoreboard(match)

    team_a_score = scoreboard["team_a_score"]
    team_b_score = scoreboard["team_b_score"]

    winner = None
    is_draw = False

    if team_a_score > team_b_score:
        winner = match.team_a
    elif team_b_score > team_a_score:
        winner = match.team_b
    else:
        is_draw = True

    MatchResult.objects.create(
        match=match,
        team_a_score=team_a_score,
        team_b_score=team_b_score,
        winner=winner,
        is_draw=is_draw
    )

    match.status = "COMPLETED"
    match.save()

def get_match_state(match: Match):
    """
    Returns current authoritative state of the match
    """

    remaining_time = None

    if match.status == 'LIVE' and match.started_at:
        elapsed = (timezone.now() - match.started_at).total_seconds()
        TOTAL_DURATION = 9 * 60  # 9 minutes (change later if needed)
        remaining_time = max(int(TOTAL_DURATION - elapsed), 0)

    return {
        "match_id": match.id,
        "status": match.status,
        "started_at": match.started_at,
        "ended_at": match.ended_at,
        "remaining_time": remaining_time,
    }




def pause_match(match):
    if match.status != 'LIVE':
            raise ValidationError("Only LIVE match can be paused")
    match.status = 'PAUSED'
    match.save()
    return match


def resume_match(match):
    if match.status != 'PAUSED':
        raise ValidationError("Only PAUSED match can be resumed")

    match.status = 'LIVE'
    match.save()
    return match


def get_tournament_standings(tournament):

    teams = Team.objects.filter(tournament=tournament)

    table = []

    for team in teams:

        results = MatchResult.objects.filter(
            match__tournament=tournament
        ).filter(
            Q(match__team_a=team) | Q(match__team_b=team)
        )

        played = results.count()

        wins = results.filter(winner=team).count()

        draws = results.filter(is_draw=True).count()

        losses = played - wins - draws

        # Calculate total points scored and conceded
        points_scored = 0
        points_conceded = 0

        for result in results:
            if result.match.team_a == team:
                points_scored += result.team_a_score
                points_conceded += result.team_b_score
            else:
                points_scored += result.team_b_score
                points_conceded += result.team_a_score

        score_difference = points_scored - points_conceded

        tournament_points = wins * 2 + draws  # Win=2, Draw=1

        table.append({
            "team": team.name,
            "played": played,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "points_scored": points_scored,
            "points_conceded": points_conceded,
            "score_difference": score_difference,
            "tournament_points": tournament_points
        })

    # Sort by tournament points first, then score difference
    table.sort(
        key=lambda x: (x["tournament_points"], x["score_difference"]),
        reverse=True
    )

    # Add ranking position
    for index, row in enumerate(table, start=1):
        row["rank"] = index

    return table