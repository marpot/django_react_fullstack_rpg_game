from django.db import models
from django.conf import settings
from world.models import Adventure

class Room(models.Model):
    STATE_CHOICES = [
        ("lobby", "Lobby"),
        ("in_game", "In Game"),
    ]

    name = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    adventure = models.ForeignKey(Adventure, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    state = models.CharField(max_length=20, choices=STATE_CHOICES, default="lobby")

    def __str__(self):
        return self.name