from django.contrib import admin
from .models import GameSession, GameEvent

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('player', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('player__name', 'player__adventure__title')

@admin.register(GameEvent)
class GameEventAdmin(admin.ModelAdmin):
    list_display = ('player', 'adventure', 'location', 'timestamp')
    list_filter = ('adventure', 'location', 'timestamp')
    search_fields = ('player__name', 'adventure__title', 'description')
