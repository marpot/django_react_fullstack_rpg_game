from game.core.game_command import GameCommand


class BotPlayerService:
    """Choose a legal command for an AI participant from current room state."""

    def __init__(self, state_manager):
        self.state_manager = state_manager

    def choose_command(self, room_obj, participant_id):
        if participant_id not in room_obj.ai_participants:
            raise ValueError("participant_is_not_ai")

        player = room_obj.players.get(participant_id)
        if player is None:
            raise ValueError("runtime_player_not_found")

        enemies = self.state_manager.visible_enemies(room_obj, player)
        if enemies:
            return GameCommand(action="attack", target=next(iter(enemies)))

        npcs = self.state_manager.visible_npcs(room_obj, player)
        if npcs:
            return GameCommand(action="talk", target=next(iter(npcs)))

        exits = self.state_manager.get_exits(room_obj, player)
        if exits:
            return GameCommand(action="move", target=str(exits[0].next_location_id))

        return GameCommand(action="inspect")
