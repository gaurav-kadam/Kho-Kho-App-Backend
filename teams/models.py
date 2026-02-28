# teams/models.py
from django.db import models
from django.core.exceptions import ValidationError
from tournaments.models import Tournament
from django.conf import settings

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

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("DISQUALIFIED", "Disqualified"),
        ("WITHDRAWN", "Withdrawn"),
    ]

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name="teams",
        db_index=True
    )
    name = models.CharField(max_length=150, db_index=True)
    short_name = models.CharField(max_length=20)
    color = models.CharField(max_length=50)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    age_group = models.CharField(max_length=20, choices=AGE_GROUP_CHOICES)
    
    # New professional fields
    logo = models.ImageField(upload_to='team_logos/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")
    captain_name = models.CharField(max_length=200, blank=True)
    coach_name = models.CharField(max_length=200, blank=True)
    coach_contact = models.CharField(max_length=15, blank=True)
    
    # Statistics (cached for performance)
    matches_played = models.PositiveIntegerField(default=0)
    matches_won = models.PositiveIntegerField(default=0)
    matches_lost = models.PositiveIntegerField(default=0)
    matches_drawn = models.PositiveIntegerField(default=0)
    total_points = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_teams'
    )

    class Meta:
        unique_together = ("tournament", "name")
        ordering = ["-total_points", "name"]
        indexes = [
            models.Index(fields=['tournament', 'status']),
            models.Index(fields=['total_points']),
        ]

    def clean(self):
        if Team.objects.filter(
            tournament=self.tournament,
            name__iexact=self.name
        ).exclude(id=self.id).exists():
            raise ValidationError("Team name already exists in this tournament.")

        if Team.objects.filter(
            tournament=self.tournament,
            short_name__iexact=self.short_name
        ).exclude(id=self.id).exists():
            raise ValidationError("Team short name already exists.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def update_statistics(self):
        """Update team statistics from match results"""
        from matches.models import MatchResult
        from django.db.models import Q
        
        results = MatchResult.objects.filter(
            Q(match__team_a=self) | Q(match__team_b=self)
        )
        
        self.matches_played = results.count()
        self.matches_won = results.filter(winner=self).count()
        self.matches_drawn = results.filter(is_draw=True).count()
        self.matches_lost = self.matches_played - self.matches_won - self.matches_drawn
        self.total_points = (self.matches_won * 2) + self.matches_drawn
        
        self.save(update_fields=[
            'matches_played', 'matches_won', 'matches_lost',
            'matches_drawn', 'total_points'
        ])

    def __str__(self):
        return f"{self.name} ({self.tournament.name})"