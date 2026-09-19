from game.core.game_command import GameCommand
from game.domain.adventure_definition import build_definition_for_adventure


class BotPlayerService:
    """Choose a legal command for an AI participant from current room state."""

    def __init__(self, state_manager):
        self.state_manager = state_manager

    def choose_command(self, room_obj, participant_id):
        if participant_id not in room_obj.ai_participants:
            raise ValueError("participant_is_not_ai")

        if room_obj.adventure_completed or room_obj.quest.completed:
            return None

        player = room_obj.players.get(participant_id)
        if player is None:
            raise ValueError("runtime_player_not_found")

        enemies = self.state_manager.visible_enemies(room_obj, player)
        if enemies:
            return GameCommand(action="attack", target=next(iter(enemies)))

        npcs = self.state_manager.visible_npcs(room_obj, player)
        exits = self.state_manager.get_exits(room_obj, player)
        progression_step = self._next_progression_step(room_obj)

        if progression_step is not None:
            trigger_action, trigger_target, target_location = self._trigger_parts(
                progression_step.trigger
            )

            if trigger_action == "talk" and trigger_target in npcs:
                return GameCommand(action="talk", target=trigger_target)

            if trigger_action in {"talk", "move", "defeat"}:
                for exit_choice in exits:
                    if exit_choice.next_location.title.casefold() == target_location.casefold():
                        return GameCommand(
                            action="move",
                            target=str(exit_choice.next_location_id),
                        )

            if npcs:
                return GameCommand(action="talk", target=next(iter(npcs)))
            return GameCommand(action="inspect")

        if npcs:
            return GameCommand(action="talk", target=next(iter(npcs)))

        if exits:
            return GameCommand(action="move", target=str(exits[0].next_location_id))

        return GameCommand(action="inspect")

    @staticmethod
    def _trigger_parts(trigger):
        action, target = trigger.split(":", 1)
        if action == "move":
            return action, None, target
        target_name, location = target.split("@", 1)
        return action, target_name, location

    @staticmethod
    def _next_progression_step(room_obj):
        if not room_obj.adventure_id:
            return None

        try:
            definition = build_definition_for_adventure(room_obj.adventure_id)
        except Exception:
            return None

        steps = definition.progression.steps
        if not steps:
            return None

        quest = room_obj.quest
        if quest.status == "not_started":
            return steps[0]

        current_index = next(
            (
                index
                for index, step in enumerate(steps)
                if step.stage == quest.stage
            ),
            None,
        )
        if current_index is None or current_index + 1 >= len(steps):
            return None
        return steps[current_index + 1]
