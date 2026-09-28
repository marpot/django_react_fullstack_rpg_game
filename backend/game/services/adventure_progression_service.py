from game.domain.adventure_definition import build_definition_for_adventure


class AdventureProgressionService:
    def __init__(self, state_manager):
        self.state_manager = state_manager

    def advance(self, room_obj, participant_id, action, result):
        """Apply the configured deterministic progression slice."""
        if not room_obj.adventure_id:
            return

        try:
            definition = build_definition_for_adventure(room_obj.adventure_id)
        except Exception:
            return

        steps = definition.progression.steps
        if not steps or room_obj.quest.completed or room_obj.adventure_completed:
            return

        player = room_obj.players.get(participant_id)
        if player is None:
            return

        location = self.state_manager.get_location(room_obj, player)
        quest = room_obj.quest

        if quest.status == "not_started":
            step = steps[0]
        else:
            current_index = next(
                (index for index, candidate in enumerate(steps) if candidate.stage == quest.stage),
                None,
            )
            if current_index is None or current_index + 1 >= len(steps):
                return
            step = steps[current_index + 1]

        if not self._trigger_matches(
            definition, step.trigger, action, result, location, room_obj, player
        ):
            return

        if action == "talk":
            npc_id = result.get("npc_id") or result.get("_npc_id")
            flag_suffix = "spoken" if quest.status == "not_started" else "found"
            quest.flags[f"{npc_id}_{flag_suffix}"] = True
        elif action == "attack":
            quest.flags["enemy_defeated"] = True

        quest.stage = step.stage
        quest.objective = step.objective or None
        if step.next_stage is None:
            quest.status = "completed"
            quest.completed = True
            room_obj.adventure_completed = True
        else:
            quest.status = "active"

    def _trigger_matches(
        self, definition, trigger, action, result, location, room_obj, player
    ):
        if location is None or ":" not in trigger:
            return False

        trigger_action, target_location = trigger.split(":", 1)
        if trigger_action == "move":
            if action != "move":
                return False
            location_token = target_location
        else:
            if "@" not in target_location:
                return False
            trigger_target, location_token = target_location.split("@", 1)

        location_id = next(
            (
                candidate.id
                for candidate in definition.locations
                if candidate.title.casefold() == location_token.casefold()
            ),
            None,
        )
        if location_id is None or str(location_id) != str(location.id):
            return False

        if trigger_action == "talk":
            npc_id = result.get("npc_id") or result.get("_npc_id")
            return action == "talk" and npc_id == trigger_target

        if trigger_action == "defeat":
            if action != "attack" or result.get("winner") != "attacker":
                return False
            if trigger_target != "enemy":
                return False
            return not any(
                enemy.hp > 0
                for enemy in self.state_manager.visible_enemies(room_obj, player)
            )

        if trigger_action == "move":
            return True

        return False
