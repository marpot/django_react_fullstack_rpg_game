import logging

from game.services.combat_service import CombatService
from game.services.dice_service import DiceService
from game.state.resolver.entity_resolver import EntityResolver
from game.services.event_service import GameEventService

from accounts.models import PlayerCharacter
from world.models import Enemy as EnemyORM, Adventure

logger = logging.getLogger(__name__)


class ActionProcessor:
    def __init__(self, state_manager, combat_service=None, resolver=None):
        self.state_manager = state_manager
        self.combat_service = combat_service or CombatService(DiceService())
        self.resolver = resolver or EntityResolver(state_manager)
        self.event_service = GameEventService()

    def process(self, parsed_input):
        logger.info(f"[ACTION PROCESS] input={parsed_input}")

        action = parsed_input.get("action")
        logger.info(f"[ACTION PROCESS] action={action}")

        if parsed_input.get("error") == "unknown_intent_fallback":
            logger.info("[FALLBACK] redirect -> inspect")
            return self._handle_inspect(parsed_input)

        if not action or action == "unknown":
            return self._handle_inspect(parsed_input)

        if action == "attack":
            return self._handle_attack(parsed_input)

        if action == "inspect":
            return self._handle_inspect(parsed_input)

        if action == "move":
            return self._handle_move(parsed_input)

        if action == "look":
            return self._handle_inspect(parsed_input)

        if action == "talk":
            from game.npc.npc_service import NPCService
            return NPCService(self.state_manager).talk(
                parsed_input["room"],
                parsed_input["target"]
            )

        return {"action": action, "result": "Unhandled action"}

    def _handle_attack(self, parsed_input):
        room = parsed_input.get("room")
        user_id = parsed_input.get("user_id")
        enemy_name = parsed_input.get("target")
        adventure_id = parsed_input.get("adventure")

        enemy_name = enemy_name.lower().strip() if enemy_name else None

        logger.info(f"[COMBAT] START room={room} user_id={user_id} enemy={enemy_name}")

        if not enemy_name:
            return {"action": "attack", "error": "Missing target enemy"}

        room_key = self.state_manager.normalize_room_id(room)
        room_obj = self.state_manager.get_or_create_room(room_key)

        if not room_obj.enemies:
            logger.warning("[SEED GUARD] empty enemies")

            if adventure_id:
                from world.seeders.world_seeder import WorldSeeder
                WorldSeeder(self.state_manager).seed_from_adventure(adventure_id, room_key)
                room_obj = self.state_manager.get_room(room_key)

        attacker_runtime = self._get_or_create_runtime_player(room_obj, user_id)
        defender_runtime = self.resolver.resolve_enemy(room_key, enemy_name)

        if not attacker_runtime or not defender_runtime:
            return {"action": "attack", "error": "Missing combat entities"}

        result = self.combat_service.resolve(attacker_runtime, defender_runtime)

        if enemy_name in room_obj.enemies:
            room_obj.enemies[enemy_name].hp = defender_runtime.hp

        attacker_orm = PlayerCharacter.objects.filter(user_id=user_id).first()
        adventure = Adventure.objects.filter(id=adventure_id).first() if adventure_id else None

        if attacker_orm and adventure:
            enemy_orm = EnemyORM.objects.filter(
                name=enemy_name,
                adventure=adventure
            ).first()

            if enemy_orm:
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
            "text": "Walka zakończona",
            "result": {
                "attacker_hit": result.attacker_hit,
                "defender_hit": result.defender_hit,
                "attacker_damage": result.attacker_damage,
                "defender_damage": result.defender_damage,
                "winner": result.winner,
            },
        }

    def _get_or_create_runtime_player(self, room_obj, user_id):
        player = room_obj.players.get(user_id) or room_obj.players.get(str(user_id))
        if player:
            return player

        attacker_orm = PlayerCharacter.objects.filter(user_id=user_id).first()
        if not attacker_orm:
            return None

        from game.state.runtime.models import Player as RuntimePlayer

        player = RuntimePlayer(
            id=attacker_orm.user_id,
            name=attacker_orm.name,
            hp=attacker_orm.health,
            max_hp=attacker_orm.health,
            attack_bonus=getattr(attacker_orm, "attack_bonus", 0),
            damage_die=getattr(attacker_orm, "damage_die", 6),
            damage_bonus=getattr(attacker_orm, "damage_bonus", 0),
            defense=getattr(attacker_orm, "defense", 0),
        )

        room_obj.players[user_id] = player
        room_obj.players[str(user_id)] = player

        return player

    def _handle_inspect(self, parsed_input):
        room = parsed_input.get("room")
        user_id = parsed_input.get("user_id")

        room_key = self.state_manager.normalize_room_id(room)
        room_obj = self.state_manager.get_or_create_room(room_key)

        player = room_obj.players.get(user_id) or room_obj.players.get(str(user_id))
        enemies = list(room_obj.enemies.keys())

        return {
            "action": "inspect",
            "text": "Rozglądasz się po okolicy",
            "result": {
                "room": room_key,
                "player": player.name if player else None,
                "enemies": enemies,
                "message": "Rozglądasz się po okolicy"
            }
        }

    def _handle_move(self, parsed_input):
        room = parsed_input.get("room")
        user_id = parsed_input.get("user_id")
        target = parsed_input.get("target")

        room_key = self.state_manager.normalize_room_id(room)
        room_obj = self.state_manager.get_or_create_room(room_key)

        player = room_obj.players.get(user_id) or room_obj.players.get(str(user_id))

        if not player:
            return {"action": "move", "error": "Player not found in room"}

        player.location = target or "unknown"

        return {
            "action": "move",
            "text": f"Przemieszczasz się do: {player.location}",
            "result": {
                "message": f"Przemieszczasz się do: {player.location}",
                "location": player.location
            },
        }