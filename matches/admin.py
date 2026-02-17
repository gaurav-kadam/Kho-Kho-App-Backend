from django.contrib import admin
from .models import Match
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from .models import MatchOfficial, MatchStaff, MatchPlayer


class MatchAdminForm(ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        team_a = cleaned_data.get("team_a")
        team_b = cleaned_data.get("team_b")

        if team_a and team_b and team_a == team_b:
            raise ValidationError("Team A and Team B must be different.")

        return cleaned_data

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    form = MatchAdminForm
    list_display = ('id','tournament', 'team_a', 'team_b', 'status', 'match_date')
    list_filter = ('status', 'tournament')
    readonly_fields = ('status',)

@admin.register(MatchOfficial)
class MatchOfficialAdmin(admin.ModelAdmin):
    list_display = ("match", "user", "role")
    list_filter = ("role", "match")
    search_fields = ("user__username",)


@admin.register(MatchStaff)
class MatchStaffAdmin(admin.ModelAdmin):
    list_display = ("match", "user", "role")
    list_filter = ("role", "match")


@admin.register(MatchPlayer)
class MatchPlayerAdmin(admin.ModelAdmin):
    list_display = ("match", "player", "status")
    list_filter = ("status", "match")
