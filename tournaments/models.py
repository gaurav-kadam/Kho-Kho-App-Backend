# tournaments/models.py

from django.db import models
from django.core.exceptions import ValidationError
from datetime import date


class Tournament(models.Model):

    GENDER_CHOICES = [
        ("MEN", "Men"),
        ("WOMEN", "Women"),
    ]

    STATUS_CHOICES = [
        ("UPCOMING", "Upcoming"),
        ("ONGOING", "Ongoing"),
        ("COMPLETED", "Completed"),
    ]

    AGE_GROUP_CHOICES = [
        ("U14", "Under 14"),
        ("U16", "Under 16"),
        ("U18", "Under 18"),
        ("OPEN", "Open"),
    ]

    FORMAT_CHOICES = [
        ("LEAGUE", "League"),
        ("KNOCKOUT", "Knockout"),
        ("ROUND_ROBIN", "Round Robin"),
    ]

    name = models.CharField(max_length=200, unique=True)
    location = models.CharField(max_length=200)

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    age_group = models.CharField(
        max_length=10,
        choices=AGE_GROUP_CHOICES,
        default="OPEN"
    )

    format_type = models.CharField(
        max_length=20,
        choices=FORMAT_CHOICES,
        default="LEAGUE"
    )

    max_time_per_turn = models.PositiveIntegerField(
        help_text="Time per turn in seconds",
        default=30
    )

    max_teams = models.PositiveIntegerField(default=16)

    start_date = models.DateField()
    end_date = models.DateField()

    organizer = models.CharField(max_length=200)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="UPCOMING"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date.")

    def save(self, *args, **kwargs):
        today = date.today()
        if today < self.start_date:
            self.status = "UPCOMING"
        elif self.start_date <= today <= self.end_date:
            self.status = "ONGOING"
        else:
            self.status = "COMPLETED"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.age_group} - {self.gender})"
