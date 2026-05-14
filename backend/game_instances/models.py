from django.db import models
from world.models import Adventure
from chat.models import Room

class AdventureInstance(models.Model):
    adventure = models.ForeignKey(
        Adventure,
        on_delete=models.CASCADE,
        related_name="instances"
    )

    room = models.OneToOneField(
        Room,
        on_delete=models.CASCADE,
        related_name="instance"
    )

    state = models.JSONField(default=dict)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.adventure.title} @ {self.room.name}"
    