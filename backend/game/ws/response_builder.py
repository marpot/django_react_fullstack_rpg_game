class ResponseBuilder:

    def build_action_response(self, parsed, result):
        return {
            "type": "game_event",
            "subtype": "action_result",
            "action": parsed,
            "result": result,
        }

    def build_state_response(self, state):
        return {
            "type": "state_update",
            "state": state,
        }