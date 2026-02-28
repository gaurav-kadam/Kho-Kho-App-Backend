# tournaments/utils.py
from datetime import timedelta
from matches.models import Match

def generate_round_robin_fixtures(team_ids):
    """
    Generate round-robin fixtures for a list of team IDs.
    Returns list of dicts: {'team_a': id, 'team_b': id, 'round': round_number}
    Handles even and odd number of teams (adds a dummy 'bye' for odd counts).
    """
    teams = list(team_ids)
    num_teams = len(teams)
    
    # If odd, add a dummy None (bye) – matches with None will be skipped
    if num_teams % 2 != 0:
        teams.append(None)
        num_teams += 1

    num_rounds = num_teams - 1
    half = num_teams // 2
    fixtures = []

    for round_num in range(num_rounds):
        round_matches = []
        for i in range(half):
            team_a = teams[i]
            team_b = teams[num_teams - 1 - i]
            # Skip if either team is None (bye)
            if team_a is not None and team_b is not None:
                round_matches.append((team_a, team_b))
        fixtures.extend([{'team_a': a, 'team_b': b, 'round': round_num + 1} for a, b in round_matches])
        
        # Rotate teams (keep first team fixed)
        teams = [teams[0]] + [teams[-1]] + teams[1:-1]

    return fixtures


def create_matches_for_tournament(tournament, team_ids, venue="TBD"):
    """
    Create Match objects for a tournament using round-robin fixtures.
    Matches are scheduled starting from tournament.start_date, one per day.
    """
    fixtures = generate_round_robin_fixtures(team_ids)
    matches_created = []
    base_date = tournament.start_date

    for idx, fix in enumerate(fixtures):
        match = Match.objects.create(
            tournament=tournament,
            team_a_id=fix['team_a'],
            team_b_id=fix['team_b'],
            match_number=idx + 1,
            round_number=fix['round'],
            match_date=base_date + timedelta(days=idx),  # simple scheduling
            venue=venue,
            status='SCHEDULED'
        )
        matches_created.append(match)
    
    return matches_created