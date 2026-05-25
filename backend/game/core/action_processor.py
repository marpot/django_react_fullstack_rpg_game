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

        # runtime entities (game state)
        attacker_runtime = self.resolver.resolve_player(room, user_id)
        defender_runtime = self.resolver.resolve_enemy(room, enemy_name)

        if not attacker_runtime or not defender_runtime:
            logger.error("[COMBAT] Missing runtime entities")
            return {"error": "Missing combat entities"}

        # safety runtime checks
        if attacker_runtime.hp <= 0:
            logger.error("[COMBAT] Attacker already dead")
            return {"error": "Attacker dead"}

        if defender_runtime.hp <= 0:
            logger.error("[COMBAT] Defender already dead")
            return {"error": "Enemy already dead"}

        logger.info(
            f"[COMBAT] RUNTIME attacker_hp={attacker_runtime.hp} defender_hp={defender_runtime.hp}"
        )

        # combat resolution
        result = self.combat_service.resolve(attacker_runtime, defender_runtime)

        # sync enemy name with runtime (avoid mismatch)
        enemy_name = getattr(defender_runtime, "name", enemy_name)

        # ORM SAFE FETCH (NO CRASH)
        attacker_orm = PlayerCharacter.objects.filter(id=user_id).first()
        enemy_orm = Enemy.objects.filter(name=enemy_name).first()
        adventure = Adventure.objects.first()

        if not attacker_orm:
            logger.error(f"[COMBAT] Player not found id={user_id}")
            return {"error": "Player not found"}

        if not enemy_orm:
            logger.error(f"[COMBAT] Enemy not found name={enemy_name}")
            return {"error": "Enemy not found in DB"}

        if not adventure:
            logger.error("[COMBAT] Adventure missing")
            return {"error": "Adventure missing"}

        # event log
        self.event_service.create_event(
            adventure=adventure,
            player=attacker_orm,
            location=None,
            description=(
                f"[COMBAT] {attacker_orm.name} vs {enemy_name} | "
                f"winner={result.winner} | "
                f"dmg={result.attacker_damage}/{result.defender_damage}"
            ),
            event_type="combat",
            choices=[]
        )

        # persist state
        attacker_orm.health = attacker_runtime.hp
        attacker_orm.save(update_fields=["health"])

        enemy_orm.hp = defender_runtime.hp
        enemy_orm.save(update_fields=["hp"])

        logger.info(f"[COMBAT] END winner={result.winner}")

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