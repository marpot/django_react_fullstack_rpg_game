from django.db import models
from users.models import CustomUser
from world.models import Adventure

class Flag(models.Model):
    adventure = models.ForeignKey(Adventure, on_delete=models.CASCADE)
    player = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('adventure', 'player', 'name')

    def __str__(self):
        return f"{self.name} for {self.player} in {self.adventure}" 