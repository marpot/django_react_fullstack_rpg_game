import random
from django.db import transaction
from django.contrib.auth import get_user_model
from game.domain.generated_adventure import validate_generated_adventure
from world.models import Adventure, Choice, Location, Enemy

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
    def create_from_spec(creator, spec):
        validate_generated_adventure(spec)

        with transaction.atomic():
            adventure = Adventure.objects.create(
                title=spec.title,
                description=spec.description,
                creator=creator,
            )

            locations = {
                location_spec.key: Location.objects.create(
                    adventure=adventure,
                    title=location_spec.title,
                    description=location_spec.description,
                    order=order,
                )
                for order, location_spec in enumerate(spec.locations)
            }

            for choice_spec in spec.choices:
                Choice.objects.create(
                    location=locations[choice_spec.from_location],
                    next_location=locations[choice_spec.to_location],
                    title=choice_spec.title,
                    description=choice_spec.description,
                )

            enemy_locations = {}
            for enemy_spec in spec.enemies:
                enemy = Enemy.objects.create(
                    name=enemy_spec.name,
                    hp=enemy_spec.hp,
                    defense=enemy_spec.defense,
                    attack_bonus=enemy_spec.attack_bonus,
                    damage_die=enemy_spec.damage_die,
                    damage_bonus=enemy_spec.damage_bonus,
                    adventure=adventure,
                )
                enemy_locations[str(enemy.id)] = locations[
                    enemy_spec.location
                ].id

            adventure.generated_scenario = {
                "start_location_id": locations[spec.start_location].id,
                "enemy_locations": enemy_locations,
                "npcs": [
                    {
                        "id": npc.key,
                        "name": npc.name,
                        "role": npc.role,
                        "location_id": locations[npc.location].id,
                    }
                    for npc in spec.npcs
                ],
                "progression": [
                    {
                        "stage": step.stage,
                        "trigger": step.trigger,
                        "objective": step.objective,
                        "next_stage": step.next_stage,
                    }
                    for step in spec.progression
                ],
            }
            adventure.save(update_fields=["generated_scenario"])

        return adventure

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
