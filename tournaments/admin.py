from django.contrib import admin
from .models import Tournament


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "gender",
        "age_group",
        "format_type",
        "status",
        "start_date",
        "end_date",
        "is_active",
    )

    list_filter = (
        "gender",
        "age_group",
        "status",
        "is_active",
    )

    search_fields = ("name", "location", "organizer")

    readonly_fields = ("created_at",)

    fieldsets = (
        ("Basic Information", {
            "fields": (
                "name",
                "location",
                "organizer",
            )
        }),
        ("Competition Settings", {
            "fields": (
                "gender",
                "age_group",
                "format_type",
                "max_time_per_turn",
                "max_teams",
            )
        }),
        ("Schedule", {
            "fields": (
                "start_date",
                "end_date",
                "status",
                "is_active",
            )
        }),
        ("System", {
            "fields": ("created_at",)
        }),
    )
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)