from world.models import Enemy
from game.state.runtime.models import Enemy as RuntimeEnemy


class WorldSeeder:
    def __init__(self, state_manager):
        self.state = state_manager

    def seed_from_adventure(self, adventure_id, room_id):
        print("\n================ WORLD SEED START ================")
        print(f"[SEED] adventure_id={adventure_id} room_id={room_id}")

        # 🔥 DEBUG: podstawowy stan DB
        total_enemies = Enemy.objects.count()
        print(f"[SEED] total enemies in DB: {total_enemies}")

        # 🔥 DEBUG: wszystko co istnieje w DB
        all_enemies = list(Enemy.objects.all().values(
            "id", "name", "hp", "adventure_id"
        ))
        print(f"[SEED] all enemies: {all_enemies}")

        # 🔥 filtr dla konkretnej przygody
        enemies = Enemy.objects.filter(adventure_id=adventure_id)
        print(f"[SEED] filtered enemies count: {enemies.count()}")
        print(f"[SEED] filtered enemies: {[e.name for e in enemies]}")

        # 🔥 runtime room
        room = self.state.get_or_create_room(room_id)

        # opcjonalnie reset (ważne przy re-seedach)
        room.enemies = {}

        # 🔥 seed runtime
        for e in enemies:
            print(f"[SEED] loading enemy: {e.name}")

            room.enemies[e.name] = RuntimeEnemy(
                id=e.name,
                name=e.name,
                hp=e.hp,
                defense=e.defense,
                attack_bonus=e.attack_bonus,
                damage_die=getattr(e, "damage_die", 6),
                damage_bonus=getattr(e, "damage_bonus", 0),
            )

        print(f"[SEED] FINAL ROOM ENEMIES: {list(room.enemies.keys())}")
        print("================ WORLD SEED END ================\n")