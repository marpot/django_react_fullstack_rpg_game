from asgiref.sync import sync_to_async
from chat.models import RoomParticipant

class PlayerService:

    async def get_players(self, room_id: str):
        participants = await sync_to_async(
            lambda: list(
                RoomParticipant.objects.filter(room_id=room_id)
                .values("id", "name", "is_ai")
            )
        )()

        return [
            {
                "id": p["id"],
                "name": p["name"],
                "type": "ai" if p["is_ai"] else "human"
            }
            for p in participants
        ]