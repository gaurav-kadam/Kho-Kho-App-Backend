from django.contrib import admin
from .models import ScoreEvent
from .models import ScoreAuditLog

from django.contrib import admin
from .models import ScoreEvent, ScoreAuditLog


@admin.register(ScoreEvent)
class ScoreEventAdmin(admin.ModelAdmin):

    list_display = (
        "match",
        "event_type",
        "attacking_team",
        "defending_team",
        "player",
        "points",
        "timestamp",
    )

    list_filter = (
        "match",
        "event_type",
        "attacking_team",
        "defending_team",
    )

    search_fields = (
        "match__name",
        "attacking_team__name",
        "defending_team__name",
        "player__name",
    )

    ordering = ("-timestamp",)

    def save_model(self, request, obj, form, change):
        obj.full_clean()  
        super().save_model(request, obj, form, change)

@admin.register(ScoreAuditLog)
class ScoreAuditLogAdmin(admin.ModelAdmin):
    list_display = ('match', 'user', 'points', 'created_at')
    list_filter = ('match', 'user')
    search_fields = ('user__username',)
    readonly_fields = ('match', 'user', 'points', 'created_at')
    ordering = ('-created_at',)
