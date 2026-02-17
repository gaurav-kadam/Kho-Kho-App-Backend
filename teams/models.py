from django.db import models
from tournaments.models import Tournament

class Team(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='teams'
    )

    name = models.CharField(max_length=150)
    gender = models.CharField(
        max_length=10,
        choices=[
            ('MEN', 'Men'),
            ('WOMEN', 'Women')
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.tournament.name})"
