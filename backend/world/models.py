from django.db import models
from django.conf import settings

class Adventure(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="world"
        )

    def __str__(self):
        return self.title

class Location(models.Model):
    adventure = models.ForeignKey(
        Adventure,
        on_delete=models.CASCADE,
        related_name="locations",
        null=True,
        blank=True)

    title = models.CharField(max_length=255)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return(
            self.title
            if self.adventure is None
            else f"{self.adventure.title} - {self.title}"
        )
    class Meta:
        verbose_name_plural = "locations"
        ordering = ['order']

class Choice(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="choices",  verbose_name="Current location")
    title = models.CharField(max_length=255)
    description = models.TextField()
    next_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name="choices_leading_here", verbose_name="Next location")  # Opcjonalne przypisanie
    effects = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "choices"

class Enemy(models.Model):
    name = models.CharField(max_length=100)

    hp = models.IntegerField(default=30)
    defense = models.IntegerField(default=10)

    attack_bonus = models.IntegerField(default=2)
    damage_die = models.IntegerField(default=6)
    damage_bonus = models.IntegerField(default=1)

    adventure = models.ForeignKey(
        "world.Adventure",
        on_delete=models.CASCADE,
        related_name="enemies"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name