from game.services.combat_service import CombatService
from game.services.dice_service import DiceService

class ActionProcessor:
    def __init__(self):
        self.combat_service = CombatService(
            DiceService()
        )

    def process(self, parsed_input, attacker=None, defender=None):
            
        action = parsed_input.get("action")

        if action == "attack":
            if not attacker or not defender:
                return {
                    "error": "Missing combat entities"
                }
                
            result = self.combat_service.resolve(
                attacker,
                defender
            )

            return {
                "action": "attack",
                "result": result
            }
            
        return {
            "action": action,
            "result": "Unhandled action"
        }