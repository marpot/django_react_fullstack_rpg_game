from django.apps import AppConfig


class WorldConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "world"
    path = "/app/world"

    def ready(self):
        from world.seeders.adventure_seeder import seed_adventures

        try:
            seed_adventures()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[ADVENTURE SEED ERROR] {e}")