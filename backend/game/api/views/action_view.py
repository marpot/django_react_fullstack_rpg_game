from game.core.action_processor import ActionProcessor
from game.state.game_state_manager import GameStateManager


state_manager = GameStateManager()
processor = ActionProcessor(state_manager)


def handle_action(request):
    data = request.data

    parsed_input = {
        "action": data.get("action"),
        "attacker": data.get("attacker"),
        "target": data.get("target"),
        "room": data.get("room"),
    }

    return processor.process(parsed_input)