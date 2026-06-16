from game.npc.npc_registry import NPCRegistry
from game.npc.npc_models import NPC


class NPCResolver:
    """
    Builds NPC list based on game state (NO STORAGE)
    """

    def __init__(self, session, flags=None):
        self.session = session
        self.flags = flags or []

    def resolve(self) -> list[NPC]:
        adventure_id = self.session.progress.get("adventure_id")

        if not adventure_id:
            return []

        npcs = NPCRegistry.get_npcs_for_adventure(adventure_id)

        # -------------------------
        # FLAGS LOGIC (GAME STATE)
        # -------------------------
        flag_names = {f.name for f in self.flags}

        # example: NPC disappears after meeting
        if "met_old_man" in flag_names:
            npcs = [n for n in npcs if n.id != "old_man"]

        return npcs