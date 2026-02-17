from django.contrib import admin
from .models import Player

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id','first_name', 'last_name', 'team', 'jersey_number', 'role', 'is_active')
    list_filter = ('team', 'role', 'is_active')
    search_fields = ('name',)
