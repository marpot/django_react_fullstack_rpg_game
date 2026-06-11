from world.models import Enemy
from game.state.runtime.models import Enemy as RuntimeEnemy
import logging

logger = logging.getLogger(__name__)


class WorldSeeder:
    def __init__(self, state_manager):
        self.state = state_manager

    def seed_from_adventure(self, adventure_id, room_id):
        logger.info("================================")
        logger.info("WORLD SEED START")
        logger.info(f"adventure_id={adventure_id} room_id={room_id}")

        enemies = Enemy.objects.filter(adventure__id=adventure_id)
        logger.info(f"[SEED] filtered enemies count: {enemies.count()}")

        room = self.state.get_or_create_room(room_id)

        logger.info(f"[SEED] room ready: {room_id}")

        # RESET STATE
        room.enemies = {}
        logger.info("[SEED] room enemies reset")

        # SEED ENEMIES
        for e in enemies:
            logger.info(f"[SEED] loading enemy: {e.name}")

            enemy_runtime = RuntimeEnemy(
                id=e.name,
                name=e.name,
                hp=e.hp,
                defense=e.defense,
                attack_bonus=e.attack_bonus,
                damage_die=getattr(e, "damage_die", 6),
                damage_bonus=getattr(e, "damage_bonus", 0),
            )

            enemy_key = e.name.lower().strip()
            room.enemies[enemy_key] = enemy_runtime

            if e.name != enemy_key:
                room.enemies[e.name] = enemy_runtime

        logger.info(f"[SEED] FINAL ENEMIES: {list(room.enemies.keys())}")
        logger.info("WORLD SEED END")
        logger.info("================================")