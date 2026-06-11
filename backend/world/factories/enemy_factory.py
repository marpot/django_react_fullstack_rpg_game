import random
from world.models import Enemy


ENEMY_TEMPLATES = [
    {
        "name": "goblin",
        "hp": (15, 30),
        "defense": (8, 12),
        "attack_bonus": (1, 3),
        "damage_die": 6,
        "damage_bonus": (0, 2),
    },
    {
        "name": "bandit",
        "hp": (20, 40),
        "defense": (10, 14),
        "attack_bonus": (2, 4),
        "damage_die": 6,
        "damage_bonus": (1, 3),
    },
    {
        "name": "wolf",
        "hp": (10, 25),
        "defense": (9, 13),
        "attack_bonus": (2, 5),
        "damage_die": 4,
        "damage_bonus": (1, 2),
    },
]


class EnemyFactory:

    @staticmethod
    def generate_for_adventure(adventure, count=3):
        enemies = []

        for _ in range(count):
            tpl = random.choice(ENEMY_TEMPLATES)

            enemy = Enemy.objects.create(
                name=tpl["name"],
                hp=random.randint(*tpl["hp"]),
                defense=random.randint(*tpl["defense"]),
                attack_bonus=random.randint(*tpl["attack_bonus"]),
                damage_die=tpl["damage_die"],
                damage_bonus=random.randint(*tpl["damage_bonus"]),
                adventure=adventure,
            )

            enemies.append(enemy)

        return enemies