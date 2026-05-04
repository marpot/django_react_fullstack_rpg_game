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
    EVENT_TYPES = [
        ('story', 'Story'),
        ('choice', 'Choice'),
        ('combat', 'Combat'),
        ('item', 'Item'),
        ('status', 'Status'),
        ('quest', 'Quest'),
        ('shop', 'Shop'),
        ('treasure', 'Treasure'),
    ]

    # Basic fields
    adventure = models.ForeignKey('world.Adventure', on_delete=models.CASCADE, related_name="game_events")
    player = models.ForeignKey(PlayerCharacter, on_delete=models.CASCADE, related_name="game_events")
    location = models.ForeignKey('world.Location', on_delete=models.SET_NULL, null=True, blank=True, related_name="game_events")
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='story')
    timestamp = models.DateTimeField(auto_now_add=True)

    # Requirements and flags
    required_flags = models.JSONField(default=list, blank=True)  # Flags required to activate the event
    blocking_flags = models.JSONField(default=list, blank=True)  # Flags blocking the event
    requirements = models.JSONField(default=dict, blank=True)  # Requirements to activate the event (level, items, skills)

    # Event data and choices
    event_data = models.JSONField(default=dict, blank=True)  # Specific data for the event type
    choices = models.JSONField(default=list, blank=True)  # List of available choices
    consequences = models.JSONField(default=dict, blank=True)  # Consequences of choices

    def __str__(self):
        """Returns a string representation of the game event."""
        return f"{self.player.name} - {self.description} ({self.timestamp})"

    def is_available(self, player):
        """
        Checks if the event is available for the player.
        """
        # Check required flags
        for flag in self.required_flags:
            if flag not in player.flags:
                return False

        # Check blocking flags
        for flag in self.blocking_flags:
            if flag in player.flags:
                return False

        # Check requirements
        if self.requirements:
            if player.level < self.requirements.get('min_level', 0):
                return False
            
            for item in self.requirements.get('required_items', []):
                if item not in player.inventory:
                    return False
            
            for skill in self.requirements.get('required_skills', []):
                if skill not in player.skills:
                    return False

        return True

    def get_available_choices(self, player):
        """
        Returns a list of available choices for the player.
        """
        available_choices = []
        for choice in self.choices:
            if self._is_choice_available(choice, player):
                available_choices.append(choice)
        return available_choices

    def _is_choice_available(self, choice, player):
        """
        Checks if a choice is available for the player.
        """
        requirements = choice.get('requirements', {})
        
        # Check level
        if player.level < requirements.get('min_level', 0):
            return False
        
        # Check items
        for item in requirements.get('required_items', []):
            if item not in player.inventory:
                return False
        
        # Check skills
        for skill in requirements.get('required_skills', []):
            if skill not in player.skills:
                return False
        
        # Check flags
        for flag in requirements.get('required_flags', []):
            if flag not in player.flags:
                return False
        
        return True