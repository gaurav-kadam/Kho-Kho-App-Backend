# teams/models.py

from django.db import models
from django.core.exceptions import ValidationError
from tournaments.models import Tournament


class Team(models.Model):

    GENDER_CHOICES = [
        ("MEN", "Men"),
        ("WOMEN", "Women"),
    ]

    AGE_GROUP_CHOICES = [
        ("U14", "Under 14"),
        ("U17", "Under 17"),
        ("U19", "Under 19"),
        ("SENIOR", "Senior"),
    ]

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name="teams"
    )

    name = models.CharField(max_length=150)

    short_name = models.CharField(max_length=20)

    color = models.CharField(max_length=50)

    state = models.CharField(max_length=100)

    city = models.CharField(max_length=100)

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    age_group = models.CharField(
        max_length=20,
        choices=AGE_GROUP_CHOICES
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tournament", "name")
        ordering = ["name"]

    def clean(self):

        # 1️ Team name uniqueness inside tournament
        if Team.objects.filter(
            tournament=self.tournament,
            name__iexact=self.name
        ).exclude(id=self.id).exists():
            raise ValidationError("Team name already exists in this tournament.")

        # 2️ Short name uniqueness
        if Team.objects.filter(
            tournament=self.tournament,
            short_name__iexact=self.short_name
        ).exclude(id=self.id).exists():
            raise ValidationError("Team short name already exists.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.tournament.name})"
