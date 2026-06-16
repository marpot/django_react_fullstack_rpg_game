class StateSyncService:

    def __init__(self, state_manager):
        self.state = state_manager

    def build_state(self, room_id: str) -> dict:
        room = self.state.get_or_create_room(room_id)

        return {
            "room_id": room_id,
            "npcs": list(getattr(room, "npcs", {}).keys()),
            "players": list(getattr(room, "players", {}).keys()),
            "events": list(getattr(room, "events", []))[-10:],
            "flags": getattr(room, "flags", {})
        }