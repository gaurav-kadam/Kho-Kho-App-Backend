from django.db import models
from django.forms import ValidationError
from tournaments.models import Tournament
from teams.models import Team
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q

User = settings.AUTH_USER_MODEL


class Match(models.Model):

    STATUS_CHOICES = [
        ("SCHEDULED", "Scheduled"),
        ("LIVE", "Live"),
        ("PAUSED", "Paused"),
        ("COMPLETED", "Completed"),
    ]

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name="matches"
    )

    team_a = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="team_a_matches"
    )

    team_b = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="team_b_matches"
    )

    match_number = models.PositiveIntegerField()
    
    venue = models.CharField(max_length=200)

    match_date = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="SCHEDULED"
    )

    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tournament", "match_number")

    def clean(self):

        if self.match_number <= 0:
            raise ValidationError("Match number must be positive.")

        # Teams cannot be same
        if self.team_a == self.team_b:
            raise ValidationError("Team A and Team B cannot be same.")

        # Teams must belong to same tournament
        if self.team_a.tournament != self.tournament:
            raise ValidationError("Team A does not belong to this tournament.")

        if self.team_b.tournament != self.tournament:
            raise ValidationError("Team B does not belong to this tournament.")

        # Teams must have minimum 7 active players
        if self.team_a.players.filter(is_active=True).count() < 7:
            raise ValidationError("Team A must have at least 7 active players.")

        if self.team_b.players.filter(is_active=True).count() < 7:
            raise ValidationError("Team B must have at least 7 active players.")
        
        if self.match_date.date() < self.tournament.start_date or \
            self.match_date.date() > self.tournament.end_date:
            raise ValidationError("Match date must be within tournament dates.")
        if not self.tournament.is_active:
            raise ValidationError("Cannot create match for inactive tournament.")
        

        conflict = Match.objects.filter(
            match_date=self.match_date
        ).filter(
            Q(team_a=self.team_a) |
            Q(team_b=self.team_a) |
            Q(team_a=self.team_b) |
            Q(team_b=self.team_b)
        ).exclude(id=self.id)

        if conflict.exists():
            raise ValidationError("One of the teams already has a match at this time.")


    def save(self, *args, **kwargs):

    # Auto-generate match number if not provided
        if not self.match_number:
            last_match = Match.objects.filter(
                tournament=self.tournament
            ).order_by("-match_number").first()

            if last_match and last_match.match_number:
                self.match_number = last_match.match_number + 1
            else:
                self.match_number = 1

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Match {self.match_number} - {self.team_a.name} vs {self.team_b.name}"



class MatchOfficial(models.Model):
    OFFICIAL_ROLE_CHOICES = [
        ("UMPIRE", "Umpire"),
        ("REFEREE", "Referee"),
        ("SCORER", "Scorer"),
        ("TIME_KEEPER", "Time Keeper"),
    ]

    match = models.ForeignKey(
        "matches.Match",
        on_delete=models.CASCADE,
        related_name="officials"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    role = models.CharField(
        max_length=20,
        choices=OFFICIAL_ROLE_CHOICES
    )

    class Meta:
        unique_together = ("match", "user", "role")

    def clean(self):

    # Prevent official time conflict
        conflict = MatchOfficial.objects.filter(
            user=self.user,
            match__match_date=self.match.match_date
        ).exclude(id=self.id)

        if conflict.exists():
            raise ValidationError("Official already assigned to another match at this time.")

        # Enforce max 2 umpires
        if self.role == "UMPIRE":
            existing = MatchOfficial.objects.filter(
                match=self.match,
                role="UMPIRE"
            ).exclude(id=self.id).count()

            if existing >= 2:
                raise ValidationError("Only 2 umpires allowed per match.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} ({self.role}) - {self.match}"




class MatchStaff(models.Model):
    STAFF_ROLE_CHOICES = [
        ("MEDICAL", "Medical Staff"),
        ("GROUND", "Ground Staff"),
        ("TECHNICAL", "Technical Staff"),
    ]

    match = models.ForeignKey(
        "matches.Match",
        on_delete=models.CASCADE,
        related_name="staff"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    role = models.CharField(
        max_length=20,
        choices=STAFF_ROLE_CHOICES
    )

    class Meta:
        unique_together = ("match", "user", "role")

    def __str__(self):
        return f"{self.user} ({self.role}) - {self.match}"


class MatchPlayer(models.Model):
    PLAYER_STATUS = [
        ("PLAYING", "Playing"),
        ("SUBSTITUTE", "Substituting"),
    ]

    match = models.ForeignKey(
        "matches.Match",
        on_delete=models.CASCADE,
        related_name="match_players"
    )

    player = models.ForeignKey(
        "players.Player",
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=20,
        choices=PLAYER_STATUS,
        default="PLAYING"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("match", "player")

    def clean(self):

        # 1 Player must belong to one of the match teams
        if self.player.team not in [self.match.team_a, self.match.team_b]:
            raise ValidationError("Player does not belong to this match teams")

        # 2️ Cannot modify lineup after match is LIVE
        if self.match.status != "SCHEDULED":
            raise ValidationError("Cannot modify lineup after match has started")

        # 3️ Maximum 9 PLAYING players per team
        if self.status == "PLAYING":

            playing_count = MatchPlayer.objects.filter(
                match=self.match,
                player__team=self.player.team,
                status="PLAYING"
            ).exclude(id=self.id).count()

            if playing_count >= 9:
                raise ValidationError("Maximum 9 playing players allowed per team")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.player} - {self.status}"
    
class MatchResult(models.Model):

    match = models.OneToOneField(
        "matches.Match",
        on_delete=models.CASCADE,
        related_name="result"
    )

    team_a_score = models.IntegerField()
    team_b_score = models.IntegerField()

    winner = models.ForeignKey(
        "teams.Team",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wins"
    )

    is_draw = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result - Match {self.match.match_number}"
