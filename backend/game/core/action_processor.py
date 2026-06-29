import logging

from game.services.combat_service import CombatService
from game.services.dice_service import DiceService
from game.state.resolver.entity_resolver import EntityResolver
from game.state.runtime.runtime_player_service import RuntimePlayerService
from game_instances.services.llm.orchestrator.llm_service import LLMService
from game.npc.npc_service import NPCService

logger = logging.getLogger(__name__)


class ActionProcessor:
    def __init__(self, state_manager, combat_service=None, resolver=None):
        self.state_manager = state_manager
        self.combat_service = combat_service or CombatService(DiceService())
        self.resolver = resolver or EntityResolver(state_manager)
        self.runtime_player_service = RuntimePlayerService(state_manager)

    def _narrate(self, action: str, result: dict, world: dict | None = None):
        llm = LLMService()
        return llm.generate_event_narration({
            "event_type": action,
            "result": result,
            "world": world or {}
        })

    def process(self, parsed_input):
        logger.info(f"[ACTION PROCESS] input={parsed_input}")

        action = parsed_input.get("action")
        world = parsed_input.get("world")

        logger.info(f"[ACTION PROCESS] action={action}")

        if parsed_input.get("error") == "unknown_intent_fallback":
            return self._handle_inspect(parsed_input)

        if not action or action == "unknown":
            return self._handle_inspect(parsed_input)

        if action == "attack":
            return self._handle_attack(parsed_input, world)

        if action == "inspect":
            return self._handle_inspect(parsed_input, world)

        if action == "move":
            return self._handle_move(parsed_input, world)

        if action == "look":
            return self._handle_inspect(parsed_input, world)

        if action == "talk":
            return NPCService(self.state_manager).talk(
                parsed_input["room"],
                parsed_input["target"]
            )

        return {"action": action, "result": "Unhandled action"}

    # -------------------------
    # ATTACK
    # -------------------------
    def _handle_attack(self, parsed_input, world=None):
        room = parsed_input.get("room")
        user_id = parsed_input.get("user_id")
        enemy_name = parsed_input.get("target")

        if isinstance(enemy_name, str):
            enemy_name = enemy_name.lower().strip().rstrip(".,!?")
        else:
            enemy_name = None

        room_key = self.state_manager.normalize_room_id(room)
        room_obj = self.state_manager.get_or_create_room(room_key)

        attacker_runtime = self.runtime_player_service.get_or_create(
            room_obj,
            user_id
        )

        if not attacker_runtime:
            return {"action": "attack", "text": "Brak postaci"}

        defender_runtime = self.resolver.resolve_enemy(room_key, enemy_name)

        if not defender_runtime:
            logger.warning(f"[ACTION PROCESS] enemy not found: {enemy_name} in room {room_key}")

            return {
                "action": "attack",
                "text": f"Nie znaleziono przeciwnika: {enemy_name}",
                "result": {
                    "error": "enemy_not_found",
                    "target": enemy_name
                }
            }

        result = self.combat_service.resolve(attacker_runtime, defender_runtime)

        narration = self._narrate("attack", {
            "attacker_hit": result.attacker_hit,
            "defender_hit": result.defender_hit,
            "attacker_damage": result.attacker_damage,
            "defender_damage": result.defender_damage,
            "winner": result.winner,
        }, world)

        return {
            "action": "attack",
            "text": narration.get("text", "Walka zakończona"),
            "result": {
                "winner": result.winner,
                "attacker_damage": result.attacker_damage,
                "defender_damage": result.defender_damage,
            },
        }

    # -------------------------
    # INSPECT
    # -------------------------
    def _handle_inspect(self, parsed_input, world=None):
        room = parsed_input.get("room")
        user_id = parsed_input.get("user_id")

        room_key = self.state_manager.normalize_room_id(room)
        room_obj = self.state_manager.get_or_create_room(room_key)

        self.runtime_player_service.get_or_create(room_obj, user_id)
        enemies = list(room_obj.enemies.keys())

        narration = self._narrate("inspect", {
            "room": room_key,
            "enemies": enemies
        }, world)

        return {
            "action": "inspect",
            "text": narration.get("text", "Rozglądasz się po okolicy"),
            "result": {
                "room": room_key,
                "enemies": enemies,
            }
        }

    # -------------------------
    # MOVE
    # -------------------------
    def _handle_move(self, parsed_input, world=None):
        room = parsed_input.get("room")
        user_id = parsed_input.get("user_id")
        target = parsed_input.get("target")

        room_key = self.state_manager.normalize_room_id(room)
        room_obj = self.state_manager.get_or_create_room(room_key)

        player = self.runtime_player_service.get_or_create(room_obj, user_id)

        if not player:
            return {"action": "move", "error": "Player not found"}

        player.location = target or "unknown"

        narration = self._narrate("move", {
            "location": player.location
        }, world)

        return {
            "action": "move",
            "text": narration.get("text", f"Przemieszczasz się do: {player.location}"),
            "result": {
                "location": player.location
            },
        }