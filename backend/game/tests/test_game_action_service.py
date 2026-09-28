from unittest.mock import Mock

import pytest

from game.services.game_action_service import GameActionService, NO_ACTION


@pytest.fixture
def action_service():
    processor = Mock()
    processor.process.return_value = {"action": "inspect"}
    interpreter = Mock()
    interpreter.interpret_player_input.return_value = {"action": "inspect"}
    return GameActionService(processor, interpreter), processor, interpreter


def _execute(service, player_input):
    return service.execute(
        player_input,
        state_manager="state-manager",
        room="room-7",
        participant_id=17,
        adventure=31,
        world={"name": "Test World"},
    )


def test_structured_command_bypasses_natural_language_interpreter(action_service):
    service, _, interpreter = action_service

    _execute(service, {"command": {"action": "inspect"}})

    interpreter.interpret_player_input.assert_not_called()


def test_structured_command_reaches_processor_with_game_context(action_service):
    service, processor, _ = action_service
    command = {"action": "move", "target": "forest"}

    result = _execute(service, {"command": command})

    assert result == {"action": "inspect"}
    processor.process.assert_called_once_with(
        command,
        room="room-7",
        participant_id=17,
        adventure=31,
        world={"name": "Test World"},
        player_message=None,
    )


def test_natural_language_is_interpreted_with_game_context(action_service):
    service, _, interpreter = action_service

    _execute(service, {"message": "Rozglądam się"})

    interpreter.interpret_player_input.assert_called_once_with(
        {"input": "Rozglądam się"},
        state_manager="state-manager",
        room="room-7",
        participant_id=17,
    )


def test_interpreted_action_reaches_processor(action_service):
    service, processor, interpreter = action_service
    interpreted = {"action": "attack", "target": "wolf"}
    interpreter.interpret_player_input.return_value = interpreted

    _execute(service, {"message": "Atakuję wilka"})

    assert processor.process.call_args.args[0] is interpreted


def test_none_interpretation_does_not_run_processor(action_service):
    service, processor, interpreter = action_service
    interpreter.interpret_player_input.return_value = None

    assert _execute(service, {"message": "Czekam"}) is NO_ACTION
    processor.process.assert_not_called()


def test_non_dict_interpretation_does_not_run_processor(action_service):
    service, processor, interpreter = action_service
    interpreter.interpret_player_input.return_value = "inspect"

    assert _execute(service, {"message": "Patrzę"}) is NO_ACTION
    processor.process.assert_not_called()


def test_interpretation_without_action_does_not_run_processor(action_service):
    service, processor, interpreter = action_service
    interpreter.interpret_player_input.return_value = {"target": "door"}

    assert _execute(service, {"message": "Sprawdzam drzwi"}) is NO_ACTION
    processor.process.assert_not_called()


def test_structured_command_has_no_player_message(action_service):
    service, processor, _ = action_service

    _execute(service, {"command": {"action": "inspect"}})

    assert processor.process.call_args.kwargs["player_message"] is None


def test_natural_language_preserves_player_message(action_service):
    service, processor, _ = action_service

    _execute(service, {"message": "Nasłuchuję odgłosów"})

    assert (
        processor.process.call_args.kwargs["player_message"]
        == "Nasłuchuję odgłosów"
    )
