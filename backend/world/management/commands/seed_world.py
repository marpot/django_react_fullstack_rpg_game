from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from world.models import Adventure, Choice, Enemy, Location


class Command(BaseCommand):
    help = "Seed initial RPG world data"

    def handle(self, *args, **options):
        self.stdout.write("🌍 Seeding world...")

        User = get_user_model()
        user, _ = User.objects.get_or_create(username="seed_user")

        adventure, _ = Adventure.objects.get_or_create(
            title="Przygoda startowa",
            creator=user,
            defaults={"description": "Seeded world adventure"},
        )

        village, _ = Location.objects.get_or_create(
            title="Wioska początkowa",
            adventure=adventure,
            defaults={"description": "Safe starting area", "order": 1},
        )

        forest, _ = Location.objects.get_or_create(
            title="Mroczny las",
            adventure=adventure,
            defaults={"description": "Niebezpieczne miejsce", "order": 2},
        )

        dungeon, _ = Location.objects.get_or_create(
            title="Starożytne Ruiny",
            adventure=adventure,
            defaults={"description": "End game test area", "order": 3},
        )

        for source, destination in (
            (village, forest), (forest, village),
            (forest, dungeon), (dungeon, forest),
        ):
            Choice.objects.get_or_create(
                location=source,
                next_location=destination,
                defaults={
                    "title": f"Idź do {destination.title}",
                    "description": f"Przejdź do {destination.title}.",
                },
            )

        Enemy.objects.get_or_create(
            adventure=adventure,
            name="goblin",
            defaults={"hp": 20, "defense": 2},
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
