from django.db import models
from teams.models import Team


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

    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)

    jersey_number = models.IntegerField(null=True, blank=True)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        null=True,
        blank=True
    )

    date_of_birth = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
