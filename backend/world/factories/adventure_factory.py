import random
from world.models import Adventure, Location, Enemy
from django.contrib.auth import get_user_model

User = get_user_model()


ADVENTURE_TEMPLATES = [
    {
        "title": "Cienie {place}",
        "theme": "dark fantasy",
        "enemies": ["goblin", "wolf"],
        "locations": [
            "Wejście do {place}",
            "Ruiny {place}",
            "Serce {place}",
        ]
    },
    {
        "title": "Upadek {place}",
        "theme": "survival",
        "enemies": ["bandit", "wolf"],
        "locations": [
            "Granica {place}",
            "Opuszczona droga",
            "Fort ruin"
        ]
    }
]


PLACES = ["Eldorii", "Valemor", "Kragh Keep", "Blackwood"]


class AdventureFactory:

    @staticmethod
    def generate(creator, system_user=None):
        template = random.choice(ADVENTURE_TEMPLATES)
        place = random.choice(PLACES)

        adventure = Adventure.objects.create(
            title=template["title"].format(place=place),
            description=f"Procedural adventure in {place}",
            creator=creator or system_user
        )

        # LOCATIONS
        locations = []
        for i, loc in enumerate(template["locations"]):
            location = Location.objects.create(
                adventure=adventure,
                title=loc.format(place=place),
                description=f"Location {i+1} in {place}",
                order=i
            )
            locations.append(location)

        # ENEMIES
        for enemy_name in template["enemies"]:
            Enemy.objects.create(
                name=enemy_name,
                hp=random.randint(15, 40),
                defense=random.randint(8, 14),
                attack_bonus=random.randint(1, 4),
                damage_die=6,
                damage_bonus=random.randint(0, 2),
                adventure=adventure
            )

        return adventure