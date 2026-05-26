from game.services.combat_service import CombatService
from game.services.dice_service import DiceService
from game.state.resolver.entity_resolver import EntityResolver
from game.services.event_service import GameEventService

from accounts.models import PlayerCharacter
from world.models import Enemy as EnemyORM, Adventure

import logging

logger = logging.getLogger(__name__)


class ActionProcessor:
    def __init__(self, state_manager, combat_service=None, resolver=None):
        self.state_manager = state_manager
        self.combat_service = combat_service or CombatService(DiceService())
        self.resolver = resolver or EntityResolver(state_manager)
        self.event_service = GameEventService()

    def process(self, parsed_input):
        action = parsed_input.get("action")

        if action != "attack":
            return {
                "action": action,
                "result": "Unhandled action",
            }

        room = parsed_input.get("room")
        user_id = parsed_input.get("user_id")
        enemy_name = parsed_input.get("target")
        adventure_id = parsed_input.get("adventure")

        logger.info(f"[COMBAT] START room={room} user_id={user_id} enemy={enemy_name}")

        # 1. runtime (SOURCE OF TRUTH dla walki)
        attacker_runtime = self.resolver.resolve_player(room, user_id)
        defender_runtime = self.resolver.resolve_enemy(room, enemy_name)

        if not attacker_runtime or not defender_runtime:
            return {
                "action": action,
                "error": "Missing combat entities",
            }

        # 2. combat resolution
        result = self.combat_service.resolve(attacker_runtime, defender_runtime)

        # 🔥 FIX: sync runtime state back to GameStateManager (TEST DEPENDENT)
        room_obj = self.state_manager.get_room(room)
        if room_obj and enemy_name in room_obj.enemies:
            room_obj.enemies[enemy_name].hp = defender_runtime.hp

        # 3. ORM lookup
        attacker_orm = PlayerCharacter.objects.filter(user_id=user_id).first()

        adventure = None
        if adventure_id:
            adventure = Adventure.objects.filter(id=adventure_id).first()

        enemy_orm = None
        if adventure:
            enemy_orm = EnemyORM.objects.filter(
                name=enemy_name,
                adventure=adventure
            ).first()

        # 4. validations
        if not attacker_orm:
            return {
                "action": action,
                "error": "Player not found",
            }

        if not adventure:
            return {
                "action": action,
                "error": "Adventure missing",
            }

        if not enemy_orm:
            return {
                "action": action,
                "error": "Enemy not found in DB",
            }

        # 5. event log
        self.event_service.create_event(
            adventure=adventure,
            player=attacker_orm,
            location=None,
            description=f"[COMBAT] {attacker_orm.name} vs {enemy_name}",
            event_type="combat",
            choices=[],
        )

        # 6. persist runtime -> ORM
        attacker_orm.health = attacker_runtime.hp
        attacker_orm.save(update_fields=["health"])

        enemy_orm.hp = defender_runtime.hp
        enemy_orm.save(update_fields=["hp"])

        # 7. response contract
        return {
            "action": action,
            "result": {
                "attacker_hit": result.attacker_hit,
                "defender_hit": result.defender_hit,
                "attacker_damage": result.attacker_damage,
                "defender_damage": result.defender_damage,
                "winner": result.winner,
            },
        }