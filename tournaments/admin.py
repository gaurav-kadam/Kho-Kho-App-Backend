from django.contrib import admin
from .models import Tournament

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'location', 'start_date', 'end_date', 'is_active')
