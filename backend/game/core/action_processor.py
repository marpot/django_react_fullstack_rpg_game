from game.services.combat_service import CombatService
from game.services.dice_service import DiceService
from game.state.resolver.entity_resolver import EntityResolver
from game.services.event_service import GameEventService

from accounts.models import PlayerCharacter
from world.models import Enemy, Adventure

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
            return {"action": action, "result": "Unhandled action"}

        room = parsed_input.get("room", "testroom")
        user_id = parsed_input.get("user_id")
        enemy_name = parsed_input.get("target")

        logger.info(f"[COMBAT] START room={room} user_id={user_id} enemy={enemy_name}")

        attacker_runtime = self.resolver.resolve_player(room, user_id)
        defender_runtime = self.resolver.resolve_enemy(room, enemy_name)

        if not attacker_runtime or not defender_runtime:
            return {"error": "Missing combat entities"}

        result = self.combat_service.resolve(attacker_runtime, defender_runtime)

        enemy_name = getattr(defender_runtime, "name", enemy_name)

        attacker_orm = PlayerCharacter.objects.filter(user_id=user_id).first()

        # ✅ FIX: adventure_id -> object
        adventure_id = parsed_input.get("adventure")
        adventure = Adventure.objects.filter(id=adventure_id).first()

        enemy_orm = Enemy.objects.filter(
            name=enemy_name,
            adventure=adventure
        ).first() if adventure else None

        if not attacker_orm:
            return {"error": "Player not found"}

        if not enemy_orm:
            return {"error": "Enemy not found in DB"}

        if not adventure:
            return {"error": "Adventure missing"}

        self.event_service.create_event(
            adventure=adventure,
            player=attacker_orm,
            location=None,
            description=f"[COMBAT] {attacker_orm.name} vs {enemy_name}",
            event_type="combat",
            choices=[]
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
            }
        }