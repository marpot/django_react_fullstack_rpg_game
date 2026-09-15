class GameTurnService:
    def __init__(self, state_manager):
        self.state_manager = state_manager

    def get_room(self, room_id: str):
        return self.state_manager.get_or_create_room(room_id)

    def is_player_turn(self, room_obj, user_id):
        return room_obj.current_player_id == user_id

    def advance_turn(self, room_obj):
        if not room_obj.turn_order:
            return None

        current = room_obj.current_player_id
        if current is None:
            room_obj.current_player_id = room_obj.turn_order[0]
            room_obj.current_turn_index = 0
            return room_obj.current_player_id

        idx = room_obj.turn_order.index(current)
        next_idx = (idx + 1) % len(room_obj.turn_order)

        room_obj.current_player_id = room_obj.turn_order[next_idx]
        room_obj.current_turn_index = next_idx

        return room_obj.current_player_id

    def register_player(self, room_obj, user_id):
        if user_id not in room_obj.turn_order:
            room_obj.turn_order.append(user_id)

        room_obj.player_histories.setdefault(user_id, [])

        if room_obj.current_player_id is None:
            room_obj.current_player_id = user_id
            room_obj.current_turn_index = 0

    def build_state(self, room_obj, user_id):
        return {
            "current_player_id": room_obj.current_player_id,
            "current_turn_index": room_obj.current_turn_index,
            "turn_order": room_obj.turn_order,
            "is_your_turn": room_obj.current_player_id == user_id,
            "history": room_obj.player_histories.get(user_id, []),
        }