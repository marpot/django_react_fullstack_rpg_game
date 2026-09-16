import json
from unittest.mock import Mock, patch

import pytest
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import PlayerCharacter
from chat.models import Room, RoomParticipant
from game.middleware.state_middleware import STATE_MANAGER
from game.npc.npc_models import NPC
from game_instances.services.llm.orchestrator.ai_game_master import AIGameMaster
from game_instances.services.llm.orchestrator.llm_service import LLMService
from game_instances.services.llm.core.llm_client import LLMClient
from rpg_project.asgi import application
from world.models import Adventure


pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def two_joined_players():
    user_model = get_user_model()
    # Distinct ID ranges catch accidental use of User or Character IDs as turns.
    for index in range(2):
        user_model.objects.create_user(
            username=f"identity-padding-{index}", password="x"
        )
    user_a = user_model.objects.create_user(username="sync-a", password="x")
    user_b = user_model.objects.create_user(username="sync-b", password="x")
    for index in range(3):
        PlayerCharacter.objects.create(
            user=user_a, name=f"Inactive {index}", is_active=False
        )
    character_a = PlayerCharacter.objects.create(user=user_a, name="Character A")
    character_b = PlayerCharacter.objects.create(user=user_b, name="Character B")
    adventure = Adventure.objects.create(
        title="Sync adventure", description="Two player adventure", creator=user_a
    )
    room = Room.objects.create(name="sync-room", owner=user_a, adventure=adventure)

    clients = []
    participants = []
    for user, character in ((user_a, character_a), (user_b, character_b)):
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(f"/api/chat/rooms/{room.id}/join/", {}, format="json")
        assert response.status_code == 200, response.data
        assert response.data["character_id"] == character.id
        clients.append(client)
        participants.append(response.data["participant_id"])

    assert participants[0] != participants[1]
    assert RoomParticipant.objects.filter(room=room).count() == 2
    assert set(participants).isdisjoint({user_a.id, user_b.id})
    assert set(participants).isdisjoint({character_a.id, character_b.id})
    return room, (user_a, user_b), clients, participants


def _socket(room, user):
    token = str(RefreshToken.for_user(user).access_token)
    return WebsocketCommunicator(application, f"/ws/game/{room.id}/?token={token}")


async def _receive_pair(socket_a, socket_b, event):
    from_a = await socket_a.receive_json_from(timeout=2)
    from_b = await socket_b.receive_json_from(timeout=2)
    assert from_a["type"] == from_b["type"] == "game_event"
    assert from_a["event"] == from_b["event"] == event
    assert from_a["payload"] == from_b["payload"]
    return from_a["payload"]


