from simulation_engine.services.combat_service import CombatService
from simulation_engine.services.dice_service import DiceService
from game.state.resolver.entity_resolver import EntityResolver
from game.services.event_service import GameEventService


class ActionProcessor:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.combat_service = CombatService(DiceService())
        self.resolver = EntityResolver(state_manager)
        self.event_service = GameEventService()

    def process(self, parsed_input):
        action = parsed_input.get("action")

        if action == "attack":
            return self._attack(parsed_input)

        if action == "inspect":
            return {"action": "inspect"}

        if action == "move":
            return {"action": "move"}

        return {"error": "Unhandled action"}

    def _attack(self, parsed_input):
        from simulation_engine.combat.combat_resolver import CombatResolver

        resolver = CombatResolver(self.combat_service)

        return resolver.handle(parsed_input)