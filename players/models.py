# players/models.py

from django.db import models
from django.core.exceptions import ValidationError
from teams.models import Team
from datetime import date


class Player(models.Model):

    ROLE_CHOICES = [
        ("RAIDER", "Raider"),
        ("DEFENDER", "Defender"),
        ("ALL_ROUNDER", "All Rounder"),
    ]

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="players"
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    jersey_number = models.PositiveIntegerField()

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    date_of_birth = models.DateField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("team", "jersey_number")

    def clean(self):

        # Maximum 15 players per team
        if self.team.players.exclude(id=self.id).count() >= 15:
            raise ValidationError("Maximum 15 players allowed per team.")

        # Age validation based on tournament age group
        today = date.today()
        age = today.year - self.date_of_birth.year - (
            (today.month, today.day) <
            (self.date_of_birth.month, self.date_of_birth.day)
        )

        age_group = self.team.tournament.age_group

        if age_group == "U14" and age > 14:
            raise ValidationError("Player exceeds age limit for U14.")

        if age_group == "U16" and age > 16:
            raise ValidationError("Player exceeds age limit for U16.")

        if age_group == "U18" and age > 18:
            raise ValidationError("Player exceeds age limit for U18.")

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name()
