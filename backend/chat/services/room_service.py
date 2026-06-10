from world.models import Adventure
from chat.models import Room


class RoomService:

    @staticmethod
    def set_adventure(room: Room, user, adventure_id: int):
        if room.owner != user:
            return {
                "ok": False,
                "error": "ONLY_OWNER"
            }

        if not adventure_id:
            return {
                "ok": False,
                "error": "ADVENTURE_REQUIRED"
            }

        adventure = Adventure.objects.filter(id=adventure_id).first()

        if not adventure:
            return {
                "ok": False,
                "error": "ADVENTURE_NOT_FOUND"
            }

        room.adventure = adventure
        room.state = "lobby"
        room.save(update_fields=["adventure", "state"])

        return {
            "ok": True,
            "room": room,
            "adventure": adventure
        }

    @staticmethod
    def can_start_game(room: Room, user):
        if room.owner != user:
            return {"ok": False, "error": "ONLY_OWNER"}

        if not room.adventure:
            return {"ok": False, "error": "NO_ADVENTURE"}

        return {"ok": True}