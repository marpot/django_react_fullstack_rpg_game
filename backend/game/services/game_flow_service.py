import logging
from asgiref.sync import sync_to_async

from game.core.action_processor import ActionProcessor
from game.core.events.memory_builder import GameMemoryBuilder
from game_instances.services.llm.orchestrator.llm_service import LLMService

logger = logging.getLogger(__name__)


class GameFlowService:

    def __init__(self, state_manager, turn_service):
        self.state_manager = state_manager
        self.turn_service = turn_service
        self.processor = ActionProcessor(state_manager)

    async def handle(self, consumer, user_input, world, room_name, user_id, adventure_id):

        memory = await sync_to_async(GameMemoryBuilder().build)(
            adventure_id,
            room_name,
            20
        )

        llm = LLMService()

        parsed = llm.parse_player_input({
            "input": user_input,
            "memory": memory,
            "world": world
        })

        if not isinstance(parsed, dict) or "action" not in parsed:
            return None

        parsed.update({
            "room": room_name,
            "user_id": user_id,
            "adventure": adventure_id,
            "world": world,
        })

        room_obj = self.turn_service.get_room(room_name)

        self.turn_service.register_player(room_obj, user_id)

        if not self.turn_service.is_player_turn(room_obj, user_id):
            return {
                "blocked": True,
                "room_obj": room_obj
            }

        result = await sync_to_async(self.processor.process)(parsed)

        self.turn_service.advance_turn(room_obj)

        return {
            "blocked": False,
            "result": result
        }