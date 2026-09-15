from asgiref.sync import sync_to_async
from chat.models import RoomParticipant
from game_instances.services.llm.orchestrator.llm_service import LLMService


class GameWorldService:

    def __init__(self, state_manager, choice_service):
        self.state_manager = state_manager
        self.choice_service = choice_service

    async def build_world(self, room_name, adventure_id):

        llm = LLMService()

        world_raw = await sync_to_async(llm.generate_world)(
            {"adventure": {"id": adventure_id}}
        )

        if not isinstance(world_raw, dict):
            world_raw = {
                "intro": "A strange world forms...",
                "situation": "The world is unstable."
            }

        world = {
            "name": world_raw.get("name", "Unknown World"),
            "title": world_raw.get("title", "Unknown World"),
            "description": world_raw.get("description", ""),
            "intro": world_raw.get("intro", ""),
            "lore": {"situation": world_raw.get("situation", "")},
            "rules": world_raw.get("rules", {}),
            "seed": world_raw.get("seed", {}),
        }

        choices = await sync_to_async(self.choice_service.build_choices)(
            adventure_id=adventure_id,
            room_key=room_name,
            event_type="game_started",
            result={"intro": world.get("intro", "")},
            world=world,
        )

        participants = await sync_to_async(
            lambda: list(
                RoomParticipant.objects.filter(room_id=room_name)
                .values("id", "name", "is_ai")
            )
        )()

        players = [
            {
                "id": p["id"],
                "name": p["name"],
                "type": "ai" if p["is_ai"] else "human"
            }
            for p in participants
        ]

        return world, choices, players