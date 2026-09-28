class BotTurnService:
    def __init__(self, state_manager, bot_player_service, processor):
        self.state_manager = state_manager
        self.bot_player_service = bot_player_service
        self.processor = processor

    def execute(self, room_name, *, adventure, world):
        results = []
        room_state = self.state_manager.get_room(room_name)
        if room_state is None:
            return results

        with self.state_manager.start_lock:
            for _ in range(len(room_state.turn_order)):
                if room_state.adventure_completed or room_state.quest.completed:
                    break

                participant_id = room_state.current_player_id
                if participant_id not in room_state.ai_participants:
                    break

                command = self.bot_player_service.choose_command(
                    room_state,
                    participant_id,
                )
                result = self.processor.process(
                    command,
                    room=room_name,
                    participant_id=participant_id,
                    adventure=adventure,
                    world=world,
                )
                result["_actor_id"] = participant_id
                results.append(result)

        return results
