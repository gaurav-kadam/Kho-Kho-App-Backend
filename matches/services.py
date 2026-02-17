from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Match


def start_match(match: Match):
    if match.status != 'SCHEDULED':
        raise ValidationError("Match already started or completed")

    match.status = 'LIVE'
    match.started_at = timezone.now()
    match.save()
    return match


def end_match(match: Match):
    if match.status != 'LIVE':
        raise ValidationError("Only LIVE matches can be ended")

    match.status = 'COMPLETED'
    match.ended_at = timezone.now()
    match.save()
    return match


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
