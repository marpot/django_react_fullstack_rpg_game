class CombatResolver:
    def __init__(self, combat_service):
        self.combat_service = combat_service

    def handle(self, parsed_input):
        attacker = parsed_input["attacker"]
        defender = parsed_input["target"]

        result = self.combat_service.resolve(attacker, defender)

        return {
            "action": "attack",
            "result": result.model_dump() if hasattr(result, "model_dump") else result
        }