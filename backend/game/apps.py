from django.apps import AppConfig
import os


class GameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'game'
    label = 'game'
    path = '/app/game'
