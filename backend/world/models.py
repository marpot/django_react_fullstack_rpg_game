from django.db import models
from django.conf import settings

class Adventure(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="world")
    locations = models.ManyToManyField('Location', related_name='world', blank=True)  # Opcjonalne przypisanie lokalizacji
    def __str__(self):
        return self.title

class Location(models.Model):
    adventure = models.ForeignKey(Adventure, on_delete=models.CASCADE, null=True, blank=True)  # Przygoda opcjonalna
    title = models.CharField(max_length=255)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title if self.adventure is None else f"{self.adventure.title} - {self.title}"

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