@pytest.mark.asyncio
async def test_two_players_share_rest_websocket_turns_and_reconnect(two_joined_players):
    room, (user_a, user_b), (client_a, _), (participant_a, participant_b) = (
        two_joined_players
    )
    STATE_MANAGER.rooms.clear()
    socket_a = _socket(room, user_a)
    socket_b = _socket(room, user_b)
    sockets = [socket_a, socket_b]

    with (
        patch.object(LLMService, "generate_world", return_value={
            "name": "Shared World", "description": "One shared runtime world."
        }) as generate_world,
        patch.object(LLMService, "generate_intro", return_value={
            "text": "Shared intro"
        }) as generate_intro,
        patch.object(AIGameMaster, "interpret_player_input", return_value={
            "action": "inspect"
        }),
        patch.object(AIGameMaster, "narrate_event", return_value={
            "text": "Inspection complete"
        }),
    ):
        try:
            assert (await socket_a.connect())[0]
            assert (await socket_b.connect())[0]
            # connect() returns after accept, before on_connect() finishes its DB work.
            assert await socket_a.receive_nothing(timeout=0.2)
            assert await socket_b.receive_nothing(timeout=0.2)

            start = await sync_to_async(client_a.post)(
                f"/api/chat/rooms/{room.id}/start_game/"
            )
            assert start.status_code == 200, start.data
            assert start.data["state"] == "in_game"
            started = await _receive_pair(socket_a, socket_b, "game_started")
            assert started["world"]["name"] == "Shared World"
            assert started["game_state"]["players"].keys() == {
                str(participant_a), str(participant_b)
            }
            assert started["turn_state"]["turn_order"] == [
                participant_a, participant_b
            ]
            assert started["turn_state"]["current_player_id"] == participant_a
            assert started["turn_state"]["turn_order"].count(
                started["turn_state"]["current_player_id"]
            ) == 1

            # B cannot take A's turn, even if the client supplies A's ID.
            await socket_b.send_json_to({"message": "look", "participant_id": participant_a})
            rejected = await _receive_pair(socket_a, socket_b, "action_result")
            assert rejected["data"]["result"]["error"] == "not_your_turn"
            assert rejected["data"]["result"]["turn_state"]["current_player_id"] == participant_a
            assert STATE_MANAGER.get_room(room.id).current_player_id == participant_a

            await socket_a.send_json_to({"message": "look"})
            action_a = await _receive_pair(socket_a, socket_b, "action_result")
            assert action_a["data"]["action"] == "inspect"
            assert action_a["data"]["result"]["room"] == str(room.id)
            assert action_a["turn_state"]["current_player_id"] == participant_b
            assert action_a["turn_state"]["turn_order"] == [participant_a, participant_b]

            room_state = STATE_MANAGER.get_room(room.id)
            world = room_state.world
            history = {pid: list(events) for pid, events in room_state.player_histories.items()}
            repeated_start = await sync_to_async(client_a.post)(
                f"/api/chat/rooms/{room.id}/start_game/"
            )
            assert repeated_start.status_code == 200, repeated_start.data
            assert STATE_MANAGER.get_room(room.id) is room_state
            assert room_state.world is world
            assert room_state.current_player_id == participant_b
            assert room_state.turn_order == [participant_a, participant_b]
            assert room_state.player_histories == history
            assert await socket_a.receive_nothing(timeout=0.1)
            assert await socket_b.receive_nothing(timeout=0.1)

            await socket_b.send_json_to({"message": "look"})
            action_b = await _receive_pair(socket_a, socket_b, "action_result")
            assert action_b["data"]["action"] == "inspect"
            assert action_b["turn_state"]["current_player_id"] == participant_a
            assert action_b["turn_state"]["turn_order"] == [participant_a, participant_b]

            history = {pid: list(events) for pid, events in room_state.player_histories.items()}
            assert len(history[participant_a]) == len(history[participant_b]) == 1
            await socket_b.disconnect()
            sockets.remove(socket_b)
            reconnected_b = _socket(room, user_b)
            sockets.append(reconnected_b)
            assert (await reconnected_b.connect())[0]
            snapshot = await reconnected_b.receive_json_from(timeout=2)
            assert snapshot["event"] == "game_started"
            assert snapshot["payload"]["reconnect"] is True
            assert snapshot["payload"]["world"] == started["world"]
            assert snapshot["payload"]["turn_state"]["turn_order"] == [
                participant_a, participant_b
            ]
            assert snapshot["payload"]["turn_state"]["current_player_id"] == participant_a
            assert snapshot["payload"]["turn_state"]["is_your_turn"] is False
            assert snapshot["payload"]["game_state"]["player_histories"] == {
                str(pid): events for pid, events in history.items()
            }
            assert STATE_MANAGER.get_room(room.id) is room_state
            assert room_state.world is world
            assert generate_world.call_count == generate_intro.call_count == 1
            assert await socket_a.receive_nothing(timeout=0.1)
        finally:
            for socket in sockets:
                await socket.disconnect()
            STATE_MANAGER.rooms.clear()


@pytest.mark.asyncio
async def test_structured_choice_bypasses_parser_and_preserves_server_identity(two_joined_players):
    room, (user_a, user_b), (client_a, _), (participant_a, participant_b) = (
        two_joined_players
    )
    STATE_MANAGER.rooms.clear()
    socket_a = _socket(room, user_a)
    socket_b = _socket(room, user_b)

    with (
        patch.object(LLMService, "generate_world", return_value={"name": "World"}),
        patch.object(LLMService, "generate_intro", return_value={"text": "Intro"}),
        patch.object(AIGameMaster, "interpret_player_input", return_value={
            "action": "inspect"
        }) as parse_input,
        patch.object(LLMClient, "generate_intent", side_effect=AssertionError(
            "structured choice must not call provider"
        )) as generate_intent,
        patch.object(AIGameMaster, "narrate_event", return_value={
            "text": "Inspection complete"
        }),
        patch.object(AIGameMaster, "dialogue_with_npc", return_value="Witaj, wędrowcze.") as dialogue,
    ):
        try:
            assert (await socket_a.connect())[0]
            assert (await socket_b.connect())[0]
            assert await socket_a.receive_nothing(timeout=0.2)
            assert await socket_b.receive_nothing(timeout=0.2)

            start = await sync_to_async(client_a.post)(
                f"/api/chat/rooms/{room.id}/start_game/"
            )
            assert start.status_code == 200, start.data
            await _receive_pair(socket_a, socket_b, "game_started")

            # Client-supplied identity cannot take another participant's turn.
            await socket_b.send_json_to({
                "type": "player_action",
                "command": {"action": "inspect", "participant_id": participant_a},
            })
            blocked = await _receive_pair(socket_a, socket_b, "action_result")
            assert blocked["data"]["result"]["error"] == "not_your_turn"
            assert STATE_MANAGER.get_room(room.id).current_player_id == participant_a
            parse_input.assert_not_called()
            generate_intent.assert_not_called()

            await socket_a.send_json_to({
                "type": "player_action",
                "command": {
                    "action": "inspect", "target": None, "method": None,
                    "participant_id": participant_b, "room": "other-room",
                    "hp": 999, "damage": 999, "result": {"winner": "client"},
                },
            })
            chosen = await _receive_pair(socket_a, socket_b, "action_result")
            assert chosen["data"]["action"] == "inspect"
            assert chosen["data"]["result"]["room"] == str(room.id)
            assert "hp" not in chosen["data"]["result"]
            assert "damage" not in chosen["data"]["result"]
            assert chosen["turn_state"]["current_player_id"] == participant_b
            assert STATE_MANAGER.get_room(room.id).player_histories[participant_a][-1]["action"] == "inspect"
            parse_input.assert_not_called()
            generate_intent.assert_not_called()

            await socket_b.send_json_to({
                "type": "player_action",
                "command": {"action": "teleport", "participant_id": participant_a},
            })
            rejected = await _receive_pair(socket_a, socket_b, "action_result")
            assert rejected["data"]["result"]["error"] == "invalid_action"
            assert STATE_MANAGER.get_room(room.id).current_player_id == participant_b
            parse_input.assert_not_called()
            generate_intent.assert_not_called()

            await socket_b.send_json_to({"type": "player_action", "message": "look around"})
            typed = await _receive_pair(socket_a, socket_b, "action_result")
            assert typed["data"]["action"] == "inspect"
            assert typed["turn_state"]["current_player_id"] == participant_a
            parse_input.assert_called_once()
            assert parse_input.call_args.args[0]["input"] == "look around"

            STATE_MANAGER.get_room(room.id).npcs["guide"] = NPC(id="guide", name="Guide")
            await socket_a.send_json_to({
                "type": "player_action",
                "command": {"action": "talk", "target": "guide", "method": None},
            })
            spoken = await _receive_pair(socket_a, socket_b, "action_result")
            assert spoken["data"]["action"] == "talk"
            assert spoken["data"]["text"] == "Witaj, wędrowcze."
            dialogue.assert_called_once()
            assert parse_input.call_count == 1
            generate_intent.assert_not_called()
        finally:
            await socket_a.disconnect()
            await socket_b.disconnect()
            STATE_MANAGER.rooms.clear()


