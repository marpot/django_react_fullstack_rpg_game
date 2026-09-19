import logging

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
        visible = self.state_manager.visible_enemies(room_obj, attacker)
        enemy_in_room = next(
            (enemy for enemy in visible.values()
             if defender is not None and enemy.name == defender.name),
            None,
        )

        if enemy_in_room is None:
            logger.warning(f"[ACTION PROCESS] enemy not found: {enemy_name} in room {room_key}")
            return self.response_fn(
                "attack",
                f"Nie znaleziono przeciwnika: {enemy_name}",
                {"error": "enemy_not_found", "target": enemy_name},
            )

        defender = enemy_in_room
        result = self.combat_service.resolve(attacker, defender)
        enemy_in_room.hp = max(0, enemy_in_room.hp - result.attacker_damage)

        attacker.hp = max(0, attacker.hp - result.defender_damage)

        canonical_result = {
            "winner": (
                "draw" if attacker.hp == 0 and enemy_in_room.hp == 0 else
                "defender" if attacker.hp == 0 else
                "attacker" if enemy_in_room.hp == 0 else None
            ),
            "attacker_damage": result.attacker_damage,
            "defender_damage": result.defender_damage,
        }
        narration = self.narrate_fn("attack", canonical_result, world, {
            "actor": attacker.name,
            "actor_is_ai": participant_id in room_obj.ai_participants,
            "target": defender.name,
            "location": attacker.location,
            "recent_actions": [
                entry.get("action") for entry in room_obj.player_histories.get(participant_id, [])[-3:]
                if isinstance(entry, dict)
            ],
        })

        choices = self.choice_service.build_choices(
            enemies=self.state_manager.visible_enemies(room_obj, attacker),
            npcs=self.state_manager.visible_npcs(room_obj, attacker),
            exits=self.state_manager.get_exits(room_obj, attacker),
        )

        return self.response_fn(
            "attack",
            narration.get("text", "Walka zakończona"),
            canonical_result,
            world,
            choices,
        )
