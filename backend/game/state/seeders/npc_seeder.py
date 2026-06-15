from game.npc.npc_service import NPCService
from game.npc.npc_registry import create_starter_npcs
import logging

logger = logging.getLogger(__name__)

class NPCSeeder:
    def __init__(self, state_manager):
        self.state = state_manager
        self.service = NPCService(state_manager)

    def seed(self, room_id: str, adventure_id: int):
        logger.info(f"[NPC SEED] seeding room_id={room_id}")

        npcs = create_starter_npcs(adventure_id)
        
        for npc in npcs:
            self.service.spawn(room_id, npc)