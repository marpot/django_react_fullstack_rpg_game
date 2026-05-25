from game.services.combat_service import CombatService
from game.services.dice_service import DiceService

class GameService:
    def resolve_fight(self, attacker, defender):
        dice = DiceService(seed=1)
        combat = CombatService(dice)

        return combat.resolve(attacker, defender)