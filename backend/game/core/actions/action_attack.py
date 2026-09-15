import logging
from game.state.runtime.models import Enemy as RuntimeEnemy

logger = logging.getLogger(__name__)


class AttackAction:
    def __init__(
        self,
        state_manager,
        combat_service,
        resolver,
        runtime_player_service,
        choice_service,
        narrate_fn,
        response_fn,
    ):
        self.state_manager = state_manager
        self.combat_service = combat_service
        self.resolver = resolver
        self.runtime_player_service = runtime_player_service
        self.choice_service = choice_service
        self.narrate_fn = narrate_fn
        self.response_fn = response_fn

    def handle(self, parsed_input, world=None):
        from world.models import Enemy as EnemyORM
        room = parsed_input.get("room")
        participant_id = parsed_input.get("participant_id")
        enemy_name = parsed_input.get("target")

        if isinstance(enemy_name, str):
            enemy_name = enemy_name.lower().strip().rstrip(".,!?")
        else:
            enemy_name = None

        room_key = self.state_manager.normalize_room_id(room)
        room_obj = self.state_manager.get_or_create_room(room_key)

        attacker = self.runtime_player_service.get_or_create(room_obj, participant_id)

        if not attacker:
            return self.response_fn(
                "attack",
                "Brak postaci",
                {"error": "no_player"},
            )

        defender = self.resolver.resolve_enemy(room_key, enemy_name)

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
            return self.response_fn(
                "attack",
                f"Nie znaleziono przeciwnika: {enemy_name}",
                {"error": "enemy_not_found", "target": enemy_name},
            )

        if enemy_name not in room_obj.enemies:
            room_obj.enemies[enemy_name] = defender

        result = self.combat_service.resolve(attacker, defender)

        enemy_in_room = room_obj.enemies.get(enemy_name)

        if enemy_in_room:
            enemy_in_room.hp = max(0, enemy_in_room.hp - result.attacker_damage)

        attacker.hp = max(0, attacker.hp - result.defender_damage)

        narration = self.narrate_fn(
            "attack",
            {
                "attacker_hit": result.attacker_hit,
                "defender_hit": result.defender_hit,
                "attacker_damage": result.attacker_damage,
                "defender_damage": result.defender_damage,
                "winner": result.winner,
            },
            world,
        )

        choices = self.choice_service.build_choices(
            adventure_id=parsed_input.get("adventure"),
            room_key=room_key,
            event_type="attack",
            result={
                "winner": result.winner,
                "attacker_damage": result.attacker_damage,
                "defender_damage": result.defender_damage,
            },
            world=world,
        )

        return self.response_fn(
            "attack",
            narration.get("text", "Walka zakończona"),
            {
                "winner": result.winner,
                "attacker_damage": result.attacker_damage,
                "defender_damage": result.defender_damage,
            },
            world,
            choices,
        )