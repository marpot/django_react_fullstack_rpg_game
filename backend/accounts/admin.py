from django.contrib import admin
from .models import PlayerCharacter


@admin.action(description="Activate selected characters")
def activate(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="Deactivate selected characters")
def deactivate(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.register(PlayerCharacter)
class PlayerCharacterAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'user',
        'adventure',
        'level',
        'health',
        'mana',
        'is_active',
        'created_at',
        'updated_at'
    )

    list_filter = ('level', 'is_active')
    search_fields = ('name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')

    actions = [activate, deactivate]