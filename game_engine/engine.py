from .match_state import MatchState

class KhoKhoEngine:
    def __init__(self):
        self.state = MatchState()

    def start_match(self, team):
        self.state.start(team)

    def player_out(self, player_id):
        if player_id not in self.state.out_players:
            self.state.out_players.append(player_id)

    def get_state(self):
        return {
            "status": self.state.status,
            "remaining_time": self.state.remaining_time(),
            "active_team": self.state.active_team,
            "active_batch": self.state.active_batch,
            "out_players": self.state.out_players
        }
