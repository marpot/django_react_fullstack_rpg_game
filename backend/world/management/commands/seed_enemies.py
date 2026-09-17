from django.core.management.base import BaseCommand
from world.models import Enemy, Adventure

class Command(BaseCommand):
    def handle(self, *args, **options):
        adventure = Adventure.objects.first()

        if not adventure:
            raise Exception("No Adventure found - create one first")

        Enemy.objects.get_or_create(
            name="goblin",
            adventure=adventure,   # 🔥 DODAJ TO
            defaults={
                "hp": 20,
                "defense": 2,
            }
        )

        self.stdout.write(self.style.SUCCESS("Enemies seeded"))
