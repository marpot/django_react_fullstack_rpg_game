class GameLoopService:

    def __init__(self, state_manager, llm, processor, state_sync, builder):
        self.state = state_manager
        self.llm = llm
        self.processor = processor
        self.state_sync = state_sync
        self.builder = builder

    def handle_action(self, room_name, user_id, user_input, adventure_id):
        parsed = self.llm.parse_player_input(user_input)

        parsed["room"] = room_name
        parsed["user_id"] = user_id
        parsed["adventure"] = adventure_id

        result = self.processor.process(parsed)

        state = self.state_sync.build_state(room_name)

        return parsed, result, state