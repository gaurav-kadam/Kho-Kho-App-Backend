from django.db import models
from django.core.exceptions import ValidationError
from matches.models import Match
from teams.models import Team
from players.models import Player
from django.conf import settings



class ScoreEvent(models.Model):

    EVENT_TYPE = [
        ('TOUCH', 'Touch'),
        ('OUT', 'Out'),
        ('BONUS', 'Bonus'),
        ("ALL_OUT", "All Out"),
        ('FOUL', 'Foul'),
    ]

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='score_events'
    )

    attacking_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='attacking_events'
    )

    defending_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='defending_events'
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE
    )

    points = models.PositiveIntegerField(default=0)

    timestamp = models.DateTimeField(auto_now_add=True)

    # VALIDATION 
    def clean(self):

        # 1 Match must be LIVE
        if self.match.status != 'LIVE':
            raise ValidationError("Scoring allowed only when match is LIVE.")

        # 2️ Attacking & Defending team must be different
        if self.attacking_team == self.defending_team:
            raise ValidationError("Attacking and Defending team cannot be same.")

        # 3️ Teams must belong to match
        valid_teams = [self.match.team_a, self.match.team_b]
        if self.attacking_team not in valid_teams:
            raise ValidationError("Attacking team does not belong to this match.")

        if self.defending_team not in valid_teams:
            raise ValidationError("Defending team does not belong to this match.")

        # 4️ Player must belong to attacking team (if provided)
        if self.player and self.player.team != self.attacking_team:
            raise ValidationError("Player must belong to attacking team.")

        # 5️ Points sanity check
        if self.points < 0:
            raise ValidationError("Points cannot be negative.")

    def save(self, *args, **kwargs):
        self.full_clean()   # Forces clean() always
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.match} | {self.event_type} | {self.points}"
    

# ======================================
# Audit

class ScoreAuditLog(models.Model):
    match = models.ForeignKey(
        'matches.Match',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    points = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} added {self.points} points"

