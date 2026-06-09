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

    # =========================
    # ENTRY POINT
    # =========================
    def process(self, parsed_input):
        print("PROCESS INPUT:", parsed_input)
        
        action = parsed_input.get("action")

        if action == "attack":
            return self._handle_attack(parsed_input)

        if action == "inspect":
            return self._handle_inspect(parsed_input)

        if action == "move":
            return self._handle_move(parsed_input)

        if action == "look":
            return self._handle_inspect(parsed_input)

        return {
            "action": action,
            "result": "Unhandled action",
        }

    # =========================
    # ATTACK 
    # =========================
    def _handle_attack(self, parsed_input):
        room = parsed_input.get("room")
        user_id = parsed_input.get("user_id")
        enemy_name = parsed_input.get("target")
        adventure_id = parsed_input.get("adventure")

        logger.info(f"[COMBAT] START room={room} user_id={user_id} enemy={enemy_name}")

        attacker_runtime = self.resolver.resolve_player(room, user_id)
        defender_runtime = self.resolver.resolve_enemy(room, enemy_name)

        if not attacker_runtime or not defender_runtime:
            return {
                "action": "attack",
                "error": "Missing combat entities",
            }

        result = self.combat_service.resolve(attacker_runtime, defender_runtime)

        # sync runtime state
        room_obj = self.state_manager.get_room(room)
        if room_obj and enemy_name in room_obj.enemies:
            room_obj.enemies[enemy_name].hp = defender_runtime.hp

        attacker_orm = PlayerCharacter.objects.filter(user_id=user_id).first()
        adventure = Adventure.objects.filter(id=adventure_id).first() if adventure_id else None

        enemy_orm = None
        if adventure:
            enemy_orm = EnemyORM.objects.filter(
                name=enemy_name,
                adventure=adventure
            ).first()

        if not attacker_orm:
            return {"action": "attack", "error": "Player not found"}

        if not adventure:
            return {"action": "attack", "error": "Adventure missing"}

        if not enemy_orm:
            return {"action": "attack", "error": "Enemy not found in DB"}

        self.event_service.create_event(
            adventure=adventure,
            player=attacker_orm,
            location=None,
            description=f"[COMBAT] {attacker_orm.name} vs {enemy_name}",
            event_type="combat",
            choices=[],
        )

        attacker_orm.health = attacker_runtime.hp
        attacker_orm.save(update_fields=["health"])

        enemy_orm.hp = defender_runtime.hp
        enemy_orm.save(update_fields=["hp"])

        return {
            "action": "attack",
            "result": {
                "attacker_hit": result.attacker_hit,
                "defender_hit": result.defender_hit,
                "attacker_damage": result.attacker_damage,
                "defender_damage": result.defender_damage,
                "winner": result.winner,
            },
        }

    # =========================
    # INSPECT (STUB)
    # =========================
    def _handle_inspect(self, parsed_input):
        return {
            "action": "inspect",
            "result": "Inspect not implemented yet"
        }

    # =========================
    # MOVE (STUB)
    # =========================
    def _handle_move(self, parsed_input):
        return {
            "action": "move",
            "result": "Move not implemented yet"
        }