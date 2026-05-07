from django.db import models
from users.models import CustomUser
from game.core.events.models import GameEvent

class Choice(models.Model):
    event = models.ForeignKey(GameEvent, on_delete=models.CASCADE, related_name='available_choices')
    player = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    description = models.TextField()
    requirements = models.JSONField(default=dict)
    consequences = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Choice for {self.event} by {self.player}" 