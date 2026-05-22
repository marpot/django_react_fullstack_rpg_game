from django.db import models
from accounts.models import PlayerCharacter

class GameSession(models.Model):
    player = models.ForeignKey(PlayerCharacter, on_delete=models.CASCADE, related_name="sessions")
    progress = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        """Returns a string representation of the game session."""
        return f"{self.player.name} - {self.player.adventure.title} (Session)"

class GameEvent(models.Model):
    class EventType(models.TextChoices):
        STORY = 'story', 'Story'
        CHOICE = 'choice', 'Choice'
        COMBAT = 'combat', 'Combat'
        ITEM = 'item', 'Item'
        STATUS = 'status', 'Status'
        QUEST = 'quest', 'Quest'
        SHOP = 'shop', 'Shop'
        TREASURE = 'treasure', 'Treasure'

    adventure = models.ForeignKey('world.Adventure', on_delete=models.CASCADE, related_name="game_events")
    player = models.ForeignKey(PlayerCharacter, on_delete=models.CASCADE, related_name="game_events")
    location = models.ForeignKey('world.Location', on_delete=models.SET_NULL, null=True, blank=True)

    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EventType.choices)

    timestamp = models.DateTimeField(auto_now_add=True)

    required_flags = models.JSONField(default=list, blank=True)
    blocking_flags = models.JSONField(default=list, blank=True)
    requirements = models.JSONField(default=dict, blank=True)

    event_data = models.JSONField(default=dict, blank=True)
    choices = models.JSONField(default=list, blank=True)
    consequences = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['adventure', 'timestamp']),
            models.Index(fields=['player', 'timestamp']),
        ]

class Flag(models.Model):
    adventure = models.ForeignKey('world.Adventure', on_delete=models.CASCADE)
    player = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    value = models.JSONField(default=dict)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('adventure', 'player', 'name')

    def __str__(self):
        return f"{self.name} ({self.player_id})"