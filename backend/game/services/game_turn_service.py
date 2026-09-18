class GameTurnService:
    def __init__(self, state_manager):
        self.state_manager = state_manager

    def get_room(self, room_id: str):
        return self.state_manager.get_or_create_room(room_id)

    def is_player_turn(self, room_obj, participant_id):
        return (
            room_obj.current_player_id == participant_id
            and self.is_participant_active(room_obj, participant_id)
        )

    def is_participant_active(self, room_obj, participant_id):
        if participant_id in room_obj.ai_participants:
            return True
        if room_obj.connected_participants is None:
            return True
        return participant_id in room_obj.connected_participants

    def advance_turn(self, room_obj):
        if not room_obj.turn_order:
            return None

        current = room_obj.current_player_id
        start_index = (
            room_obj.turn_order.index(current)
            if current in room_obj.turn_order
            else -1
        )
        for offset in range(1, len(room_obj.turn_order) + 1):
            next_idx = (start_index + offset) % len(room_obj.turn_order)
            candidate = room_obj.turn_order[next_idx]
            if self.is_participant_active(room_obj, candidate):
                room_obj.current_player_id = candidate
                room_obj.current_turn_index = next_idx
                return candidate

        if current in room_obj.turn_order and self.is_participant_active(room_obj, current):
            room_obj.current_turn_index = start_index
            return current

        room_obj.current_player_id = None
        room_obj.current_turn_index = 0
        return None

    def mark_disconnected(self, room_obj, participant_id):
        was_current = room_obj.current_player_id == participant_id
        if room_obj.connected_participants is None:
            room_obj.connected_participants = set(room_obj.turn_order)
        room_obj.connected_participants.discard(participant_id)
        if was_current:
            return self.advance_turn(room_obj)
        return room_obj.current_player_id

    def register_player(self, room_obj, participant_id):
        if participant_id not in room_obj.turn_order:
            room_obj.turn_order.append(participant_id)

        room_obj.player_histories.setdefault(participant_id, [])

        if room_obj.current_player_id is None:
            room_obj.current_player_id = participant_id
            room_obj.current_turn_index = 0

    def build_state(self, room_obj, participant_id):
        return {
            "current_player_id": room_obj.current_player_id,
            "current_turn_index": room_obj.current_turn_index,
            "turn_order": room_obj.turn_order,
            "is_your_turn": room_obj.current_player_id == participant_id,
            "history": room_obj.player_histories.get(participant_id, []),
        }
