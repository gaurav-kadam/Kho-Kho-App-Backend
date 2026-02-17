from django.db import models
from django.forms import ValidationError
from tournaments.models import Tournament
from teams.models import Team
from django.conf import settings
from django.core.exceptions import ValidationError

User = settings.AUTH_USER_MODEL


class Match(models.Model):

    MATCH_STATUS = [
        ('SCHEDULED', 'Scheduled'),
        ('LIVE', 'Live'),
        ('PAUSED', 'Paused'),
        ('COMPLETED', 'Completed'),
    ]

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='matches'
    )

    team_a = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='team_a_matches'
    )

    team_b = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='team_b_matches'
    )

    match_date = models.DateTimeField()
    venue = models.CharField(max_length=200)

    toss_winner = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='toss_wins'
    )

    status = models.CharField(
        max_length=20,
        choices=MATCH_STATUS,
        default='SCHEDULED'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)


    def clean(self):
        if self.team_a == self.team_b:
            raise ValidationError("Team A and Team B cannot be the same.")

    def __str__(self):
        return f"{self.team_a.name} vs {self.team_b.name}"

    court_no = models.IntegerField(null=True, blank=True)
    match_no = models.IntegerField(null=True, blank=True)

    AGE_GROUP_CHOICES = [
        ("U14", "Under 14"),
        ("U17", "Under 17"),
        ("U19", "Under 19"),
        ("OPEN", "Open"),
    ]

    age_group = models.CharField(
        max_length=20,
        choices=AGE_GROUP_CHOICES,
        null=True,
        blank=True
    )

    GENDER_CHOICES = [
        ("MALE", "Male"),
        ("FEMALE", "Female"),
    ]

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        null=True,
        blank=True
    )
    match_date = models.DateTimeField()
    venue = models.CharField(max_length=200)



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
        # Enforce max 2 umpires per match
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

    class Meta:
        unique_together = ("match", "player")

    def __str__(self):
        return f"{self.player} - {self.status}"

