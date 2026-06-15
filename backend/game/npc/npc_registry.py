from game.npc.npc_models import NPC


class NPCRegistry:
    """
    Static NPC definitions (world seed layer)
    """

    @staticmethod
    def get_npcs_for_adventure(adventure_id: int) -> list[NPC]:
        return [
            NPC(
                id="old_man",
                name="Old Man",
                dialog=[
                    "Witaj, wędrowcze...",
                    "Uważaj na gobliny w lesie."
                ],
                personality="wise"
            ),
            NPC(
                id="merchant",
                name="Merchant",
                dialog=[
                    "Kup coś zanim odejdziesz!",
                    "Mam najlepsze towary w regionie."
                ],
                personality="greedy"
            )
        ]


# backward compatibility layer (USED BY SEEDER)

def create_starter_npcs(adventure_id: int):
    return NPCRegistry.get_npcs_for_adventure(adventure_id)