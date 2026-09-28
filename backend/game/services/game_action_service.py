NO_ACTION = object()


class GameActionService:
    def __init__(self, processor, input_interpreter):
        self.processor = processor
        self.input_interpreter = input_interpreter

    def execute(
        self,
        player_input,
        *,
        state_manager,
        room,
        participant_id,
        adventure,
        world,
    ):
        has_command = "command" in player_input

        if has_command:
            command = player_input["command"]
            player_message = None
        else:
            player_message = player_input.get("message", "")
            command = self.input_interpreter.interpret_player_input(
                {"input": player_message},
                state_manager=state_manager,
                room=room,
                participant_id=participant_id,
            )
            if not isinstance(command, dict) or "action" not in command:
                return NO_ACTION

        return self.processor.process(
            command,
            room=room,
            participant_id=participant_id,
            adventure=adventure,
            world=world,
            player_message=player_message,
        )
