from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import PlayerCharacter
from .models import PlayerProfile

User = get_user_model()

@admin.register(PlayerCharacter)
class PlayerCharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'adventure', 'level', 'health', 'mana')
    list_filter = ('level', 'is_active')
    search_fields = ('name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
