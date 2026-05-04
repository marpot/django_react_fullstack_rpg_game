from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class PlayerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    level = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - Level {self.level}"


class PlayerCharacter(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="characters"
    )

    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)

    health = models.IntegerField(default=100)
    max_health = models.IntegerField(default=100)

    mana = models.IntegerField(default=100)
    max_mana = models.IntegerField(default=100)

    strength = models.IntegerField(default=10)
    dexterity = models.IntegerField(default=10)
    intelligence = models.IntegerField(default=10)

    current_location = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    adventure = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    stats = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return f"{self.name} (Level {self.level})"

    def gain_experience(self, amount: int) -> None:
        """
        Adds experience and handles level up.
        """
        self.experience += amount

        while self.experience >= self.required_experience():
            self.level_up()

        self.save()

    def required_experience(self) -> int:
        """
        Returns experience required for next level.
        """
        return self.level * 1000

    def level_up(self) -> None:
        """
        Handles leveling logic.
        """
        self.experience -= self.required_experience()
        self.level += 1

        self.max_health += 10
        self.max_mana += 10

        self.health = self.max_health
        self.mana = self.max_mana

        self.strength += 2
        self.dexterity += 2
        self.intelligence += 2