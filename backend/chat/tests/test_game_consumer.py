import json
from unittest.mock import AsyncMock, Mock

import pytest

from chat.consumers_modules.game_consumer import GameConsumer
from game.services.game_action_service import GameActionService


def _consumer(*, participant_id=17, character_id=23):
    consumer = object.__new__(GameConsumer)
    consumer.participant_id = participant_id
    consumer.character_id = character_id
    consumer.room_name = "characterization-room"
    consumer.adventure_id = 31
    consumer.world = {"name": "Characterization World"}
    consumer.state_manager = Mock()
    consumer.ai_game_master = Mock()
    consumer.processor = Mock()
    consumer.game_action_service = GameActionService(
        consumer.processor,
        consumer.ai_game_master,
    )
    consumer._send_game_event = AsyncMock()
    return consumer


@pytest.mark.asyncio
async def test_init_does_not_overwrite_database_character_id():
    consumer = _consumer(character_id=23)

    await consumer.receive(json.dumps({
        "type": "init",
        "character_id": 999,
    }))

    assert consumer.character_id == 23
    consumer.ai_game_master.interpret_player_input.assert_not_called()
    consumer.processor.process.assert_not_called()
    consumer._send_game_event.assert_not_awaited()


@pytest.mark.asyncio
async def test_action_without_resolved_participant_returns_no_participant_error():
    consumer = _consumer(participant_id=None)

    await consumer.receive(json.dumps({
        "command": {"action": "inspect"},
    }))

    consumer._send_game_event.assert_awaited_once_with(
        "error",
        {
            "reason": "no_participant",
            "details": "Nie jesteś uczestnikiem tego pokoju.",
        },
        text="Nie jesteś uczestnikiem tego pokoju.",
    )
    consumer.ai_game_master.interpret_player_input.assert_not_called()
    consumer.processor.process.assert_not_called()


@pytest.mark.asyncio
async def test_action_without_valid_character_returns_no_character_error():
    consumer = _consumer(character_id=None)

    await consumer.receive(json.dumps({
        "command": {"action": "inspect"},
    }))

    consumer._send_game_event.assert_awaited_once_with(
        "error",
        {
            "reason": "no_character",
            "details": "Wybierz postać przed rozpoczęciem rozgrywki.",
        },
        text="Wybierz postać przed rozpoczęciem rozgrywki.",
    )
    consumer.ai_game_master.interpret_player_input.assert_not_called()
    consumer.processor.process.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("message", ["", " \t\n"], ids=["empty", "whitespace"])
async def test_blank_message_without_command_is_ignored(message):
    consumer = _consumer()

    await consumer.receive(json.dumps({"message": message}))

    consumer.ai_game_master.interpret_player_input.assert_not_called()
    consumer.processor.process.assert_not_called()
    consumer._send_game_event.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "parsed",
    [None, "inspect", {}, {"target": "door"}],
    ids=["none", "not-a-dict", "empty-dict", "missing-action"],
)
async def test_natural_language_without_parsed_action_does_not_run_processor(parsed):
    consumer = _consumer()
    consumer.ai_game_master.interpret_player_input.return_value = parsed

    await consumer.receive(json.dumps({"message": "Sprawdzam drzwi"}))

    consumer.ai_game_master.interpret_player_input.assert_called_once_with(
        {"input": "Sprawdzam drzwi"},
        state_manager=consumer.state_manager,
        room=consumer.room_name,
        participant_id=consumer.participant_id,
    )
    consumer.processor.process.assert_not_called()
    consumer._send_game_event.assert_not_awaited()
