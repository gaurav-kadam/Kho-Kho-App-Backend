from django.contrib import admin
from .models import Team
from players.models import Player


class PlayerInline(admin.TabularInline):
    model = Player
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "tournament",
        "player_count",
        "created_at",
    )

    list_filter = (
        "tournament",
    )

    search_fields = (
        "name",
        "tournament__name",
    )

    readonly_fields = ("created_at",)

    inlines = [PlayerInline]

    fieldsets = (
        ("Team Information", {
            "fields": (
                "tournament",
                "name",
            )
        }),
        ("System Information", {
            "fields": ("created_at",)
        }),
    )

    def player_count(self, obj):
        return obj.players.count()
    player_count.short_description = "Total Players"
