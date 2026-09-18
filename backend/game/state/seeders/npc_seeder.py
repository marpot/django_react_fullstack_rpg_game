from game.domain.adventure_definition import build_definition_for_adventure
from game.npc.npc_service import NPCService
from game.npc.npc_models import NPC
from game.npc.npc_registry import create_starter_npcs
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

class NPCSeeder:
    def __init__(self, state_manager):
        self.state = state_manager
        self.service = NPCService(state_manager)

    def seed(self, room_id: str, adventure_id: int):
        logger.info(f"[NPC SEED] seeding room_id={room_id}")

        try:
            definition = build_definition_for_adventure(adventure_id)
        except ObjectDoesNotExist:
            npcs = create_starter_npcs(adventure_id)
        else:
            npcs = (
                NPC(
                    id=npc.id,
                    name=npc.name,
                    dialog=list(npc.dialog),
                    personality=npc.personality,
                )
                for npc in definition.npcs
            )
        
        for npc in npcs:
            self.service.spawn(room_id, npc)
