from datetime import datetime, timedelta

class MatchState:
    def __init__(self, duration_seconds=540):  # 9 minutes
        self.status = "NOT_STARTED"  # NOT_STARTED, RUNNING, PAUSED, FINISHED
        self.start_time = None
        self.duration = timedelta(seconds=duration_seconds)
        self.active_team = None
        self.active_batch = 1
        self.out_players = []

    def start(self, team):
        self.status = "RUNNING"
        self.start_time = datetime.utcnow()
        self.active_team = team

    def remaining_time(self):
        if self.status != "RUNNING":
            return int(self.duration.total_seconds())

        elapsed = datetime.utcnow() - self.start_time
        remaining = self.duration - elapsed
        return max(int(remaining.total_seconds()), 0)
