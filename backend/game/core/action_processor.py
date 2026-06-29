import logging

from game.services.combat_service import CombatService
from game.services.dice_service import DiceService
from game.state.resolver.entity_resolver import EntityResolver
from game.state.runtime.runtime_player_service import RuntimePlayerService
from game_instances.services.llm.orchestrator.llm_service import LLMService
from game.npc.npc_service import NPCService

from game.state.runtime.models import Enemy as RuntimeEnemy
from world.models import Enemy as EnemyORM

logger = logging.getLogger(__name__)


class ActionProcessor:
    def __init__(self, state_manager, combat_service=None, resolver=None):
        self.state_manager = state_manager
        self.combat_service = combat_service or CombatService(DiceService())
        self.resolver = resolver or EntityResolver(state_manager)
        self.runtime_player_service = RuntimePlayerService(state_manager)

    def _response(self, event_type: str, text: str, result=None, world=None, choices=None):
        return {
            "action": event_type,
            "event_type": event_type,
            "text": text,
            "result": result or {},
            "world": world or {},
            "choices": choices or [],
        }

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
            return self._response(
                "unknown",
                "Invalid action",
                {"error": "invalid_action"}
            )

        if action == "attack":
            return self._handle_attack(parsed_input, world)

        if action == "inspect":
            return self._handle_inspect(parsed_input, world)

        if action == "move":
            return self._handle_move(parsed_input, world)

        if action == "look":
            return self._handle_inspect(parsed_input, world)

        if action == "talk":
            result = NPCService(self.state_manager).talk(
                parsed_input["room"],
                parsed_input["target"]
            )
            return self._response("talk", result.get("text", ""), result)

        return self._response(action, "Unhandled action", {"error": "unhandled_action"})

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

        attacker = self.runtime_player_service.get_or_create(room_obj, user_id)

        if not attacker:
            return self._response("attack", "Brak postaci", {"error": "no_player"})

        # -------------------------
        # RESOLVE ENEMY
        # -------------------------
        defender = self.resolver.resolve_enemy(room_key, enemy_name)

        # 🔥 FIX 1: ORM fallback seed (KLUCZ DO TESTU)
        if not defender:
            orm_enemy = EnemyORM.objects.filter(
                name=enemy_name,
                adventure_id=parsed_input.get("adventure")
            ).first()

            if orm_enemy:
                defender = RuntimeEnemy(
                    id=orm_enemy.name,
                    name=orm_enemy.name,
                    hp=orm_enemy.hp,
                    defense=orm_enemy.defense,
                    attack_bonus=orm_enemy.attack_bonus,
                    damage_die=orm_enemy.damage_die,
                    damage_bonus=orm_enemy.damage_bonus,
                )

        if not defender:
            logger.warning(f"[ACTION PROCESS] enemy not found: {enemy_name} in room {room_key}")
            return self._response(
                "attack",
                f"Nie znaleziono przeciwnika: {enemy_name}",
                {"error": "enemy_not_found", "target": enemy_name},
            )

        # 🔥 FIX 2: seed do room state
        if enemy_name not in room_obj.enemies:
            room_obj.enemies[enemy_name] = defender

        result = self.combat_service.resolve(attacker, defender)

        enemy_in_room = room_obj.enemies.get(enemy_name)

        if enemy_in_room:
            enemy_in_room.hp = max(0, enemy_in_room.hp - result.attacker_damage)

        attacker.hp = max(0, attacker.hp - result.defender_damage)

        narration = self._narrate("attack", {
            "attacker_hit": result.attacker_hit,
            "defender_hit": result.defender_hit,
            "attacker_damage": result.attacker_damage,
            "defender_damage": result.defender_damage,
            "winner": result.winner,
        }, world)

        return self._response(
            "attack",
            narration.get("text", "Walka zakończona"),
            {
                "winner": result.winner,
                "attacker_damage": result.attacker_damage,
                "defender_damage": result.defender_damage,
            },
        )

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

        return self._response(
            "inspect",
            narration.get("text", "Rozglądasz się po okolicy"),
            {
                "room": room_key,
                "enemies": enemies,
            },
        )

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
            return self._response("move", "Player not found", {"error": "no_player"})

        player.location = target or "unknown"

        narration = self._narrate("move", {
            "location": player.location
        }, world)

        return self._response(
            "move",
            narration.get("text", f"Przemieszczasz się do: {player.location}"),
            {"location": player.location},
        )