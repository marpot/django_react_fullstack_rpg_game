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
        logger.info(f"[ACTION PROCESS] room={parsed_input.get('room')} user={parsed_input.get('user_id')}")

        action = parsed_input.get("action")
        logger.info(f"[ACTION PROCESS] action={action}")

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

            service = NPCService(self.state_manager)
            return service.talk(
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
        logger.debug(f"[COMBAT DEBUG INPUT] {parsed_input}")

        if not enemy_name:
            logger.error("[COMBAT ERROR] Missing target enemy")
            return {"action": "attack", "error": "Missing target enemy"}

        # ROOM
        room_key = self.state_manager.normalize_room_id(room)
        logger.info(f"[ROOM] normalized room_key={room_key}")

        room_obj = self.state_manager.get_or_create_room(room_key)

        logger.info(f"[ROOM DEBUG] exists={room_obj is not None}")
        logger.info(f"[ROOM DEBUG] players={list(room_obj.players.keys())}")
        logger.info(f"[ROOM DEBUG] enemies={list(room_obj.enemies.keys())}")

        # SEED CHECK
        if not room_obj.enemies:
            logger.warning("[SEED GUARD] empty enemies → attempting seed")

            if adventure_id:
                logger.info(f"[SEED] adventure_id={adventure_id}")

                from world.seeders.world_seeder import WorldSeeder

                seeder = WorldSeeder(self.state_manager)
                seeder.seed_from_adventure(adventure_id, room_key)

                room_obj = self.state_manager.get_room(room_key)

                logger.info(f"[SEED RESULT] enemies={list(room_obj.enemies.keys())}")
            else:
                logger.error("[SEED ERROR] no adventure_id provided")

        # RESOLVE
        logger.info(f"[RESOLVE INPUT] enemy_name={enemy_name} room_key={room_key}")

        attacker_runtime = self._get_or_create_runtime_player(room_obj, user_id)
        defender_runtime = self.resolver.resolve_enemy(room_key, enemy_name)

        logger.info(
            f"[RESOLVE RESULT] player={attacker_runtime is not None} "
            f"enemy={defender_runtime is not None}"
        )

        if not attacker_runtime or not defender_runtime:
            logger.error(f"[COMBAT FAIL] enemy={enemy_name}")
            logger.error(f"[ROOM SNAPSHOT] {list(room_obj.enemies.keys())}")
            return {"action": "attack", "error": "Missing combat entities"}

        result = self.combat_service.resolve(attacker_runtime, defender_runtime)

        # ROOM SYNC
        logger.info(f"[ROOM SYNC BEFORE] {list(room_obj.enemies.keys())}")

        if enemy_name in room_obj.enemies:
            room_obj.enemies[enemy_name].hp = defender_runtime.hp
            logger.info(f"[ROOM SYNC OK] {enemy_name} hp={defender_runtime.hp}")
        else:
            logger.error(f"[ROOM SYNC FAIL] enemy not in room: {enemy_name}")

        # ORM SYNC
        attacker_orm = PlayerCharacter.objects.filter(user_id=user_id).first()
        adventure = Adventure.objects.filter(id=adventure_id).first() if adventure_id else None

        if not attacker_orm or not adventure:
            return {"action": "attack", "error": "Missing DB entities"}

        enemy_orm = EnemyORM.objects.filter(
            name=enemy_name,
            adventure=adventure
        ).first()

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

        logger.info("[COMBAT SUCCESS] attack resolved")

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

    def _get_or_create_runtime_player(self, room_obj, user_id):
        player = room_obj.players.get(user_id) or room_obj.players.get(str(user_id))
        if player:
            logger.debug(f"[PLAYER CACHE HIT] user_id={user_id}")
            return player

        logger.info(f"[PLAYER LOAD] loading ORM player user_id={user_id}")

        attacker_orm = PlayerCharacter.objects.filter(user_id=user_id).first()
        if not attacker_orm:
            logger.error(f"[PLAYER ERROR] not found user_id={user_id}")
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

        logger.info(f"[PLAYER LOADED] user_id={user_id}")

        return player

    def _handle_inspect(self, parsed_input):
        return {"action": "inspect", "result": "Inspect not implemented yet"}

    def _handle_move(self, parsed_input):
        return {"action": "move", "result": "Move not implemented yet"}