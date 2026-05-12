from game.services.combat_service import CombatService
from game.services.dice_service import DiceService
from game.state.game_state_manager import GameStateManager
from game.state.resolver.entity_resolver import EntityResolver

class ActionProcessor:
    def __init__(self, state_manager):
        self.combat_service = CombatService(DiceService())
        self.state_manager = GameStateManager()
        self.resolver = EntityResolver(self.state_manager)
        

    def process(self, parsed_input, attacker=None, defender=None):
            
        action = parsed_input.get("action")

        if action == "attack":
            room = parsed_input.get("room", "testroom")
            user_id = parsed_input.get("user_id")

            attacker = self.resolver.resolve_player(room,user_id)
            defender = self.resolver.resolve_enemy(room, parsed_input.get("target"))


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