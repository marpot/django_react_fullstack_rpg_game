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

class RoomParticipant(models.Model):
    room = models.ForeignKey("Room", on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    character = models.ForeignKey(
        "accounts.PlayerCharacter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="room_participations",
    )

    name = models.CharField(max_length=255)
    is_ai = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("room", "user")

    def __str__(self):
        return f"{self.name} ({'AI' if self.is_ai else 'HUMAN'})"