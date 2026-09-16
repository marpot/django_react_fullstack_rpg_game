# game/npc/npc_service.py

import logging
from game.npc.npc_models import NPC
from game.npc.npc_registry import NPCRegistry
logger = logging.getLogger(__name__)


class NPCService:
    def __init__(self, state_manager):
        self.state = state_manager

    # -------------------------
    # SPAWN
    # -------------------------
    def spawn(self, room_id: str, npc: NPC):
        room = self.state.get_or_create_room(room_id)
        room.npcs[npc.id] = npc
        logger.info(f"[NPC SPAWN] {npc.id} -> room={room_id}")

    # -------------------------
    # TALK
    # -------------------------
    def talk(self, room_id: str, npc_id: str | None):
        room = self.state.get_or_create_room(room_id)
        npc = room.npcs.get(npc_id)

        if not npc:
            return {"error": "npc_not_found", "text": "Nie znaleziono NPC."}

        return {
            "action": "talk",
            "npc": npc.name,
            "text": npc.dialog[0] if npc.dialog else f"Rozmawiasz z {npc.name}.",
        }

    # -------------------------
    # SEEDING (WORLD INTEGRATION)
    # -------------------------
    def seed_room(self, room_id: str, adventure_id: int):
        npcs = NPCRegistry.get_npcs_for_adventure(adventure_id)

        for npc in npcs:
            self.spawn(room_id, npc)

        logger.info(f"[NPC SEED] room={room_id} count={len(npcs)}")
