from game.npc.npc_models import NPC


class NPCRegistry:
    """
    Static NPC definitions (world seed layer)
    """

    @staticmethod
    def get_npcs_for_adventure(adventure_id: int) -> list[NPC]:
        # Reference adventure uses deterministic roles required by its slice.
        try:
            from world.models import Adventure
            is_shadows = Adventure.objects.filter(
                pk=adventure_id, title="Cienie Eldorii"
            ).exists()
        except Exception:
            is_shadows = False
        if is_shadows:
            return [
                NPC(
                    id="guard", name="Guard",
                    dialog=["Strażnik wskazuje ścieżkę do mrocznego lasu."],
                    personality="vigilant",
                ),
                NPC(
                    id="merchant", name="Merchant",
                    dialog=["Kupiec czekał na kogoś, kto pokonał bestię."],
                    personality="relieved",
                ),
            ]
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
