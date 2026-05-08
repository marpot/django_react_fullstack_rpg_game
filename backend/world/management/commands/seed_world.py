from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from world.models import Adventure, Location


class Command(BaseCommand):
    help = "Seed initial RPG world data"

    def handle(self, *args, **options):
        self.stdout.write("🌍 Seeding world...")

        if Adventure.objects.exists():
            self.stdout.write("⚠️ World already seeded. Skipping.")
            return

        User = get_user_model()
        user, _ = User.objects.get_or_create(username="seed_user")

        adventure = Adventure.objects.create(
            title="Przygoda startowa",
            description="Seeded world adventure",
            creator=user
        )

        village = Location.objects.create(
            title="Wioska początkowa",
            description="Safe starting area",
            adventure=adventure,
            order=1
        )

        forest = Location.objects.create(
            title="Mroczny las",
            description="Niebezpieczne miejsce",
            adventure=adventure,
            order=2
        )

        dungeon = Location.objects.create(
            title="Starożytne Ruiny",
            description="End game test area",
            adventure=adventure,
            order=3
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"""
                ✅ Seed completed:
                - Adventure: {adventure.title}
                - Locations: {Location.objects.filter(adventure=adventure).count()}
                """
            )
        )