from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, call

import pytest

from game.services.bot_turn_service import BotTurnService


def _room(*, current_player_id=7, ai_participants=None):
    return SimpleNamespace(
        turn_order=[7, 8],
        current_player_id=current_player_id,
        ai_participants={7} if ai_participants is None else ai_participants,
        adventure_completed=False,
        quest=SimpleNamespace(completed=False),
    )


def _service(room):
    state_manager = Mock()
    state_manager.get_room.return_value = room
    state_manager.start_lock = MagicMock()
    bot_player_service = Mock()
    processor = Mock()
    return (
        BotTurnService(state_manager, bot_player_service, processor),
        state_manager,
        bot_player_service,
        processor,
    )


def _execute(service):
    return service.execute(
        "room-7",
        adventure=31,
        world={"name": "Test World"},
    )


def test_missing_room_returns_no_results():
    service, state_manager, bot_player_service, processor = _service(None)

    assert _execute(service) == []
    state_manager.get_room.assert_called_once_with("room-7")
    state_manager.start_lock.__enter__.assert_not_called()
    bot_player_service.choose_command.assert_not_called()
    processor.process.assert_not_called()


def test_ai_turn_uses_services_and_returns_actor_metadata():
    room = _room()
    service, state_manager, bot_player_service, processor = _service(room)
    command = {"action": "inspect"}
    bot_player_service.choose_command.return_value = command

    def process(*args, **kwargs):
        room.current_player_id = 8
        return {"action": "inspect"}

    processor.process.side_effect = process

    results = _execute(service)

    state_manager.start_lock.__enter__.assert_called_once_with()
    bot_player_service.choose_command.assert_called_once_with(room, 7)
    processor.process.assert_called_once_with(
        command,
        room="room-7",
        participant_id=7,
        adventure=31,
        world={"name": "Test World"},
    )
    assert results == [{"action": "inspect", "_actor_id": 7}]
    assert room.current_player_id == 8


@pytest.mark.parametrize(
    ("adventure_completed", "quest_completed"),
    [(True, False), (False, True)],
)
def test_completed_game_stops_before_bot_action(
    adventure_completed,
    quest_completed,
):
    room = _room()
    room.adventure_completed = adventure_completed
    room.quest.completed = quest_completed
    service, _, bot_player_service, processor = _service(room)

    assert _execute(service) == []
    bot_player_service.choose_command.assert_not_called()
    processor.process.assert_not_called()


def test_current_human_participant_stops_before_bot_action():
    room = _room(current_player_id=8)
    service, _, bot_player_service, processor = _service(room)

    assert _execute(service) == []
    bot_player_service.choose_command.assert_not_called()
    processor.process.assert_not_called()


def test_consecutive_ai_turns_are_bounded_by_turn_order():
    room = _room(ai_participants={7, 8})
    service, _, bot_player_service, processor = _service(room)
    commands = [{"action": "inspect"}, {"action": "move"}]
    bot_player_service.choose_command.side_effect = commands

    def process(*args, **kwargs):
        room.current_player_id = 8 if room.current_player_id == 7 else 7
        return {"action": args[0]["action"]}

    processor.process.side_effect = process

    results = _execute(service)

    assert bot_player_service.choose_command.call_args_list == [
        call(room, 7),
        call(room, 8),
    ]
    assert processor.process.call_count == len(room.turn_order)
    assert [result["_actor_id"] for result in results] == [7, 8]
