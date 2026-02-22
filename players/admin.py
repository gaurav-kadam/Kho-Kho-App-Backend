from django.contrib import admin
from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):

    list_display = (
        "first_name",
        "last_name",
        "team",
        "jersey_number",
        "role",
        "is_active",
    )

    list_filter = (
        "role",
        "is_active",
        "team",
    )

    search_fields = (
        "first_name",
        "last_name",
        "jersey_number",
    )

    readonly_fields = ("created_at",)

    fieldsets = (
        ("Personal Information", {
            "fields": (
                "team",
                "first_name",
                "last_name",
                "date_of_birth",
            )
        }),
        ("Game Details", {
            "fields": (
                "jersey_number",
                "role",
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
