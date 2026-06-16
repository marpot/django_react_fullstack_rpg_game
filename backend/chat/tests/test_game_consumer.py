import pytest
from channels.testing import WebsocketCommunicator
from rpg_project.asgi import application


@pytest.mark.asyncio
class GameConsumerTests:

    async def test_move_action(self):
        communicator = WebsocketCommunicator(
            application,
            "/ws/game/lobby/?token=VALID_TOKEN"
        )

        connected, _ = await communicator.connect()
        assert connected

        await communicator.send_json_to({
            "action": "move",
            "sender": "Player1"
        })

        response = await communicator.receive_json_from()

        assert "porusza się" in response.get("message", "")

        await communicator.disconnect()

    async def test_init_sets_character_id(self):
        communicator = WebsocketCommunicator(
            application,
            "/ws/game/lobby/?token=VALID_TOKEN"
        )

        connected, _ = await communicator.connect()
        assert connected

        await communicator.send_json_to({
            "type": "init",
            "character_id": 5
        })

        await communicator.send_json_to({
            "message": "look around"
        })

        response = await communicator.receive_json_from()

        assert response.get("type") is not None

        await communicator.disconnect()

    async def test_missing_character_id_causes_error(self):
        communicator = WebsocketCommunicator(
            application,
            "/ws/game/lobby/?token=VALID_TOKEN"
        )

        connected, _ = await communicator.connect()
        assert connected

        await communicator.send_json_to({
            "message": "look around"
        })

        response = await communicator.receive_json_from()

        assert response.get("type") == "game_event"

        await communicator.disconnect()