@pytest.mark.asyncio
async def test_natural_free_text_uses_fake_intent_provider_and_shared_result(two_joined_players):
    room, (user_a, user_b), (client_a, _), (participant_a, participant_b) = (
        two_joined_players
    )
    STATE_MANAGER.rooms.clear()
    socket_a = _socket(room, user_a)
    socket_b = _socket(room, user_b)
    provider = Mock()
    provider.complete.return_value = '{"action":"inspect","target":null,"method":null}'

    with (
        patch("game_instances.services.llm.core.llm_client.GroqProvider", return_value=provider),
        patch.object(LLMService, "generate_world", return_value={"name": "World"}),
        patch.object(LLMService, "generate_intro", return_value={"text": "Intro"}),
        patch.object(AIGameMaster, "narrate_event", return_value={
            "text": "Inspection complete"
        }),
    ):
        try:
            assert (await socket_a.connect())[0]
            assert (await socket_b.connect())[0]
            assert await socket_a.receive_nothing(timeout=0.2)
            assert await socket_b.receive_nothing(timeout=0.2)

            start = await sync_to_async(client_a.post)(
                f"/api/chat/rooms/{room.id}/start_game/"
            )
            assert start.status_code == 200, start.data
            await _receive_pair(socket_a, socket_b, "game_started")

            await socket_a.send_json_to({
                "type": "player_action", "message": "Przyglądam się śladom",
            })
            action = await _receive_pair(socket_a, socket_b, "action_result")

            assert action["data"]["action"] == "inspect"
            assert action["data"]["result"]["room"] == str(room.id)
            assert action["turn_state"]["current_player_id"] == participant_b
            assert STATE_MANAGER.get_room(room.id).player_histories[participant_a][-1]["action"] == "inspect"
            provider.complete.assert_called_once()
            prompt = json.loads(provider.complete.call_args.args[1])
            assert prompt["message"] == "Przyglądam się śladom"
            assert prompt["game_context"]["current_player"] == "Character A"
            assert prompt["game_context"]["current_location"] == "start"
            assert "hp" not in provider.complete.call_args.args[1]
        finally:
            await socket_a.disconnect()
            await socket_b.disconnect()
            STATE_MANAGER.rooms.clear()


@pytest.mark.asyncio
async def test_in_game_db_without_runtime_reports_unavailable(two_joined_players):
    room, (user_a, user_b), (client_a, _), _ = two_joined_players
    STATE_MANAGER.rooms.clear()
    await Room.objects.filter(pk=room.pk).aupdate(state="in_game")
    socket_b = _socket(room, user_b)

    try:
        assert (await socket_b.connect())[0]
        event = await socket_b.receive_json_from(timeout=2)
        assert event["type"] == "game_event"
        assert event["event"] == "error"
        assert event["payload"]["reason"] == "game_state_unavailable"
        assert STATE_MANAGER.get_room(room.id) is None

        response = await sync_to_async(client_a.post)(
            f"/api/chat/rooms/{room.id}/start_game/"
        )
        assert response.status_code == 409
        assert response.data["code"] == "GAME_STATE_UNAVAILABLE"
        assert STATE_MANAGER.get_room(room.id) is None
        assert await Room.objects.filter(pk=room.pk, state="in_game").aexists()
    finally:
        await socket_b.disconnect()
        STATE_MANAGER.rooms.clear()
