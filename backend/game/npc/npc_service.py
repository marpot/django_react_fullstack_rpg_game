# game/npc/npc_service.py

import logging
from game.npc.npc_models import NPC
from game.npc.npc_registry import NPCRegistry
from game_instances.services.llm.core.llm_client import LLMClient
logger = logging.getLogger(__name__)


class NPCService:
    def __init__(self, state_manager):
        self.state = state_manager
        self.llm = LLMClient()

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
    def talk(self, room_id: str, npc_id: str, message: str):
        room = self.state.get_or_create_room(room_id)
        npc = room.npcs.get(npc_id)

        if not npc:
            return {"error": "NPC not found"}

        prompt = f"""
            You are NPC in RPG game.

            Name: {npc.name}
            Personality: {npc.personality}
            State: {npc.state}

            Player says: {message}

            Rules:
            - stay in character
            - max 2 sentences
            - no meta talk
            """

        reply = self.llm.generate(prompt)

        return {
            "action": "talk",
            "npc": npc.name,
            "reply": reply
        }

    # -------------------------
    # SEEDING (WORLD INTEGRATION)
    # -------------------------
    def seed_room(self, room_id: str, adventure_id: int):
        npcs = NPCRegistry.get_npcs_for_adventure(adventure_id)

        for npc in npcs:
            self.spawn(room_id, npc)

        logger.info(f"[NPC SEED] room={room_id} count={len(npcs)}")