from django.contrib import admin
from .models import Team

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'gender', 'tournament')
    list_filter = ('gender', 'tournament')
