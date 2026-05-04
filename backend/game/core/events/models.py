from django.db import models
from users.models import CustomUser
from world.models import Adventure, Location

class GameEvent(models.Model):
    EVENT_TYPES = [
        ('STORY', 'Story Event'),
        ('BATTLE', 'Battle Event'),
        ('QUEST', 'Quest Event'),
        ('SHOP', 'Shop Event'),
        ('TREASURE', 'Treasure Event'),
    ]

    adventure = models.ForeignKey(Adventure, on_delete=models.CASCADE)
    player = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    choices = models.JSONField(default=list)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} at {self.location} for {self.player}" 